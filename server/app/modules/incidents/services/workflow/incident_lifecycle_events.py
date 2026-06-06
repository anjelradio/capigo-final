from typing import TYPE_CHECKING

from .event_types import IncidentWorkflowEvent

if TYPE_CHECKING:
    from app.modules.realtime.services.realtime_event_publisher import (
        RealtimeEventPublisher,
    )


class IncidentLifecycleEvents:
    def __init__(self, publisher: "RealtimeEventPublisher"):
        self.publisher = publisher

    def incident_created(self, *, incident) -> None:
        self.publisher.publish_incident_event(
            incident_id=incident.id,
            event_type=IncidentWorkflowEvent.INCIDENT_STATUS_CHANGED,
            payload={
                "status": incident.status,
                "description": "Incidente creado y pendiente de clasificacion",
            },
            status=incident.status,
        )

    def incident_classifying(self, *, incident) -> None:
        self.publisher.publish_incident_event(
            incident_id=incident.id,
            event_type=IncidentWorkflowEvent.INCIDENT_STATUS_CHANGED,
            payload={
                "status": incident.status,
                "description": "Clasificando incidente con IA",
            },
            status=incident.status,
        )

    def incident_classification_failed(self, *, incident) -> None:
        self.publisher.publish_incident_event(
            incident_id=incident.id,
            event_type=IncidentWorkflowEvent.INCIDENT_STATUS_CHANGED,
            payload={
                "status": incident.status,
                "description": "No se pudo clasificar el incidente",
            },
            status=incident.status,
        )

    def incident_classified(self, *, incident) -> None:
        self.publisher.publish_incident_event(
            incident_id=incident.id,
            event_type=IncidentWorkflowEvent.INCIDENT_STATUS_CHANGED,
            payload={
                "status": incident.status,
                "problem_id": incident.problem_id,
                "confidence": incident.ai_confidence,
                "description": "Clasificacion de incidente finalizada",
            },
            status=incident.status,
        )

    def searching_shop_started(self, *, incident, offers_created: int) -> None:
        self.publisher.publish_incident_event(
            incident_id=incident.id,
            event_type=IncidentWorkflowEvent.INCIDENT_STATUS_CHANGED,
            payload={
                "status": incident.status,
                "offers_created": offers_created,
                "description": "Buscando taller para el incidente",
            },
            status=incident.status,
        )

    def incident_cancelled_by_client(self, *, incident) -> None:
        self.publisher.publish_incident_event(
            incident_id=incident.id,
            event_type=IncidentWorkflowEvent.INCIDENT_STATUS_CHANGED,
            payload={
                "status": self.publisher.value(incident.status),
                "description": "Incidente cancelado por el cliente",
                "cancelled_by": "client",
            },
            status=incident.status,
        )
