from uuid import UUID

from sqlmodel import Field, Index, text

from app.core.base_model import UUIDBaseModel


class ShopMechanic(UUIDBaseModel, table=True):
    __tablename__ = "shop_mechanics"
    __table_args__ = (
        Index(
            "uq_shop_mechanic_user_active",
            "user_id",
            unique=True,
            sqlite_where=text("state = 1"),
            postgresql_where=text("state = true"),
        ),
    )
    is_available: bool = Field(default=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    shop_id: UUID = Field(foreign_key="repair_shop.id", index=True)
