from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlmodel import Session

from .incident_lifecycle_events import IncidentLifecycleEvents
from .mechanic_workflow_events import MechanicWorkflowEvents
from .offer_workflow_events import OfferWorkflowEvents
from .payment_workflow_events import PaymentWorkflowEvents


class IncidentWorkflowService:
    """Fachada del flujo realtime de incidente.

    Los casos de uso siguen llamando este service, mientras los detalles de
    eventos quedan separados por ciclo de vida, ofertas y mecanico.
    """

    def __init__(self, db: Session):
        from app.modules.realtime.services.realtime_event_publisher import (
            RealtimeEventPublisher,
        )

        publisher = RealtimeEventPublisher(db)
        self.lifecycle = IncidentLifecycleEvents(publisher)
        self.offers = OfferWorkflowEvents(publisher)
        self.mechanic = MechanicWorkflowEvents(publisher)
        self.payments = PaymentWorkflowEvents(publisher)

    def incident_created(self, *, incident) -> None:
        self.lifecycle.incident_created(incident=incident)

    def incident_classifying(self, *, incident) -> None:
        self.lifecycle.incident_classifying(incident=incident)

    def incident_classification_failed(self, *, incident) -> None:
        self.lifecycle.incident_classification_failed(incident=incident)

    def incident_classified(self, *, incident) -> None:
        self.lifecycle.incident_classified(incident=incident)

    def searching_shop_started(self, *, incident, offers_created: int) -> None:
        self.lifecycle.searching_shop_started(
            incident=incident,
            offers_created=offers_created,
        )

    def incident_cancelled_by_client(self, *, incident) -> None:
        self.lifecycle.incident_cancelled_by_client(incident=incident)

    def shop_notified(
        self,
        *,
        incident_id: UUID,
        assignment_id: UUID,
        repair_shop_id: UUID,
        expires_at: datetime | None,
        delivered: bool,
    ) -> None:
        self.offers.shop_notified(
            incident_id=incident_id,
            assignment_id=assignment_id,
            repair_shop_id=repair_shop_id,
            expires_at=expires_at,
            delivered=delivered,
        )

    def owner_offer_submitted(
        self,
        *,
        incident,
        assignment,
        repair_shop_name: str | None,
        mechanic_name: str | None,
    ) -> None:
        self.offers.owner_offer_submitted(
            incident=incident,
            assignment=assignment,
            repair_shop_name=repair_shop_name,
            mechanic_name=mechanic_name,
        )

    def client_offer_rejected(self, *, incident, assignment) -> None:
        self.offers.client_offer_rejected(incident=incident, assignment=assignment)

    def shop_offer_rejected(self, *, assignment) -> None:
        self.offers.shop_offer_rejected(assignment=assignment)

    def client_offer_accepted(self, *, incident, assignment, rejected_assignments) -> None:
        self.offers.client_offer_accepted(
            incident=incident,
            assignment=assignment,
            rejected_assignments=rejected_assignments,
        )

    def shop_offer_status_changed(
        self,
        *,
        assignment_id: UUID,
        incident_id: UUID,
        repair_shop_id: UUID,
        status: str,
    ) -> None:
        self.offers.shop_offer_status_changed(
            assignment_id=assignment_id,
            incident_id=incident_id,
            repair_shop_id=repair_shop_id,
            status=status,
        )

    def mechanic_status_updated(
        self,
        *,
        incident,
        assignment,
        mechanic_id: UUID,
        detail: str,
        status_payload_extra: dict | None = None,
    ) -> None:
        self.mechanic.mechanic_status_updated(
            incident=incident,
            assignment=assignment,
            mechanic_id=mechanic_id,
            detail=detail,
            status_payload_extra=status_payload_extra,
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
        self.mechanic.mechanic_location_updated(
            incident=incident,
            assignment=assignment,
            mechanic_id=mechanic_id,
            latitude=latitude,
            longitude=longitude,
            location_time=location_time,
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
        self.mechanic.service_completed(
            incident=incident,
            assignment=assignment,
            mechanic_id=mechanic_id,
            report=report,
            delivery_price=delivery_price,
            wallet_snapshot=wallet_snapshot,
            detail=detail,
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
        self.mechanic.final_report_submitted(
            incident=incident,
            assignment=assignment,
            mechanic_id=mechanic_id,
            report=report,
            detail=detail,
        )

    def payment_checkout_created(self, *, incident, assignment, payment) -> None:
        self.payments.payment_checkout_created(
            incident=incident,
            assignment=assignment,
            payment=payment,
        )

    def payment_completed(self, *, incident, assignment, payment, wallet_snapshot: dict | None) -> None:
        self.payments.payment_completed(
            incident=incident,
            assignment=assignment,
            payment=payment,
            wallet_snapshot=wallet_snapshot,
        )
