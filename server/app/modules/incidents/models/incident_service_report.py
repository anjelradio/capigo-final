from decimal import Decimal
from uuid import UUID

from sqlalchemy import Column, Numeric
from sqlmodel import Field

from app.core.base_model import UUIDBaseModel


class IncidentServiceReport(UUIDBaseModel, table=True):
    __tablename__ = "incident_service_report"

    incident_id: UUID = Field(foreign_key="incident.id", index=True, unique=True)
    description: str = Field(min_length=8, max_length=2000)
    labor_price: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
