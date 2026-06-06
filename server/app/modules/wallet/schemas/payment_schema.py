from datetime import datetime
from uuid import UUID

from sqlmodel import SQLModel


class PaymentCheckoutSessionRead(SQLModel):
    payment_id: UUID
    checkout_session_id: str
    checkout_url: str
    amount: float
    currency: str
    status: str


class PaymentStatusRead(SQLModel):
    payment_id: UUID | None = None
    incident_id: UUID
    assignment_id: UUID | None = None
    amount: float | None = None
    currency: str | None = None
    status: str | None = None
    checkout_session_id: str | None = None
    checkout_url: str | None = None
    paid_at: datetime | None = None
    incident_status: str
    assignment_status: str | None = None


class PaymentVerifyResponse(SQLModel):
    payment_id: UUID
    incident_id: UUID
    assignment_id: UUID
    payment_status: str
    incident_status: str
    assignment_status: str
    paid: bool
    detail: str
