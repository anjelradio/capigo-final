from datetime import datetime
from uuid import UUID

from sqlmodel import SQLModel


class ClientIncidentOfferRead(SQLModel):
    assignment_id: UUID
    incident_id: UUID
    repair_shop_id: UUID
    repair_shop_name: str | None = None
    quoted_price: float | None = None
    delivery_price: float | None = None
    estimated_minutes: int | None = None
    distance_km: float | None = None
    mechanic_id: UUID | None = None
    mechanic_name: str | None = None
    offered_at: datetime | None = None


class ClientIncidentOffersResponse(SQLModel):
    offers: list[ClientIncidentOfferRead]


class ClientOfferActionResponse(SQLModel):
    assignment_id: UUID
    incident_id: UUID
    assignment_status: str
    incident_status: str
    detail: str
