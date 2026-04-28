import logging
from datetime import UTC, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo
from uuid import UUID

from fastapi import HTTPException

from app.core.config import settings
from app.modules.assignments.models import AssignmentStatus
from app.modules.incidents.models import IncidentServiceReport, IncidentStatus
from app.modules.realtime.services import PushNotificationService
from app.modules.user.models import UserRole
from app.modules.wallet.models import Transactions, TransactionStatus, TransactionType

from .base_service import AssignmentBaseService

logger = logging.getLogger(__name__)


class MechanicAssignmentService(AssignmentBaseService):
    _ACTIVE_INCIDENT_STATUSES = (
        IncidentStatus.ASSIGNED,
        IncidentStatus.ON_THE_WAY,
        IncidentStatus.ARRIVED,
    )

    _STATUS_FLOW: dict[IncidentStatus, tuple[IncidentStatus, ...]] = {
        IncidentStatus.ASSIGNED: (IncidentStatus.ON_THE_WAY, IncidentStatus.CANCELLED),
        IncidentStatus.ON_THE_WAY: (IncidentStatus.ARRIVED, IncidentStatus.CANCELLED),
        IncidentStatus.ARRIVED: (IncidentStatus.COMPLETED, IncidentStatus.CANCELLED),
    }

    def get_my_active_assignment(self, *, user_id: UUID) -> dict:
        mechanic_link = self._resolve_mechanic_link(user_id)
        assignment = self.request_assignment.get_latest_active_by_mechanic(mechanic_link.id)
        if not assignment:
            return {"assignment": None}

        return {
            "assignment": self._build_assignment_read(assignment),
        }

    def get_my_assignment_detail(self, *, user_id: UUID, assignment_id: UUID) -> dict:
        mechanic_link = self._resolve_mechanic_link(user_id)
        assignment = self.request_assignment.get_by_id_and_mechanic(
            assignment_id=assignment_id,
            mechanic_id=mechanic_link.id,
        )
        if not assignment:
            raise HTTPException(status_code=404, detail="Asignacion no encontrada")

        return self._build_assignment_read(assignment)

    def get_my_today_stats(self, *, user_id: UUID) -> dict:
        mechanic_link = self._resolve_mechanic_link(user_id)

        start_utc, end_utc = self._today_utc_window()
        return self.request_assignment.get_today_status_totals_for_mechanic(
            mechanic_id=mechanic_link.id,
            start_utc=start_utc,
            end_utc=end_utc,
        )

    def list_my_completed_services(self, *, user_id: UUID) -> dict:
        mechanic_link = self._resolve_mechanic_link(user_id)
        services = self.request_assignment.list_services_by_mechanic(
            mechanic_id=mechanic_link.id,
            only_completed=True,
        )
        return {"services": services}

    def list_my_service_history(self, *, user_id: UUID) -> dict:
        mechanic_link = self._resolve_mechanic_link(user_id)
        services = self.request_assignment.list_services_by_mechanic(
            mechanic_id=mechanic_link.id,
            only_completed=False,
        )
        return {"services": services}

    def get_my_incident_detail(self, *, user_id: UUID, incident_id: UUID) -> dict:
        mechanic_link = self._resolve_mechanic_link(user_id)
        assignment = self.request_assignment.get_latest_by_incident_and_mechanic(
            incident_id=incident_id,
            mechanic_id=mechanic_link.id,
        )
        if not assignment:
            raise HTTPException(status_code=404, detail="Servicio no encontrado")

        return self._build_assignment_read(assignment)

    def update_my_assignment_status(
        self,
        *,
        user_id: UUID,
        assignment_id: UUID,
        target_status: str,
    ) -> dict:
        mechanic_link = self._resolve_mechanic_link(user_id)
        assignment = self.request_assignment.get_by_id_and_mechanic(
            assignment_id=assignment_id,
            mechanic_id=mechanic_link.id,
        )
        if not assignment:
            raise HTTPException(status_code=404, detail="Asignacion no encontrada")
        if assignment.status != AssignmentStatus.ACCEPTED:
            raise HTTPException(status_code=409, detail="La asignacion ya no esta activa")

        incident = self.incident.get_by_id(assignment.incident_id)
        if not incident:
            raise HTTPException(status_code=404, detail="Incidente no encontrado")

        next_status = self._parse_incident_status(target_status)
        if next_status == IncidentStatus.COMPLETED:
            raise HTTPException(
                status_code=400,
                detail="Para finalizar el servicio debes enviar reporte en el endpoint /complete",
            )
        self._ensure_valid_incident_transition(current=incident.status, target=next_status)

        incident.status = next_status
        self.db.add(incident)

        if next_status in (IncidentStatus.COMPLETED, IncidentStatus.CANCELLED):
            assignment.status = (
                AssignmentStatus.COMPLETED
                if next_status == IncidentStatus.COMPLETED
                else AssignmentStatus.CANCELLED
            )
            assignment.responded_at = datetime.now(UTC)
            self.db.add(assignment)

            mechanic_link.is_available = True
            self.db.add(mechanic_link)

        self.db.commit()

        detail = self._status_detail(next_status)
        self._emit_incident_realtime_event(
            incident_id=incident.id,
            event_type="mechanic.status.updated",
            payload={
                "assignment_id": assignment.id,
                "mechanic_id": mechanic_link.id,
                "status": next_status.value,
                "description": detail,
            },
            status=next_status,
            assignment_id=assignment.id,
            repair_shop_id=assignment.repair_shop_id,
            mechanic_id=mechanic_link.id,
        )
        self._emit_incident_realtime_event(
            incident_id=incident.id,
            event_type="incident.status.changed",
            payload={
                "status": next_status.value,
                "assignment_id": assignment.id,
                "mechanic_id": mechanic_link.id,
                "description": detail,
            },
            status=next_status,
            assignment_id=assignment.id,
            repair_shop_id=assignment.repair_shop_id,
            mechanic_id=mechanic_link.id,
        )

        if next_status in (
            IncidentStatus.ON_THE_WAY,
            IncidentStatus.ARRIVED,
        ):
            self._send_client_status_push(
                client_user_id=incident.user_id,
                incident_id=incident.id,
                assignment_id=assignment.id,
                status=next_status.value,
            )

        return {
            "assignment_id": assignment.id,
            "incident_id": incident.id,
            "incident_status": incident.status.value,
            "assignment_status": assignment.status.value,
            "detail": detail,
        }

    def _send_client_status_push(
        self,
        *,
        client_user_id: UUID,
        incident_id: UUID,
        assignment_id: UUID,
        status: str,
    ) -> None:
        try:
            PushNotificationService(self.db).notify_client_incident_status_changed(
                client_user_id=client_user_id,
                incident_id=incident_id,
                assignment_id=assignment_id,
                status=status,
            )
        except Exception as error:
            logger.warning(
                "No se pudo enviar push al cliente user_id=%s incident_id=%s status=%s error=%s",
                client_user_id,
                incident_id,
                status,
                error,
            )

    def update_my_assignment_location(
        self,
        *,
        user_id: UUID,
        assignment_id: UUID,
        latitude: float,
        longitude: float,
        recorded_at: datetime | None,
    ) -> dict:
        mechanic_link = self._resolve_mechanic_link(user_id)
        assignment = self.request_assignment.get_by_id_and_mechanic(
            assignment_id=assignment_id,
            mechanic_id=mechanic_link.id,
        )
        if not assignment:
            raise HTTPException(status_code=404, detail="Asignacion no encontrada")
        if assignment.status != AssignmentStatus.ACCEPTED:
            raise HTTPException(status_code=409, detail="La asignacion ya no esta activa")

        incident = self.incident.get_by_id(assignment.incident_id)
        if not incident:
            raise HTTPException(status_code=404, detail="Incidente no encontrado")
        if incident.status not in self._ACTIVE_INCIDENT_STATUSES:
            raise HTTPException(status_code=409, detail="El incidente no acepta ubicacion en este estado")

        location_time = recorded_at or datetime.now(UTC)
        self._emit_incident_realtime_event(
            incident_id=incident.id,
            event_type="mechanic.location.updated",
            payload={
                "assignment_id": assignment.id,
                "mechanic_id": mechanic_link.id,
                "status": incident.status.value,
                "mechanic_latitude": latitude,
                "mechanic_longitude": longitude,
                "mechanic_location_updated_at": location_time,
            },
            status=incident.status,
            assignment_id=assignment.id,
            repair_shop_id=assignment.repair_shop_id,
            mechanic_id=mechanic_link.id,
            mechanic_latitude=latitude,
            mechanic_longitude=longitude,
            mechanic_location_updated_at=location_time,
        )

        return {
            "assignment_id": assignment.id,
            "incident_id": incident.id,
            "incident_status": incident.status.value,
            "assignment_status": assignment.status.value,
            "detail": "Ubicacion de mecanico actualizada",
        }

    def complete_my_assignment(
        self,
        *,
        user_id: UUID,
        assignment_id: UUID,
        description: str,
        labor_price: float,
    ) -> dict:
        mechanic_link = self._resolve_mechanic_link(user_id)
        assignment = self.request_assignment.get_by_id_and_mechanic(
            assignment_id=assignment_id,
            mechanic_id=mechanic_link.id,
        )
        if not assignment:
            raise HTTPException(status_code=404, detail="Asignacion no encontrada")
        if assignment.status != AssignmentStatus.ACCEPTED:
            raise HTTPException(status_code=409, detail="La asignacion ya no esta activa")

        incident = self.incident.get_by_id(assignment.incident_id)
        if not incident:
            raise HTTPException(status_code=404, detail="Incidente no encontrado")
        if incident.status != IncidentStatus.ARRIVED:
            raise HTTPException(
                status_code=409,
                detail="Solo se puede completar un incidente cuando ya fue marcado como llegado",
            )

        normalized_description = " ".join((description or "").split())
        if len(normalized_description) < 8:
            raise HTTPException(
                status_code=400,
                detail="Debes registrar una descripcion valida del trabajo realizado",
            )

        labor_price_decimal = Decimal(str(labor_price)).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
        if labor_price_decimal < Decimal("0.00"):
            raise HTTPException(
                status_code=400,
                detail="El monto cobrado no puede ser negativo",
            )

        existing_report = self.incident_service_report.get_by_incident_id(incident.id)
        if existing_report:
            raise HTTPException(
                status_code=409,
                detail="El incidente ya tiene un reporte final registrado",
            )

        report = IncidentServiceReport(
            incident_id=incident.id,
            description=normalized_description,
            labor_price=labor_price_decimal,
        )
        self.incident_service_report.create(report)

        incident.status = IncidentStatus.COMPLETED
        self.db.add(incident)

        assignment.status = AssignmentStatus.COMPLETED
        assignment.responded_at = datetime.now(UTC)
        self.db.add(assignment)

        mechanic_link.is_available = True
        self.db.add(mechanic_link)

        wallet_debit_amount = self._resolve_delivery_charge(incident, assignment)
        wallet_snapshot = self._debit_wallet_for_completed_service(
            assignment_id=assignment.id,
            repair_shop_id=assignment.repair_shop_id,
            debit_amount=wallet_debit_amount,
        )

        self.db.commit()
        self.db.refresh(report)

        detail = self._status_detail(IncidentStatus.COMPLETED)
        self._emit_incident_realtime_event(
            incident_id=incident.id,
            event_type="mechanic.status.updated",
            payload={
                "assignment_id": assignment.id,
                "mechanic_id": mechanic_link.id,
                "status": IncidentStatus.COMPLETED.value,
                "description": detail,
            },
            status=IncidentStatus.COMPLETED,
            assignment_id=assignment.id,
            repair_shop_id=assignment.repair_shop_id,
            mechanic_id=mechanic_link.id,
        )
        self._emit_incident_realtime_event(
            incident_id=incident.id,
            event_type="incident.status.changed",
            payload={
                "status": IncidentStatus.COMPLETED.value,
                "assignment_id": assignment.id,
                "mechanic_id": mechanic_link.id,
                "description": detail,
                "review_requested": True,
            },
            status=IncidentStatus.COMPLETED,
            assignment_id=assignment.id,
            repair_shop_id=assignment.repair_shop_id,
            mechanic_id=mechanic_link.id,
        )
        self._emit_incident_realtime_event(
            incident_id=incident.id,
            event_type="incident.report.created",
            payload={
                "report_id": report.id,
                "assignment_id": assignment.id,
                "mechanic_id": mechanic_link.id,
                "description": report.description,
                "labor_price": float(report.labor_price),
                "delivery_price": float(wallet_debit_amount),
                "wallet_balance_before": float(wallet_snapshot["balance_before"]),
                "wallet_balance_after": float(wallet_snapshot["balance_after"]),
            },
            status=IncidentStatus.COMPLETED,
            assignment_id=assignment.id,
            repair_shop_id=assignment.repair_shop_id,
            mechanic_id=mechanic_link.id,
        )

        self._send_client_status_push(
            client_user_id=incident.user_id,
            incident_id=incident.id,
            assignment_id=assignment.id,
            status=IncidentStatus.COMPLETED.value,
        )

        return {
            "assignment_id": assignment.id,
            "incident_id": incident.id,
            "incident_status": incident.status.value,
            "assignment_status": assignment.status.value,
            "detail": "Servicio completado y reporte final registrado",
        }

    def _resolve_mechanic_link(self, user_id: UUID):
        user = self._get_user_or_404(user_id)
        if user.role != UserRole.MECHANIC:
            raise HTTPException(status_code=403, detail="Solo mecanicos pueden operar asignaciones")

        mechanic_link = self.shop_mechanic.get_active_by_user_id(user.id)
        if not mechanic_link:
            raise HTTPException(status_code=404, detail="Mecanico no vinculado a un taller")
        return mechanic_link

    def _build_assignment_read(self, assignment) -> dict:
        incident = self.incident.get_by_id(assignment.incident_id)
        if not incident:
            raise HTTPException(status_code=404, detail="Incidente no encontrado")

        shop = self.repair_shop.get_by_id(assignment.repair_shop_id)
        payload = self.request_assignment.get_offer_notification_payload(assignment.id) or {}
        evidences = self.evidence.list_by_incident_id(incident.id)
        vehicle_with_type = self.vehicle.get_active_by_id_with_type(incident.vehicle_id)
        client_user = self.user.get_by_id(incident.user_id)

        vehicle_data = None
        if vehicle_with_type:
            vehicle, vehicle_type = vehicle_with_type
            vehicle_data = {
                "id": vehicle.id,
                "make": vehicle.make,
                "model": vehicle.model,
                "plate": vehicle.plate,
                "color": vehicle.color,
                "year": vehicle.year,
                "type_name": vehicle_type.name.value if vehicle_type else None,
            }

        return {
            "assignment_id": assignment.id,
            "assignment_status": assignment.status.value,
            "repair_shop_id": assignment.repair_shop_id,
            "repair_shop_name": shop.name if shop else None,
            "repair_shop_latitude": shop.latitude if shop else None,
            "repair_shop_longitude": shop.longitude if shop else None,
            "mechanic_id": assignment.mechanic_id,
            "assigned_at": assignment.created_date,
            "incident": {
                "id": incident.id,
                "status": incident.status.value,
                "description": incident.description,
                "address": incident.address,
                "latitude": incident.latitude,
                "longitude": incident.longitude,
                "problem_id": payload.get("problem_id"),
                "problem_name": payload.get("problem_name"),
                "distance_km": payload.get("distance_km"),
                "delivery_price": payload.get("delivery_price"),
                "client_email": client_user.email if client_user else None,
                "client_name": (
                    f"{client_user.first_name} {client_user.last_name}".strip()
                    if client_user
                    else None
                ),
                "evidence_urls": [evidence.url for evidence in evidences],
                "vehicle": vehicle_data,
            },
        }

    def _today_utc_window(self) -> tuple[datetime, datetime]:
        local_now = datetime.now(ZoneInfo(settings.TIME_ZONE))
        start_local = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_local = start_local + timedelta(days=1)

        start_utc = start_local.astimezone(UTC).replace(tzinfo=None)
        end_utc = end_local.astimezone(UTC).replace(tzinfo=None)
        return start_utc, end_utc

    def _parse_incident_status(self, raw_status: str) -> IncidentStatus:
        normalized = raw_status.strip().lower()
        try:
            return IncidentStatus(normalized)
        except ValueError:
            raise HTTPException(status_code=400, detail="Estado de incidente invalido")

    def _ensure_valid_incident_transition(
        self,
        *,
        current: IncidentStatus,
        target: IncidentStatus,
    ) -> None:
        allowed_targets = self._STATUS_FLOW.get(current, ())
        if target not in allowed_targets:
            raise HTTPException(
                status_code=409,
                detail=f"No se puede cambiar de {current.value} a {target.value}",
            )

    def _status_detail(self, status: IncidentStatus) -> str:
        if status == IncidentStatus.ON_THE_WAY:
            return "Mecanico en camino"
        if status == IncidentStatus.ARRIVED:
            return "Mecanico llego al incidente"
        if status == IncidentStatus.COMPLETED:
            return "Incidente completado por el mecanico"
        if status == IncidentStatus.CANCELLED:
            return "Incidente cancelado por el mecanico"
        return "Estado actualizado por el mecanico"

    def _resolve_delivery_charge(self, incident, assignment) -> Decimal:
        source_value = incident.delivery_price
        if source_value is None:
            source_value = assignment.delivery_price
        if source_value is None:
            return Decimal("0.00")

        return Decimal(str(source_value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _debit_wallet_for_completed_service(
        self,
        *,
        assignment_id: UUID,
        repair_shop_id: UUID,
        debit_amount: Decimal,
    ) -> dict:
        wallets_by_shop = self.wallet_lookup.map_active_wallets_by_shop_ids([repair_shop_id])
        wallet = wallets_by_shop.get(str(repair_shop_id))
        if not wallet:
            raise HTTPException(status_code=404, detail="No se encontro billetera activa del taller")

        balance_before = Decimal(str(wallet.balance)).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
        balance_after = (balance_before - debit_amount).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
        wallet.balance = balance_after
        wallet.modified_date = datetime.utcnow()
        self.db.add(wallet)

        transaction = Transactions(
            type=TransactionType.DEBIT_SERVICE,
            status=TransactionStatus.POSTED,
            amount=debit_amount,
            balance_before=balance_before,
            balance_after=balance_after,
            description=f"Debito por servicio completado assignment_id={assignment_id}",
            wallet_id=wallet.id,
        )
        self.db.add(transaction)

        return {
            "balance_before": balance_before,
            "balance_after": balance_after,
        }

    def _emit_incident_realtime_event(
        self,
        *,
        incident_id: UUID,
        event_type: str,
        payload: dict,
        status: str | None = None,
        assignment_id: UUID | None = None,
        repair_shop_id: UUID | None = None,
        mechanic_id: UUID | None = None,
        mechanic_latitude: float | None = None,
        mechanic_longitude: float | None = None,
        mechanic_location_updated_at: datetime | None = None,
    ) -> None:
        try:
            from app.modules.realtime.services.incident_realtime_service import (
                IncidentRealtimeService,
            )

            IncidentRealtimeService(self.db).publish_incident_event_sync(
                incident_id=incident_id,
                event_type=event_type,
                payload=payload,
                status=status,
                assignment_id=assignment_id,
                repair_shop_id=repair_shop_id,
                mechanic_id=mechanic_id,
                mechanic_latitude=mechanic_latitude,
                mechanic_longitude=mechanic_longitude,
                mechanic_location_updated_at=mechanic_location_updated_at,
            )
        except Exception as error:
            try:
                self.db.rollback()
            except Exception:
                pass
            logger.warning(
                "No se pudo emitir evento realtime incident_id=%s type=%s error=%s",
                incident_id,
                event_type,
                error,
            )
