from typing import TYPE_CHECKING

from .event_types import IncidentWorkflowEvent

if TYPE_CHECKING:
    from app.modules.realtime.services.realtime_event_publisher import (
        RealtimeEventPublisher,
    )


class PaymentWorkflowEvents:
    def __init__(self, publisher: "RealtimeEventPublisher"):
        self.publisher = publisher

    def payment_checkout_created(self, *, incident, assignment, payment) -> None:
        self.publisher.publish_incident_event(
            incident_id=incident.id,
            event_type=IncidentWorkflowEvent.PAYMENT_CHECKOUT_CREATED,
            payload={
                "payment_id": payment.id,
                "assignment_id": assignment.id,
                "amount": self.publisher.decimal_to_float(payment.amount),
                "currency": payment.currency,
                "status": self.publisher.value(payment.status),
                "description": "Checkout de pago creado",
            },
            status=incident.status,
            assignment_id=assignment.id,
            repair_shop_id=assignment.repair_shop_id,
            mechanic_id=assignment.mechanic_id,
        )

    def payment_completed(self, *, incident, assignment, payment, wallet_snapshot: dict | None) -> None:
        payload = {
            "payment_id": payment.id,
            "assignment_id": assignment.id,
            "amount": self.publisher.decimal_to_float(payment.amount),
            "currency": payment.currency,
            "status": self.publisher.value(payment.status),
            "description": "Pago confirmado por Stripe",
        }
        if wallet_snapshot:
            payload.update(
                {
                    "wallet_balance_before": self.publisher.decimal_to_float(
                        wallet_snapshot.get("balance_before")
                    ),
                    "wallet_balance_after": self.publisher.decimal_to_float(
                        wallet_snapshot.get("balance_after")
                    ),
                    "wallet_debit_amount": self.publisher.decimal_to_float(
                        wallet_snapshot.get("debit_amount")
                    ),
                }
            )

        self.publisher.publish_incident_event(
            incident_id=incident.id,
            event_type=IncidentWorkflowEvent.PAYMENT_COMPLETED,
            payload=payload,
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
                "payment_id": payment.id,
                "review_requested": True,
                "description": "Incidente completado despues del pago",
            },
            status=incident.status,
            assignment_id=assignment.id,
            repair_shop_id=assignment.repair_shop_id,
            mechanic_id=assignment.mechanic_id,
        )
