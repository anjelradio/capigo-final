from decimal import Decimal
from enum import Enum
from datetime import datetime
from uuid import UUID

from sqlalchemy import Column, Numeric
from sqlmodel import Field

from app.core.base_model import UUIDBaseModel


class AssignmentStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    COMPLETED = "completed"
    FAILED = "failed"


class RequestAssignment(UUIDBaseModel, table=True):
    __tablename__ = "request_assignment"

    incident_id: UUID = Field(foreign_key="incident.id", index=True)
    repair_shop_id: UUID = Field(foreign_key="repair_shop.id", index=True)
    mechanic_id: UUID | None = Field(
        default=None,
        foreign_key="shop_mechanics.id",
        index=True,
    )
    status: AssignmentStatus = Field(default=AssignmentStatus.PENDING, index=True)
    queue_rank: int | None = Field(default=None, ge=1, index=True)
    offered_at: datetime | None = Field(default=None)
    notified_at: datetime | None = Field(default=None, index=True)
    expires_at: datetime | None = Field(default=None, index=True)
    responded_at: datetime | None = Field(default=None)
    notification_attempts: int = Field(default=0, ge=0)
    distance_km: Decimal | None = Field(
        default=None,
        sa_column=Column(Numeric(10, 3), nullable=True),
    )
    delivery_price: Decimal | None = Field(
        default=None,
        sa_column=Column(Numeric(10, 2), nullable=True),
    )
