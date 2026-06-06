from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from .event_types import IncidentWorkflowEvent

if TYPE_CHECKING:
    from app.modules.realtime.services.realtime_event_publisher import (
        RealtimeEventPublisher,
    )


class OfferWorkflowEvents:
    def __init__(self, publisher: "RealtimeEventPublisher"):
        self.publisher = publisher

    def shop_notified(
        self,
        *,
        incident_id: UUID,
        assignment_id: UUID,
        repair_shop_id: UUID,
        expires_at: datetime | None,
        delivered: bool,
    ) -> None:
        self.publisher.publish_incident_event(
            incident_id=incident_id,
            event_type=IncidentWorkflowEvent.ASSIGNMENT_SHOP_NOTIFIED,
            payload={
                "assignment_id": assignment_id,
                "repair_shop_id": repair_shop_id,
                "expires_at": expires_at,
                "delivered": delivered,
            },
            assignment_id=assignment_id,
            repair_shop_id=repair_shop_id,
        )

    def owner_offer_submitted(
        self,
        *,
        incident,
        assignment,
        repair_shop_name: str | None,
        mechanic_name: str | None,
    ) -> None:
        self.publisher.publish_incident_event(
            incident_id=assignment.incident_id,
            event_type=IncidentWorkflowEvent.ASSIGNMENT_OFFER_SUBMITTED,
            payload={
                "assignment_id": assignment.id,
                "incident_id": assignment.incident_id,
                "repair_shop_id": assignment.repair_shop_id,
                "repair_shop_name": repair_shop_name,
                "quoted_price": self.publisher.decimal_to_float(assignment.quoted_price),
                "delivery_price": self.publisher.decimal_to_float(assignment.delivery_price),
                "estimated_minutes": assignment.estimated_minutes,
                "distance_km": self.publisher.decimal_to_float(assignment.distance_km),
                "mechanic_id": assignment.mechanic_id,
                "mechanic_name": mechanic_name,
                "description": "El taller envio una oferta para tu incidente",
            },
            status=incident.status if incident else None,
            assignment_id=assignment.id,
            repair_shop_id=assignment.repair_shop_id,
            mechanic_id=assignment.mechanic_id,
        )

    def client_offer_rejected(self, *, incident, assignment) -> None:
        self.publisher.publish_incident_event(
            incident_id=incident.id,
            event_type=IncidentWorkflowEvent.ASSIGNMENT_OFFER_REJECTED,
            payload={
                "assignment_id": assignment.id,
                "description": "El cliente rechazo una oferta",
            },
            status=incident.status,
            assignment_id=assignment.id,
            repair_shop_id=assignment.repair_shop_id,
            mechanic_id=assignment.mechanic_id,
        )
        self.shop_offer_status_changed(
            assignment_id=assignment.id,
            incident_id=incident.id,
            repair_shop_id=assignment.repair_shop_id,
            status=self.publisher.value(assignment.status),
        )

    def shop_offer_rejected(self, *, assignment) -> None:
        self.publisher.publish_incident_event(
            incident_id=assignment.incident_id,
            event_type=IncidentWorkflowEvent.ASSIGNMENT_OFFER_REJECTED,
            payload={
                "assignment_id": assignment.id,
                "description": "El taller rechazo la oferta",
            },
            assignment_id=assignment.id,
            repair_shop_id=assignment.repair_shop_id,
        )

    def client_offer_accepted(self, *, incident, assignment, rejected_assignments) -> None:
        self.publisher.publish_incident_event(
            incident_id=incident.id,
            event_type=IncidentWorkflowEvent.ASSIGNMENT_CLIENT_ACCEPTED,
            payload={
                "assignment_id": assignment.id,
                "repair_shop_id": assignment.repair_shop_id,
                "mechanic_id": assignment.mechanic_id,
                "status": self.publisher.value(incident.status),
                "description": "El cliente acepto una oferta",
            },
            status=incident.status,
            assignment_id=assignment.id,
            repair_shop_id=assignment.repair_shop_id,
            mechanic_id=assignment.mechanic_id,
        )
        self.publisher.publish_incident_event(
            incident_id=incident.id,
            event_type=IncidentWorkflowEvent.INCIDENT_STATUS_CHANGED,
            payload={
                "status": self.publisher.value(incident.status),
                "assignment_id": assignment.id,
                "mechanic_id": assignment.mechanic_id,
                "description": "Incidente asignado por aceptacion del cliente",
            },
            status=incident.status,
            assignment_id=assignment.id,
            repair_shop_id=assignment.repair_shop_id,
            mechanic_id=assignment.mechanic_id,
        )
        self.shop_offer_status_changed(
            assignment_id=assignment.id,
            incident_id=incident.id,
            repair_shop_id=assignment.repair_shop_id,
            status=self.publisher.value(assignment.status),
        )
        for rejected in rejected_assignments:
            self.shop_offer_status_changed(
                assignment_id=rejected.id,
                incident_id=incident.id,
                repair_shop_id=rejected.repair_shop_id,
                status=self.publisher.value(rejected.status),
            )

    def shop_offer_status_changed(
        self,
        *,
        assignment_id: UUID,
        incident_id: UUID,
        repair_shop_id: UUID,
        status: str,
    ) -> None:
        self.publisher.publish_shop_event(
            repair_shop_id=repair_shop_id,
            event={
                "type": IncidentWorkflowEvent.ASSIGNMENT_OFFER_STATUS_CHANGED,
                "payload": {
                    "assignment_id": assignment_id,
                    "incident_id": incident_id,
                    "status": status,
                },
            },
            log_context=f"assignment_id={assignment_id} incident_id={incident_id}",
        )
