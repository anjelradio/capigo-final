import logging
from datetime import UTC, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo
from uuid import UUID

from fastapi import HTTPException

from app.core.config import settings
from app.modules.assignments.models import AssignmentStatus
from app.modules.incidents.models import IncidentServiceReport, IncidentStatus
from app.modules.incidents.services.incident_state_transition_service import (
    IncidentStateTransitionService,
)
from app.modules.incidents.services.incident_workflow_service import IncidentWorkflowService
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
                detail="Para finalizar el trabajo debes enviar reporte en el endpoint /submit-final-report",
            )
        IncidentStateTransitionService.ensure_mechanic_can_transition(
            current=incident.status,
            target=next_status,
        )

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
        IncidentWorkflowService(self.db).mechanic_status_updated(
            incident=incident,
            assignment=assignment,
            mechanic_id=mechanic_link.id,
            detail=detail,
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
        IncidentWorkflowService(self.db).mechanic_location_updated(
            incident=incident,
            assignment=assignment,
            mechanic_id=mechanic_link.id,
            latitude=latitude,
            longitude=longitude,
            location_time=location_time,
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
        return self.submit_final_report(
            user_id=user_id,
            assignment_id=assignment_id,
            description=description,
            final_price=labor_price,
        )

    def submit_final_report(
        self,
        *,
        user_id: UUID,
        assignment_id: UUID,
        description: str,
        final_price: float,
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

        final_price_decimal = Decimal(str(final_price)).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
        if final_price_decimal <= Decimal("0.00"):
            raise HTTPException(
                status_code=400,
                detail="El precio final debe ser mayor a cero",
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
            labor_price=final_price_decimal,
        )
        self.incident_service_report.create(report)

        incident.status = IncidentStatus.PAYMENT_PENDING
        self.db.add(incident)

        assignment.status = AssignmentStatus.PAYMENT_PENDING
        assignment.final_price = final_price_decimal
        self.db.add(assignment)

        mechanic_link.is_available = True
        self.db.add(mechanic_link)

        self.db.commit()
        self.db.refresh(report)

        detail = self._status_detail(IncidentStatus.PAYMENT_PENDING)
        IncidentWorkflowService(self.db).final_report_submitted(
            incident=incident,
            assignment=assignment,
            mechanic_id=mechanic_link.id,
            report=report,
            detail=detail,
        )

        self._send_client_status_push(
            client_user_id=incident.user_id,
            incident_id=incident.id,
            assignment_id=assignment.id,
            status=IncidentStatus.PAYMENT_PENDING.value,
        )

        return {
            "assignment_id": assignment.id,
            "incident_id": incident.id,
            "incident_status": incident.status.value,
            "assignment_status": assignment.status.value,
            "detail": "Reporte final registrado, pago pendiente",
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
                "estimated_minutes": payload.get("estimated_minutes"),
                "client_email": client_user.email if client_user else None,
                "client_name": (
                    f"{client_user.first_name} {client_user.last_name}".strip()
                    if client_user
                    else None
                ),
                "client_phone": client_user.phone if client_user else None,
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

    def _status_detail(self, status: IncidentStatus) -> str:
        if status == IncidentStatus.ON_THE_WAY:
            return "Mecanico en camino"
        if status == IncidentStatus.ARRIVED:
            return "Mecanico llego al incidente"
        if status == IncidentStatus.COMPLETED:
            return "Incidente completado por el mecanico"
        if status == IncidentStatus.PAYMENT_PENDING:
            return "Reporte final enviado, pago pendiente"
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
