from uuid import UUID

from sqlmodel import Field

from app.core.base_model import UUIDBaseModel


class IncidentFeedback(UUIDBaseModel, table=True):
    __tablename__ = "incident_feedback"

    incident_id: UUID = Field(foreign_key="incident.id", index=True, unique=True)
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, min_length=3, max_length=1000)
