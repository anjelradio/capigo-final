from decimal import Decimal
from enum import Enum
from uuid import UUID

from sqlalchemy import Column, Numeric
from sqlmodel import Field

from app.core.base_model import UUIDBaseModel


class IncidentStatus(str, Enum):
    PENDING = "pending"
    CLASSIFYING = "classifying"
    CLASSIFIED = "classified"
    SEARCHING_SHOP = "searching_shop"
    ASSIGNED = "assigned"
    ON_THE_WAY = "on_the_way"
    ARRIVED = "arrived"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class IncidentPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Incident(UUIDBaseModel, table=True):
    __tablename__ = "incident"

    description: str | None = Field(default=None, min_length=5, max_length=1000)
    status: IncidentStatus = Field(default=IncidentStatus.PENDING, index=True)
    priority: IncidentPriority = Field(default=IncidentPriority.MEDIUM)
    address: str | None = Field(default=None, min_length=3, max_length=300)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    ai_confidence: float | None = Field(default=None, ge=0, le=1)
    ai_attempts: int = Field(default=0, ge=0)
    delivery_price: Decimal | None = Field(
        default=None,
        sa_column=Column(Numeric(10, 2), nullable=True),
    )
    distance_km: Decimal | None = Field(
        default=None,
        sa_column=Column(Numeric(10, 3), nullable=True),
    )

    user_id: UUID = Field(foreign_key="user.id", index=True)
    vehicle_id: UUID = Field(foreign_key="vehicle.id", index=True)
    problem_id: UUID | None = Field(default=None, foreign_key="problem.id", index=True)
