from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from sqlalchemy import Column, Numeric, String, Text
from sqlmodel import Field

from app.core.base_model import UUIDBaseModel


class PaymentProvider(str, Enum):
    STRIPE = "stripe"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    CHECKOUT_CREATED = "checkout_created"
    PAID = "paid"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class Payment(UUIDBaseModel, table=True):
    __tablename__ = "payments"

    incident_id: UUID = Field(foreign_key="incident.id", index=True)
    assignment_id: UUID = Field(foreign_key="request_assignment.id", index=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    amount: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    currency: str = Field(sa_column=Column(String(8), nullable=False))
    status: PaymentStatus = Field(default=PaymentStatus.PENDING, index=True)
    provider: PaymentProvider = Field(default=PaymentProvider.STRIPE, index=True)
    stripe_checkout_session_id: str | None = Field(
        default=None,
        sa_column=Column(String(255), unique=True, nullable=True),
    )
    stripe_payment_intent_id: str | None = Field(
        default=None,
        sa_column=Column(String(255), nullable=True),
    )
    checkout_url: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    paid_at: datetime | None = Field(default=None)
