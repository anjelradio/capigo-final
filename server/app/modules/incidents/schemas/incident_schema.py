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
    client_request_id: str | None = None
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
    mechanic_name: str | None = None
    mechanic_phone: str | None = None
    estimated_minutes: int | None = None
    quoted_price: Decimal | None = None
    final_price: Decimal | None = None


class ActiveIncidentDetailRead(SQLModel):
    incident: ActiveIncidentCoreRead
    vehicle: VehicleRead
    evidences: list[IncidentEvidenceRead]
    assignment: ActiveIncidentAssignmentRead | None = None


class IncidentCreateResponse(SQLModel):
    incident: IncidentRead


class IncidentActionResponse(SQLModel):
    incident_id: UUID
    status: str
    detail: str


class IncidentFeedbackCreateRequest(SQLModel):
    rating: int
    comment: str | None = None


class IncidentFeedbackRead(SQLModel):
    id: UUID
    incident_id: UUID
    rating: int
    comment: str | None = None
    created_date: datetime


class PendingIncidentFeedbackRead(SQLModel):
    incident_id: UUID
    description: str | None
    problem_name: str | None
    completed_at: datetime | None


class PendingIncidentFeedbackListResponse(SQLModel):
    reminders: list[PendingIncidentFeedbackRead]


class ClientServiceListItemRead(SQLModel):
    incident_id: UUID
    description: str | None
    status: str
    problem_name: str | None
    vehicle_plate: str | None
    created_date: datetime
    updated_date: datetime


class ClientServiceListResponse(SQLModel):
    services: list[ClientServiceListItemRead]


class ClientServiceDetailRead(SQLModel):
    incident_id: UUID
    status: str
    description: str | None
    problem_name: str | None
    delivery_price: Decimal | None
    distance_km: Decimal | None
    address: str | None
    created_date: datetime
    updated_date: datetime
    vehicle: VehicleRead
    repair_shop_name: str | None = None
    mechanic_name: str | None = None
    report_description: str | None = None
    labor_price: Decimal | None = None
