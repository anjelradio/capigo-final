from uuid import UUID

from sqlmodel import Field, Index, text

from app.core.base_model import UUIDBaseModel


class ProblemServiceMap(UUIDBaseModel, table=True):
    __tablename__ = "problem_service_map"
    __table_args__ = (
        Index(
            "uq_problem_service_map_active",
            "problem_id",
            "service_id",
            unique=True,
            sqlite_where=text("state = 1"),
            postgresql_where=text("state = true"),
        ),
    )

    problem_id: UUID = Field(foreign_key="problem.id", index=True)
    service_id: UUID = Field(foreign_key="services.id", index=True)
