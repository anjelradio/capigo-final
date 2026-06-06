from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from .event_types import IncidentWorkflowEvent

if TYPE_CHECKING:
    from app.modules.realtime.services.realtime_event_publisher import (
        RealtimeEventPublisher,
    )


class MechanicWorkflowEvents:
    def __init__(self, publisher: "RealtimeEventPublisher"):
        self.publisher = publisher

    def mechanic_status_updated(
        self,
        *,
        incident,
        assignment,
        mechanic_id: UUID,
        detail: str,
        status_payload_extra: dict | None = None,
    ) -> None:
        self.publisher.publish_incident_event(
            incident_id=incident.id,
            event_type=IncidentWorkflowEvent.MECHANIC_STATUS_UPDATED,
            payload={
                "assignment_id": assignment.id,
                "mechanic_id": mechanic_id,
                "status": self.publisher.value(incident.status),
                "description": detail,
            },
            status=incident.status,
            assignment_id=assignment.id,
            repair_shop_id=assignment.repair_shop_id,
            mechanic_id=mechanic_id,
        )

        status_payload = {
            "status": self.publisher.value(incident.status),
            "assignment_id": assignment.id,
            "mechanic_id": mechanic_id,
            "description": detail,
        }
        if status_payload_extra:
            status_payload.update(status_payload_extra)

        self.publisher.publish_incident_event(
            incident_id=incident.id,
            event_type=IncidentWorkflowEvent.INCIDENT_STATUS_CHANGED,
            payload=status_payload,
            status=incident.status,
            assignment_id=assignment.id,
            repair_shop_id=assignment.repair_shop_id,
            mechanic_id=mechanic_id,
        )

    def mechanic_location_updated(
        self,
        *,
        incident,
        assignment,
        mechanic_id: UUID,
        latitude: float,
        longitude: float,
        location_time: datetime,
    ) -> None:
        self.publisher.publish_incident_event(
            incident_id=incident.id,
            event_type=IncidentWorkflowEvent.MECHANIC_LOCATION_UPDATED,
            payload={
                "assignment_id": assignment.id,
                "mechanic_id": mechanic_id,
                "status": self.publisher.value(incident.status),
                "mechanic_latitude": latitude,
                "mechanic_longitude": longitude,
                "mechanic_location_updated_at": location_time,
            },
            status=incident.status,
            assignment_id=assignment.id,
            repair_shop_id=assignment.repair_shop_id,
            mechanic_id=mechanic_id,
            mechanic_latitude=latitude,
            mechanic_longitude=longitude,
            mechanic_location_updated_at=location_time,
        )

    def final_report_submitted(
        self,
        *,
        incident,
        assignment,
        mechanic_id: UUID,
        report,
        detail: str,
    ) -> None:
        self.publisher.publish_incident_event(
            incident_id=incident.id,
            event_type=IncidentWorkflowEvent.ASSIGNMENT_FINAL_REPORT_SUBMITTED,
            payload={
                "assignment_id": assignment.id,
                "mechanic_id": mechanic_id,
                "report_id": report.id,
                "description": report.description,
                "labor_price": self.publisher.decimal_to_float(report.labor_price),
                "final_price": self.publisher.decimal_to_float(assignment.final_price),
                "status": self.publisher.value(incident.status),
                "description_detail": "El mecanico envio el reporte final del servicio",
            },
            status=incident.status,
            assignment_id=assignment.id,
            repair_shop_id=assignment.repair_shop_id,
            mechanic_id=mechanic_id,
        )
        self.publisher.publish_incident_event(
            incident_id=incident.id,
            event_type=IncidentWorkflowEvent.INCIDENT_STATUS_CHANGED,
            payload={
                "status": self.publisher.value(incident.status),
                "assignment_id": assignment.id,
                "mechanic_id": mechanic_id,
                "final_price": self.publisher.decimal_to_float(assignment.final_price),
                "description": detail,
                "payment_required": True,
            },
            status=incident.status,
            assignment_id=assignment.id,
            repair_shop_id=assignment.repair_shop_id,
            mechanic_id=mechanic_id,
        )

    def service_completed(
        self,
        *,
        incident,
        assignment,
        mechanic_id: UUID,
        report,
        delivery_price: Decimal,
        wallet_snapshot: dict,
        detail: str,
    ) -> None:
        self.mechanic_status_updated(
            incident=incident,
            assignment=assignment,
            mechanic_id=mechanic_id,
            detail=detail,
            status_payload_extra={"review_requested": True},
        )
        self.publisher.publish_incident_event(
            incident_id=incident.id,
            event_type=IncidentWorkflowEvent.INCIDENT_REPORT_CREATED,
            payload={
                "report_id": report.id,
                "assignment_id": assignment.id,
                "mechanic_id": mechanic_id,
                "description": report.description,
                "labor_price": float(report.labor_price),
                "delivery_price": float(delivery_price),
                "wallet_balance_before": float(wallet_snapshot["balance_before"]),
                "wallet_balance_after": float(wallet_snapshot["balance_after"]),
            },
            status=incident.status,
            assignment_id=assignment.id,
            repair_shop_id=assignment.repair_shop_id,
            mechanic_id=mechanic_id,
        )
