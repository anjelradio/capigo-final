from uuid import UUID

from sqlmodel import Session, select

from app.modules.wallet.models import Payment, PaymentStatus


class PaymentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, payment: Payment) -> Payment:
        self.db.add(payment)
        return payment

    def get_by_id(self, payment_id: UUID) -> Payment | None:
        query = select(Payment).where(
            Payment.id == payment_id,
            Payment.state == True,
        )
        return self.db.exec(query).first()

    def get_by_stripe_checkout_session_id(self, session_id: str) -> Payment | None:
        query = select(Payment).where(
            Payment.stripe_checkout_session_id == session_id,
            Payment.state == True,
        )
        return self.db.exec(query).first()

    def get_latest_open_by_incident(self, incident_id: UUID) -> Payment | None:
        query = (
            select(Payment)
            .where(
                Payment.incident_id == incident_id,
                Payment.state == True,
                Payment.status.in_((PaymentStatus.PENDING, PaymentStatus.CHECKOUT_CREATED)),
            )
            .order_by(Payment.created_date.desc())
        )
        return self.db.exec(query).first()

    def get_latest_by_incident(self, incident_id: UUID) -> Payment | None:
        query = (
            select(Payment)
            .where(
                Payment.incident_id == incident_id,
                Payment.state == True,
            )
            .order_by(Payment.created_date.desc())
        )
        return self.db.exec(query).first()
