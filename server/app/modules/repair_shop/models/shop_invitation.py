from datetime import datetime
from uuid import UUID

from sqlmodel import Field, Index, text

from app.core.base_model import UUIDBaseModel


class ShopInvitation(UUIDBaseModel, table=True):
    __table_args__ = (
        Index(
            "uq_shop_invitation_active",
            "shop_id",
            unique=True,
            sqlite_where=text("state = 1"),
            postgresql_where=text("state = true"),
        ),
    )

    code: str = Field(index=True)
    expires_at: datetime
    shop_id: UUID = Field(foreign_key="repair_shop.id", index=True)
