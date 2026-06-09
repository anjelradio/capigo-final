from datetime import UTC, datetime
import logging
from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session

from app.modules.assignments.models import AssignmentStatus
from app.modules.assignments.services.assignment_state_transition_service import AssignmentStateTransitionService
from app.modules.incidents.services.incident_workflow_service import IncidentWorkflowService

from .owner_base_service import OwnerBaseService

logger = logging.getLogger(__name__)


class OwnerOfferManagementService(OwnerBaseService):
    def __init__(self, db: Session):
        super().__init__(db)
        self.assignment_transition = AssignmentStateTransitionService(db)

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
                    "quoted_price": float(assignment.quoted_price)
                    if assignment.quoted_price is not None
                    else None,
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

        incident = self.incident.get_by_id(assignment.incident_id)

        payload = self.request_assignment.get_offer_notification_payload(assignment.id)
        if not payload:
            raise HTTPException(status_code=404, detail="Oferta no encontrada")

        return {
            "assignment_id": assignment.id,
            "incident_id": assignment.incident_id,
            "assignment_status": assignment.status.value,
            "incident_status": incident.status.value if incident else None,
            "problem_id": payload.get("problem_id"),
            "problem_name": payload.get("problem_name"),
            "incident_description": payload.get("incident_description"),
            "incident_latitude": payload["incident_latitude"],
            "incident_longitude": payload["incident_longitude"],
            "repair_shop_latitude": payload.get("shop_latitude"),
            "repair_shop_longitude": payload.get("shop_longitude"),
            "distance_km": payload.get("distance_km"),
            "delivery_price": payload.get("delivery_price"),
            "quoted_price": float(assignment.quoted_price)
            if assignment.quoted_price is not None
            else None,
            "mechanic_name": self.request_assignment.get_mechanic_full_name(
                assignment.mechanic_id
            ),
            "notified_at": assignment.notified_at,
            "expires_at": assignment.expires_at,
            "evidence_urls": payload.get("evidence_urls", []),
        }

    def reject_my_offer(self, *, user_id: UUID, assignment_id: UUID) -> dict:
        shop_id = self._resolve_owner_shop_id(user_id)
        assignment = self.request_assignment.get_by_id(assignment_id)
        if not assignment or assignment.repair_shop_id != shop_id:
            raise HTTPException(status_code=404, detail="Oferta no encontrada")

        self._ensure_offer_submittable(assignment.status, assignment.expires_at)

        self.assignment_transition.transition_assignment(assignment, AssignmentStatus.REJECTED)
        assignment.responded_at = datetime.now(UTC)
        self.db.add(assignment)
        self.db.commit()

        IncidentWorkflowService(self.db).shop_offer_rejected(assignment=assignment)

        return {
            "assignment_id": assignment.id,
            "incident_id": assignment.incident_id,
            "status": AssignmentStatus.REJECTED.value,
            "detail": "Oferta rechazada",
            "next_notified_assignment_id": None,
        }

    def submit_my_offer(
        self,
        *,
        user_id: UUID,
        assignment_id: UUID,
        mechanic_id: UUID,
        quoted_price: float,
    ) -> dict:
        shop_id = self._resolve_owner_shop_id(user_id)
        assignment = self.request_assignment.get_by_id(assignment_id)
        if not assignment or assignment.repair_shop_id != shop_id:
            raise HTTPException(status_code=404, detail="Oferta no encontrada")

        self._ensure_offer_submittable(assignment.status, assignment.expires_at)

        mechanic_link = self.shop_mechanic.get_active_by_id_and_shop(mechanic_id, shop_id)
        if not mechanic_link:
            raise HTTPException(status_code=404, detail="Mecanico no encontrado en el taller")

        if quoted_price <= 0:
            raise HTTPException(status_code=400, detail="El precio ofertado debe ser mayor a 0")

        self.assignment_transition.transition_assignment(assignment, AssignmentStatus.OFFERED)
        assignment.mechanic_id = mechanic_link.id
        assignment.quoted_price = quoted_price
        assignment.responded_at = datetime.now(UTC)
        self.db.add(assignment)

        self.db.commit()

        incident = self.incident.get_by_id(assignment.incident_id)
        shop = self.repair_shop.get_by_id(assignment.repair_shop_id)
        mechanic_name = self.request_assignment.get_mechanic_full_name(assignment.mechanic_id)

        IncidentWorkflowService(self.db).owner_offer_submitted(
            incident=incident,
            assignment=assignment,
            repair_shop_name=shop.name if shop else None,
            mechanic_name=mechanic_name,
        )

        if incident:
            self._notify_client_offer_received(
                client_user_id=incident.user_id,
                incident_id=incident.id,
                assignment_id=assignment.id,
            )

        return {
            "assignment_id": assignment.id,
            "incident_id": assignment.incident_id,
            "status": AssignmentStatus.OFFERED.value,
            "detail": "Oferta enviada al cliente",
            "next_notified_assignment_id": None,
        }

    def _to_utc_naive(self, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value
        return value.astimezone(UTC).replace(tzinfo=None)

    def _ensure_offer_submittable(
        self, status: AssignmentStatus, expires_at: datetime | None
    ) -> None:
        if status not in (AssignmentStatus.PENDING, AssignmentStatus.OFFERED):
            raise HTTPException(status_code=409, detail="La oferta ya no admite edicion")

        expires_at_naive = self._to_utc_naive(expires_at)
        if expires_at_naive is None:
            raise HTTPException(status_code=409, detail="La oferta aun no fue notificada")

        if expires_at_naive <= datetime.utcnow():
            raise HTTPException(status_code=409, detail="La oferta ya expiro")

    def _notify_client_offer_received(
        self,
        *,
        client_user_id: UUID,
        incident_id: UUID,
        assignment_id: UUID,
    ) -> None:
        try:
            from app.modules.realtime.services import PushNotificationService

            PushNotificationService(self.db).notify_client_offer_received(
                client_user_id=client_user_id,
                incident_id=incident_id,
                assignment_id=assignment_id,
            )
        except Exception as error:
            logger.warning(
                "No se pudo enviar push de oferta al cliente user_id=%s incident_id=%s error=%s",
                client_user_id,
                incident_id,
                error,
            )
