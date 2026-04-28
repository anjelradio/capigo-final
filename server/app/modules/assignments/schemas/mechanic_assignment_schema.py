from datetime import datetime
from uuid import UUID

from sqlmodel import SQLModel


class MechanicAssignmentVehicleRead(SQLModel):
    id: UUID
    make: str
    model: str
    plate: str
    color: str
    year: int
    type_name: str | None = None


class MechanicAssignmentIncidentRead(SQLModel):
    id: UUID
    status: str
    description: str | None = None
    address: str | None = None
    latitude: float
    longitude: float
    problem_id: UUID | None = None
    problem_name: str | None = None
    distance_km: float | None = None
    delivery_price: float | None = None
    estimated_minutes: int | None = None
    client_email: str | None = None
    client_name: str | None = None
    client_phone: str | None = None
    evidence_urls: list[str]
    vehicle: MechanicAssignmentVehicleRead | None = None


class MechanicAssignmentRead(SQLModel):
    assignment_id: UUID
    assignment_status: str
    repair_shop_id: UUID
    repair_shop_name: str | None = None
    repair_shop_latitude: float | None = None
    repair_shop_longitude: float | None = None
    mechanic_id: UUID
    assigned_at: datetime | None = None
    incident: MechanicAssignmentIncidentRead


class MechanicActiveAssignmentResponse(SQLModel):
    assignment: MechanicAssignmentRead | None = None


class MechanicAssignmentStatusUpdateRequest(SQLModel):
    status: str


class MechanicAssignmentLocationUpdateRequest(SQLModel):
    latitude: float
    longitude: float
    recorded_at: datetime | None = None


class MechanicAssignmentActionResponse(SQLModel):
    assignment_id: UUID
    incident_id: UUID
    incident_status: str
    assignment_status: str
    detail: str


class MechanicAssignmentCompleteRequest(SQLModel):
    description: str
    labor_price: float


class MechanicTodayStatsRead(SQLModel):
    completed_today: int
    cancelled_today: int


class MechanicServiceListItemRead(SQLModel):
    assignment_id: UUID
    incident_id: UUID
    assignment_status: str
    incident_status: str
    incident_description: str | None = None
    problem_name: str | None = None
    vehicle_plate: str | None = None
    created_date: datetime
    updated_date: datetime


class MechanicServiceListResponse(SQLModel):
    services: list[MechanicServiceListItemRead]
