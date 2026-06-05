import logging
import asyncio
from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException

from app.modules.assignments.models import AssignmentStatus
from app.modules.incidents.models import IncidentStatus
from app.modules.realtime.services import PushNotificationService

from .base_service import AssignmentBaseService

logger = logging.getLogger(__name__)


class ClientOfferService(AssignmentBaseService):
    def list_my_incident_offers(self, *, user_id: UUID, incident_id: UUID) -> dict:
        self._ensure_client_role(user_id, detail="Solo clientes pueden revisar ofertas")
        incident = self._get_client_incident_or_404(user_id=user_id, incident_id=incident_id)

        offers = self.request_assignment.list_offered_by_incident(incident.id)
        payload: list[dict] = []
        for assignment in offers:
            shop = self.repair_shop.get_by_id(assignment.repair_shop_id)
            payload.append(
                {
                    "assignment_id": assignment.id,
                    "incident_id": assignment.incident_id,
                    "repair_shop_id": assignment.repair_shop_id,
                    "repair_shop_name": shop.name if shop else None,
                    "quoted_price": float(assignment.quoted_price)
                    if assignment.quoted_price is not None
                    else None,
                    "delivery_price": float(assignment.delivery_price)
                    if assignment.delivery_price is not None
                    else None,
                    "estimated_minutes": assignment.estimated_minutes,
                    "distance_km": float(assignment.distance_km)
                    if assignment.distance_km is not None
                    else None,
                    "mechanic_id": assignment.mechanic_id,
                    "mechanic_name": self.request_assignment.get_mechanic_full_name(
                        assignment.mechanic_id
                    ),
                    "offered_at": assignment.responded_at,
                }
            )

        return {"offers": payload}

    def reject_my_incident_offer(
        self,
        *,
        user_id: UUID,
        incident_id: UUID,
        assignment_id: UUID,
    ) -> dict:
        self._ensure_client_role(user_id, detail="Solo clientes pueden rechazar ofertas")
        incident = self._get_client_incident_or_404(user_id=user_id, incident_id=incident_id)
        assignment = self.request_assignment.get_by_id(assignment_id)
        if not assignment or assignment.incident_id != incident.id:
            raise HTTPException(status_code=404, detail="Oferta no encontrada")

        if assignment.status != AssignmentStatus.OFFERED:
            raise HTTPException(status_code=409, detail="La oferta ya no se puede rechazar")

        assignment.status = AssignmentStatus.REJECTED
        assignment.responded_at = datetime.now(UTC)
        self.db.add(assignment)
        self.db.commit()

        self._emit_incident_realtime_event(
            incident_id=incident.id,
            event_type="assignment.offer.rejected",
            payload={
                "assignment_id": assignment.id,
                "description": "El cliente rechazo una oferta",
            },
            status=incident.status,
            assignment_id=assignment.id,
            repair_shop_id=assignment.repair_shop_id,
            mechanic_id=assignment.mechanic_id,
        )
        self._emit_shop_offer_status_changed(
            assignment_id=assignment.id,
            incident_id=incident.id,
            repair_shop_id=assignment.repair_shop_id,
            status=AssignmentStatus.REJECTED.value,
        )

        return {
            "assignment_id": assignment.id,
            "incident_id": incident.id,
            "assignment_status": AssignmentStatus.REJECTED.value,
            "incident_status": incident.status.value,
            "detail": "Oferta rechazada por el cliente",
        }

    def accept_my_incident_offer(
        self,
        *,
        user_id: UUID,
        incident_id: UUID,
        assignment_id: UUID,
    ) -> dict:
        self._ensure_client_role(user_id, detail="Solo clientes pueden aceptar ofertas")
        incident = self._get_client_incident_or_404(user_id=user_id, incident_id=incident_id)
        assignment = self.request_assignment.get_by_id(assignment_id)
        if not assignment or assignment.incident_id != incident.id:
            raise HTTPException(status_code=404, detail="Oferta no encontrada")

        if assignment.status != AssignmentStatus.OFFERED:
            raise HTTPException(status_code=409, detail="La oferta ya no esta disponible")

        if assignment.mechanic_id is None:
            raise HTTPException(
                status_code=409,
                detail="La oferta no tiene un mecanico asociado",
            )

        mechanic_link = self.shop_mechanic.get_active_by_id_and_shop(
            assignment.mechanic_id,
            assignment.repair_shop_id,
        )
        if not mechanic_link or not mechanic_link.state:
            raise HTTPException(status_code=409, detail="El mecanico ya no esta disponible")

        if not mechanic_link.is_available:
            raise HTTPException(status_code=409, detail="El mecanico ya no esta disponible")

        now_utc = datetime.now(UTC)
        assignment.status = AssignmentStatus.ACCEPTED
        assignment.responded_at = now_utc
        self.db.add(assignment)

        mechanic_link.is_available = False
        self.db.add(mechanic_link)

        incident.status = IncidentStatus.ASSIGNED
        incident.delivery_price = assignment.delivery_price
        incident.distance_km = assignment.distance_km
        self.db.add(incident)

        remaining = self.request_assignment.list_offer_candidates_except(
            incident_id=incident.id,
            exclude_assignment_id=assignment.id,
        )
        for candidate in remaining:
            candidate.status = AssignmentStatus.REJECTED
            candidate.responded_at = now_utc
            self.db.add(candidate)

        self.db.commit()

        self._emit_incident_realtime_event(
            incident_id=incident.id,
            event_type="assignment.client.accepted",
            payload={
                "assignment_id": assignment.id,
                "repair_shop_id": assignment.repair_shop_id,
                "mechanic_id": assignment.mechanic_id,
                "status": IncidentStatus.ASSIGNED.value,
                "description": "El cliente acepto una oferta",
            },
            status=IncidentStatus.ASSIGNED,
            assignment_id=assignment.id,
            repair_shop_id=assignment.repair_shop_id,
            mechanic_id=assignment.mechanic_id,
        )
        self._emit_incident_realtime_event(
            incident_id=incident.id,
            event_type="incident.status.changed",
            payload={
                "status": IncidentStatus.ASSIGNED.value,
                "assignment_id": assignment.id,
                "mechanic_id": assignment.mechanic_id,
                "description": "Incidente asignado por aceptacion del cliente",
            },
            status=IncidentStatus.ASSIGNED,
            assignment_id=assignment.id,
            repair_shop_id=assignment.repair_shop_id,
            mechanic_id=assignment.mechanic_id,
        )
        self._emit_shop_offer_status_changed(
            assignment_id=assignment.id,
            incident_id=incident.id,
            repair_shop_id=assignment.repair_shop_id,
            status=AssignmentStatus.ACCEPTED.value,
        )
        for candidate in remaining:
            self._emit_shop_offer_status_changed(
                assignment_id=candidate.id,
                incident_id=incident.id,
                repair_shop_id=candidate.repair_shop_id,
                status=AssignmentStatus.REJECTED.value,
            )

        self._send_mechanic_assignment_push(
            mechanic_user_id=mechanic_link.user_id,
            incident_id=incident.id,
            assignment_id=assignment.id,
        )

        return {
            "assignment_id": assignment.id,
            "incident_id": incident.id,
            "assignment_status": AssignmentStatus.ACCEPTED.value,
            "incident_status": IncidentStatus.ASSIGNED.value,
            "detail": "Oferta aceptada por el cliente",
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

    def _emit_shop_offer_status_changed(
        self,
        *,
        assignment_id: UUID,
        incident_id: UUID,
        repair_shop_id: UUID,
        status: str,
    ) -> None:
        try:
            from app.modules.realtime.services.connection_manager import (
                shop_realtime_manager,
            )

            asyncio.run(
                shop_realtime_manager.send_to_shop(
                    repair_shop_id,
                    event={
                        "type": "assignment.offer.status_changed",
                        "payload": {
                            "assignment_id": assignment_id,
                            "incident_id": incident_id,
                            "status": status,
                        },
                    },
                )
            )
        except Exception as error:
            logger.warning(
                "No se pudo emitir shop status assignment_id=%s incident_id=%s error=%s",
                assignment_id,
                incident_id,
                error,
            )
