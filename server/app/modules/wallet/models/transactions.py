from decimal import Decimal
from enum import Enum
from uuid import UUID

from sqlalchemy import Column, Numeric
from sqlmodel import Field

from app.core.base_model import UUIDBaseModel


class TransactionType(str, Enum):
    TOPUP = "topup"
    DEBIT_SERVICE = "debit_service"
    REFUND = "refund"
    ADJUSTMENT = "adjustment"


class TransactionStatus(str, Enum):
    PENDING = "pending"
    POSTED = "posted"
    FAILED = "failed"
    REVERSED = "reversed"


class Transactions(UUIDBaseModel, table=True):
    __tablename__ = "transactions"

    type: TransactionType = Field(index=True)
    status: TransactionStatus = Field(default=TransactionStatus.POSTED, index=True)
    amount: Decimal = Field(sa_column=Column(Numeric(12, 2), nullable=False))
    balance_before: Decimal = Field(sa_column=Column(Numeric(12, 2), nullable=False))
    balance_after: Decimal = Field(sa_column=Column(Numeric(12, 2), nullable=False))
    description: str | None = Field(default=None, min_length=3, max_length=280)
    wallet_id: UUID = Field(foreign_key="wallet.id", index=True)
