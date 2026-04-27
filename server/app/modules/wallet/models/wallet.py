from decimal import Decimal
from uuid import UUID

from sqlalchemy import Column, Numeric
from sqlmodel import Field, Index, text

from app.core.base_model import UUIDBaseModel


class Wallet(UUIDBaseModel, table=True):
    __tablename__ = "wallet"
    __table_args__ = (
        Index(
            "uq_wallet_repair_shop_active",
            "repair_shop_id",
            unique=True,
            sqlite_where=text("state = 1"),
            postgresql_where=text("state = true"),
        ),
    )

    balance: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(Numeric(12, 2), nullable=False),
    )
    repair_shop_id: UUID = Field(foreign_key="repair_shop.id", index=True)
