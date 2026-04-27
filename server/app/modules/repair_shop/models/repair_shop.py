from uuid import UUID

from sqlmodel import Field, Index, text

from app.core.base_model import UUIDBaseModel


class RepairShop(UUIDBaseModel, table=True):
    __tablename__ = "repair_shop"
    __table_args__ = (
        Index(
            "uq_shop_name_active",
            "name",
            unique=True,
            sqlite_where=text("state = 1"),
            postgresql_where=text("state = true"),
        ),
    )

    name: str = Field(index=True, min_length=5, max_length=70)
    text_address: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    is_available: bool = Field(default=True)
    owner_id: UUID = Field(foreign_key="user.id", index=True)
