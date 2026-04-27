from datetime import datetime
from uuid import UUID

from sqlmodel import Field, SQLModel


class OwnerPendingOfferRead(SQLModel):
    assignment_id: UUID
    incident_id: UUID
    problem_id: UUID | None = None
    problem_name: str | None = None
    incident_description: str | None = None
    distance_km: float | None = None
    delivery_price: float | None = None
    notified_at: datetime | None = None
    expires_at: datetime | None = None


class OwnerPendingOffersResponse(SQLModel):
    offers: list[OwnerPendingOfferRead]


class OwnerHistoryOfferRead(SQLModel):
    assignment_id: UUID
    incident_id: UUID
    problem_id: UUID | None = None
    problem_name: str | None = None
    incident_description: str | None = None
    distance_km: float | None = None
    delivery_price: float | None = None
    status: str
    notified_at: datetime | None = None
    expires_at: datetime | None = None
    responded_at: datetime | None = None


class OwnerOfferHistoryResponse(SQLModel):
    offers: list[OwnerHistoryOfferRead]


class OwnerOfferDetailRead(SQLModel):
    assignment_id: UUID
    incident_id: UUID
    problem_id: UUID | None = None
    problem_name: str | None = None
    incident_description: str | None = None
    incident_latitude: float
    incident_longitude: float
    repair_shop_latitude: float | None = None
    repair_shop_longitude: float | None = None
    distance_km: float | None = None
    delivery_price: float | None = None
    mechanic_name: str | None = None
    notified_at: datetime | None = None
    expires_at: datetime | None = None
    evidence_urls: list[str] = Field(default_factory=list)


class OwnerOfferActionResponse(SQLModel):
    assignment_id: UUID
    incident_id: UUID
    status: str
    detail: str
    next_notified_assignment_id: UUID | None = None


class OwnerAssignmentRead(SQLModel):
    assignment_id: UUID
    incident_id: UUID
    problem_id: UUID | None = None
    problem_name: str | None = None
    incident_description: str | None = None
    distance_km: float | None = None
    delivery_price: float | None = None
    status: str
    mechanic_name: str | None = None
    created_at: datetime


class OwnerAssignmentsResponse(SQLModel):
    assignments: list[OwnerAssignmentRead]


class OwnerOfferAcceptRequest(SQLModel):
    mechanic_id: UUID
