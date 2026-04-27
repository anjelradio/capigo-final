from datetime import datetime
from uuid import UUID

from pydantic import field_validator
from sqlmodel import SQLModel


class OwnerWalletBalanceRead(SQLModel):
    wallet_id: UUID
    repair_shop_id: UUID
    balance: float
    updated_at: datetime


class OwnerWalletTransactionRead(SQLModel):
    id: UUID
    type: str
    status: str
    amount: float
    balance_before: float
    balance_after: float
    description: str | None = None
    created_at: datetime


class OwnerWalletTransactionsResponse(SQLModel):
    transactions: list[OwnerWalletTransactionRead]


class OwnerWalletTopupQrCreateRequest(SQLModel):
    amount: float

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("El monto debe ser mayor a 0")

        cents = round(value * 100)
        if abs(value * 100 - cents) > 1e-6:
            raise ValueError("El monto debe tener maximo 2 decimales")

        return value


class OwnerWalletTopupQrRead(SQLModel):
    transaction_id: UUID
    internal_reference: str
    amount: float
    wallet_id: UUID
    repair_shop_id: UUID
    generated_at: datetime
    expires_at: datetime
    status: str
    qr_payload: str
    qr_image_url: str


class OwnerWalletTopupConfirmResponse(SQLModel):
    transaction_id: UUID
    status: str
    previous_balance: float
    new_balance: float
