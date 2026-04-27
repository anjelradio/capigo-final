from uuid import UUID

from sqlmodel import Field

from app.core.base_model import UUIDBaseModel


class Evidence(UUIDBaseModel, table=True):
    __tablename__ = "incident_evidence"

    url: str = Field(min_length=8, max_length=1000)
    incident_id: UUID = Field(foreign_key="incident.id", index=True)
