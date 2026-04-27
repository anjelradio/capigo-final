from uuid import UUID

from sqlmodel import Field, Index, text

from app.core.base_model import UUIDBaseModel


class ShopService(UUIDBaseModel, table=True):
    __tablename__ = "shop_services"
    __table_args__ = (
        Index(
            "uq_shop_service_active",
            "service_id",
            "shop_id",
            unique=True,
            sqlite_where=text("state = 1"),
            postgresql_where=text("state = true"),
        ),
    )
    is_available: bool = Field(default=True)
    shop_id: UUID = Field(foreign_key="repair_shop.id", index=True)
    service_id: UUID = Field(foreign_key="services.id", index=True)
