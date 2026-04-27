from sqlmodel import Field, Index, text

from app.core.base_model import UUIDBaseModel


class Service(UUIDBaseModel, table=True):
    __tablename__ = "services"
    __table_args__ = (
        Index(
            "uq_service_slug_active",
            "slug",
            unique=True,
            sqlite_where=text("state = 1"),
            postgresql_where=text("state = true"),
        ),
    )

    name: str = Field(min_length=2, max_length=80)
    slug: str = Field(min_length=2, max_length=90, index=True)
    is_available: bool = Field(default=True)
