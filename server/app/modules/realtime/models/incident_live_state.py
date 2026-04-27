from datetime import datetime
from uuid import UUID

from sqlmodel import Field

from app.core.base_model import UUIDBaseModel


class IncidentLiveState(UUIDBaseModel, table=True):
    __tablename__ = "incident_live_state"

    incident_id: UUID = Field(foreign_key="incident.id", index=True, unique=True)
    status: str | None = Field(default=None, index=True, max_length=80)
    assignment_id: UUID | None = Field(default=None, foreign_key="request_assignment.id", index=True)
    repair_shop_id: UUID | None = Field(default=None, foreign_key="repair_shop.id", index=True)
    mechanic_id: UUID | None = Field(default=None, foreign_key="shop_mechanics.id", index=True)
    mechanic_latitude: float | None = Field(default=None, ge=-90, le=90)
    mechanic_longitude: float | None = Field(default=None, ge=-180, le=180)
    mechanic_location_updated_at: datetime | None = Field(default=None)
    last_event_at: datetime | None = Field(default=None)
