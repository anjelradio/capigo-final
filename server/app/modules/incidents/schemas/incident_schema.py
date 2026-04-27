from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlmodel import SQLModel

from app.modules.incidents.models import IncidentPriority, IncidentStatus
from app.modules.user.schemas import VehicleRead


class IncidentEvidenceRead(SQLModel):
    id: UUID
    url: str


class IncidentRead(SQLModel):
    id: UUID
    description: str | None
    status: IncidentStatus
    priority: IncidentPriority
    latitude: float
    longitude: float
    vehicle_id: UUID
    problem_id: UUID | None
    created_date: datetime
    evidences: list[IncidentEvidenceRead]


class ActiveIncidentCoreRead(SQLModel):
    id: UUID
    description: str | None
    status: IncidentStatus
    priority: IncidentPriority
    latitude: float
    longitude: float
    delivery_price: Decimal | None
    distance_km: Decimal | None
    created_date: datetime


class ActiveIncidentAssignmentRead(SQLModel):
    request_assignment_id: UUID
    status: str
    repair_shop_id: UUID
    repair_shop_name: str | None
    repair_shop_latitude: float | None
    repair_shop_longitude: float | None
    mechanic_id: UUID | None


class ActiveIncidentDetailRead(SQLModel):
    incident: ActiveIncidentCoreRead
    vehicle: VehicleRead
    evidences: list[IncidentEvidenceRead]
    assignment: ActiveIncidentAssignmentRead | None = None


class IncidentCreateResponse(SQLModel):
    incident: IncidentRead
