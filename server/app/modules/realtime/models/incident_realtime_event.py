from uuid import UUID

from sqlalchemy import JSON, Column
from sqlmodel import Field

from app.core.base_model import UUIDBaseModel


class IncidentRealtimeEvent(UUIDBaseModel, table=True):
    __tablename__ = "incident_realtime_event"

    incident_id: UUID = Field(foreign_key="incident.id", index=True)
    event_type: str = Field(index=True, min_length=3, max_length=120)
    payload: dict = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
