from datetime import UTC, datetime
import logging
from uuid import UUID

from fastapi import HTTPException

from app.modules.assignments.models import AssignmentStatus
from app.modules.incidents.models import IncidentStatus
from app.modules.realtime.services import PushNotificationService, ShopOfferNotificationService
from app.modules.user.models import UserRole

from .base_service import AssignmentBaseService

logger = logging.getLogger(__name__)


class OwnerOfferService(AssignmentBaseService):
    def list_my_pending_offers(self, *, user_id: UUID) -> dict:
        shop_id = self._resolve_owner_shop_id(user_id)
        now_utc = datetime.now(UTC)
        assignments = self.request_assignment.list_pending_active_by_shop(shop_id, now_utc)

        offers: list[dict] = []
        for assignment in assignments:
            payload = self.request_assignment.get_offer_notification_payload(assignment.id)
            if not payload:
                continue

            offers.append(
                {
                    "assignment_id": assignment.id,
                    "incident_id": assignment.incident_id,
                    "problem_id": payload.get("problem_id"),
                    "problem_name": payload.get("problem_name"),
                    "incident_description": payload.get("incident_description"),
                    "distance_km": payload.get("distance_km"),
                    "delivery_price": payload.get("delivery_price"),
                    "notified_at": assignment.notified_at,
                    "expires_at": assignment.expires_at,
                }
            )

        return {"offers": offers}

    def get_my_offer_detail(self, *, user_id: UUID, assignment_id: UUID) -> dict:
        shop_id = self._resolve_owner_shop_id(user_id)
        assignment = self.request_assignment.get_by_id(assignment_id)
        if not assignment or assignment.repair_shop_id != shop_id:
            raise HTTPException(status_code=404, detail="Oferta no encontrada")

        payload = self.request_assignment.get_offer_notification_payload(assignment.id)
        if not payload:
            raise HTTPException(status_code=404, detail="Oferta no encontrada")

        return {
            "assignment_id": assignment.id,
            "incident_id": assignment.incident_id,
            "problem_id": payload.get("problem_id"),
            "problem_name": payload.get("problem_name"),
            "incident_description": payload.get("incident_description"),
            "incident_latitude": payload["incident_latitude"],
            "incident_longitude": payload["incident_longitude"],
            "repair_shop_latitude": payload.get("shop_latitude"),
            "repair_shop_longitude": payload.get("shop_longitude"),
            "distance_km": payload.get("distance_km"),
            "delivery_price": payload.get("delivery_price"),
            "mechanic_name": self.request_assignment.get_mechanic_full_name(
                assignment.mechanic_id
            ),
            "notified_at": assignment.notified_at,
            "expires_at": assignment.expires_at,
            "evidence_urls": payload.get("evidence_urls", []),
        }

    def list_my_offer_history(self, *, user_id: UUID) -> dict:
        shop_id = self._resolve_owner_shop_id(user_id)
        now_utc = datetime.now(UTC)
        assignments = self.request_assignment.list_history_by_shop(shop_id, now_utc)

        offers: list[dict] = []
        for assignment in assignments:
            payload = self.request_assignment.get_offer_notification_payload(assignment.id)
            if not payload:
                continue

            offers.append(
                {
                    "assignment_id": assignment.id,
                    "incident_id": assignment.incident_id,
                    "problem_id": payload.get("problem_id"),
                    "problem_name": payload.get("problem_name"),
                    "incident_description": payload.get("incident_description"),
                    "distance_km": payload.get("distance_km"),
                    "delivery_price": payload.get("delivery_price"),
                    "status": self._resolve_history_status(assignment.status, assignment.expires_at),
                    "notified_at": assignment.notified_at,
                    "expires_at": assignment.expires_at,
                    "responded_at": assignment.responded_at,
                }
            )

        return {"offers": offers}

    def list_my_assignments(self, *, user_id: UUID) -> dict:
        shop_id = self._resolve_owner_shop_id(user_id)
        assignments = self.request_assignment.list_assignments_for_shop(shop_id)

        items: list[dict] = []
        for assignment in assignments:
            payload = self.request_assignment.get_offer_notification_payload(assignment.id)
            if not payload:
                continue

            items.append(
                {
                    "assignment_id": assignment.id,
                    "incident_id": assignment.incident_id,
                    "problem_id": payload.get("problem_id"),
                    "problem_name": payload.get("problem_name"),
                    "incident_description": payload.get("incident_description"),
                    "distance_km": payload.get("distance_km"),
                    "delivery_price": payload.get("delivery_price"),
                    "status": assignment.status.value,
                    "mechanic_name": self.request_assignment.get_mechanic_full_name(
                        assignment.mechanic_id
                    ),
                    "created_at": assignment.created_date,
                }
            )

        return {"assignments": items}

    def reject_my_offer(self, *, user_id: UUID, assignment_id: UUID) -> dict:
        shop_id = self._resolve_owner_shop_id(user_id)
        assignment = self.request_assignment.get_by_id(assignment_id)
        if not assignment or assignment.repair_shop_id != shop_id:
            raise HTTPException(status_code=404, detail="Oferta no encontrada")

        self._ensure_offer_actionable(assignment.status, assignment.expires_at)

        assignment.status = AssignmentStatus.REJECTED
        assignment.responded_at = datetime.now(UTC)
        self.db.add(assignment)
        self.db.commit()

        notify_output = ShopOfferNotificationService(
            self.db
        ).notify_next_offer_in_incident_queue_sync(assignment.incident_id)
        next_assignment_id = notify_output.get("assignment_id")

        self._emit_incident_realtime_event(
            incident_id=assignment.incident_id,
            event_type="assignment.offer.rejected",
            payload={
                "assignment_id": assignment.id,
                "next_notified_assignment_id": next_assignment_id,
                "description": "El taller rechazo la oferta",
            },
            assignment_id=assignment.id,
            repair_shop_id=assignment.repair_shop_id,
        )

        return {
            "assignment_id": assignment.id,
            "incident_id": assignment.incident_id,
            "status": AssignmentStatus.REJECTED.value,
            "detail": "Oferta rechazada",
            "next_notified_assignment_id": next_assignment_id,
        }

    def accept_my_offer(self, *, user_id: UUID, assignment_id: UUID, mechanic_id: UUID) -> dict:
        shop_id = self._resolve_owner_shop_id(user_id)
        assignment = self.request_assignment.get_by_id(assignment_id)
        if not assignment or assignment.repair_shop_id != shop_id:
            raise HTTPException(status_code=404, detail="Oferta no encontrada")

        self._ensure_offer_actionable(assignment.status, assignment.expires_at)

        mechanic_link = self.shop_mechanic.get_active_by_id_and_shop(mechanic_id, shop_id)
        if not mechanic_link:
            raise HTTPException(status_code=404, detail="Mecanico no encontrado en el taller")
        if not mechanic_link.is_available:
            raise HTTPException(status_code=409, detail="El mecanico seleccionado no esta disponible")

        assignment.status = AssignmentStatus.ACCEPTED
        assignment.mechanic_id = mechanic_link.id
        assignment.responded_at = datetime.now(UTC)
        self.db.add(assignment)

        mechanic_link.is_available = False
        self.db.add(mechanic_link)

        incident = self.incident.get_by_id(assignment.incident_id)
        if incident:
            incident.status = IncidentStatus.ASSIGNED
            incident.delivery_price = assignment.delivery_price
            incident.distance_km = assignment.distance_km
            self.db.add(incident)

        remaining_pending = self.request_assignment.list_pending_by_incident_except_shop(
            incident_id=assignment.incident_id,
            exclude_shop_id=assignment.repair_shop_id,
        )
        for pending in remaining_pending:
            pending.status = AssignmentStatus.CANCELLED
            pending.responded_at = datetime.now(UTC)
            self.db.add(pending)

        self.db.commit()

        self._emit_incident_realtime_event(
            incident_id=assignment.incident_id,
            event_type="assignment.accepted",
            payload={
                "assignment_id": assignment.id,
                "mechanic_id": assignment.mechanic_id,
                "repair_shop_id": assignment.repair_shop_id,
                "status": IncidentStatus.ASSIGNED.value,
                "description": "Solicitud aceptada por el taller",
            },
            status=IncidentStatus.ASSIGNED,
            assignment_id=assignment.id,
            repair_shop_id=assignment.repair_shop_id,
            mechanic_id=assignment.mechanic_id,
        )

        self._emit_incident_realtime_event(
            incident_id=assignment.incident_id,
            event_type="incident.status.changed",
            payload={
                "status": IncidentStatus.ASSIGNED.value,
                "assignment_id": assignment.id,
                "mechanic_id": assignment.mechanic_id,
                "description": "Incidente asignado a taller y mecanico",
            },
            status=IncidentStatus.ASSIGNED,
            assignment_id=assignment.id,
            repair_shop_id=assignment.repair_shop_id,
            mechanic_id=assignment.mechanic_id,
        )

        self._emit_incident_realtime_event(
            incident_id=assignment.incident_id,
            event_type="assignment.mechanic.assigned",
            payload={
                "assignment_id": assignment.id,
                "mechanic_id": assignment.mechanic_id,
                "description": "Mecanico asignado al incidente",
            },
            status=IncidentStatus.ASSIGNED,
            assignment_id=assignment.id,
            repair_shop_id=assignment.repair_shop_id,
            mechanic_id=assignment.mechanic_id,
        )

        self._send_mechanic_assignment_push(
            mechanic_user_id=mechanic_link.user_id,
            incident_id=assignment.incident_id,
            assignment_id=assignment.id,
        )

        return {
            "assignment_id": assignment.id,
            "incident_id": assignment.incident_id,
            "status": AssignmentStatus.ACCEPTED.value,
            "detail": "Oferta aceptada",
            "next_notified_assignment_id": None,
        }

    def _send_mechanic_assignment_push(
        self,
        *,
        mechanic_user_id: UUID,
        incident_id: UUID,
        assignment_id: UUID,
    ) -> None:
        try:
            PushNotificationService(self.db).notify_mechanic_assignment_created(
                mechanic_user_id=mechanic_user_id,
                incident_id=incident_id,
                assignment_id=assignment_id,
            )
        except Exception as error:
            logger.warning(
                "No se pudo enviar push a mecanico user_id=%s incident_id=%s error=%s",
                mechanic_user_id,
                incident_id,
                error,
            )

    def _resolve_history_status(
        self, status: AssignmentStatus, expires_at: datetime | None
    ) -> str:
        now_utc_naive = datetime.utcnow()
        expires_at_naive = self._to_utc_naive(expires_at)

        if (
            status == AssignmentStatus.PENDING
            and expires_at_naive is not None
            and expires_at_naive <= now_utc_naive
        ):
            return AssignmentStatus.EXPIRED.value

        return status.value

    def _to_utc_naive(self, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value
        return value.astimezone(UTC).replace(tzinfo=None)

    def _ensure_offer_actionable(
        self, status: AssignmentStatus, expires_at: datetime | None
    ) -> None:
        if status != AssignmentStatus.PENDING:
            raise HTTPException(status_code=409, detail="La oferta ya no esta pendiente")

        expires_at_naive = self._to_utc_naive(expires_at)
        if expires_at_naive is None:
            raise HTTPException(status_code=409, detail="La oferta aun no fue notificada")

        if expires_at_naive <= datetime.utcnow():
            raise HTTPException(status_code=409, detail="La oferta ya expiro")

    def _resolve_owner_shop_id(self, user_id: UUID) -> UUID:
        owner = self._get_user_or_404(user_id)
        if owner.role != UserRole.OWNER:
            raise HTTPException(
                status_code=403,
                detail="Solo los propietarios de taller pueden revisar ofertas",
            )

        shop = self.repair_shop.get_by_owner_id(owner.id)
        if not shop:
            raise HTTPException(status_code=404, detail="Taller no encontrado")

        return shop.id

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
