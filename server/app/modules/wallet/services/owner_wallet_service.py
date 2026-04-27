import json
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from decimal import ROUND_HALF_UP
from urllib.parse import quote
from uuid import UUID
from uuid import uuid4

from fastapi import HTTPException

from app.modules.wallet.models import TransactionStatus, Transactions, TransactionType
from app.modules.wallet.schemas import (
    OwnerWalletBalanceRead,
    OwnerWalletTopupConfirmResponse,
    OwnerWalletTopupQrRead,
    OwnerWalletTransactionRead,
    OwnerWalletTransactionsResponse,
)

from .base_service import WalletBaseService


class OwnerWalletService(WalletBaseService):
    def get_my_wallet_balance(self, owner_id: UUID) -> OwnerWalletBalanceRead:
        wallet = self._get_active_wallet_by_owner_or_404(owner_id)

        return OwnerWalletBalanceRead(
            wallet_id=wallet.id,
            repair_shop_id=wallet.repair_shop_id,
            balance=float(wallet.balance),
            updated_at=wallet.modified_date,
        )

    def list_my_wallet_transactions(self, owner_id: UUID) -> OwnerWalletTransactionsResponse:
        wallet = self._get_active_wallet_by_owner_or_404(owner_id)
        transactions = self.transaction.list_active_by_wallet_id(wallet.id)

        return OwnerWalletTransactionsResponse(
            transactions=[
                OwnerWalletTransactionRead(
                    id=transaction.id,
                    type=transaction.type.value,
                    status=transaction.status.value,
                    amount=self._to_float(transaction.amount),
                    balance_before=self._to_float(transaction.balance_before),
                    balance_after=self._to_float(transaction.balance_after),
                    description=transaction.description,
                    created_at=transaction.created_date,
                )
                for transaction in transactions
            ]
        )

    def create_my_topup_qr(self, owner_id: UUID, amount: float) -> OwnerWalletTopupQrRead:
        wallet = self._get_active_wallet_by_owner_or_404(owner_id)
        decimal_amount = self._to_money_decimal(amount)
        generated_at = datetime.now(UTC)
        expires_at = generated_at + timedelta(minutes=20)
        internal_reference = self._build_internal_reference()

        transaction = Transactions(
            type=TransactionType.TOPUP,
            status=TransactionStatus.PENDING,
            amount=decimal_amount,
            balance_before=wallet.balance,
            balance_after=wallet.balance,
            description=f"Recarga pendiente {internal_reference}",
            wallet_id=wallet.id,
        )

        try:
            self.transaction.create(transaction)
            self.db.commit()
            self.db.refresh(transaction)
        except Exception:
            self.db.rollback()
            raise

        qr_payload = self._build_qr_payload(
            internal_reference=internal_reference,
            transaction_id=transaction.id,
            amount=decimal_amount,
            wallet_id=wallet.id,
            repair_shop_id=wallet.repair_shop_id,
            generated_at=generated_at,
        )
        qr_image_url = self._build_qr_image_url(qr_payload)

        return OwnerWalletTopupQrRead(
            transaction_id=transaction.id,
            internal_reference=internal_reference,
            amount=self._to_float(decimal_amount),
            wallet_id=wallet.id,
            repair_shop_id=wallet.repair_shop_id,
            generated_at=generated_at,
            expires_at=expires_at,
            status=transaction.status.value,
            qr_payload=qr_payload,
            qr_image_url=qr_image_url,
        )

    def confirm_my_topup(self, owner_id: UUID, transaction_id: UUID) -> OwnerWalletTopupConfirmResponse:
        wallet = self._get_active_wallet_by_owner_or_404(owner_id)
        transaction = self.transaction.get_active_by_id(transaction_id)

        if not transaction or transaction.wallet_id != wallet.id:
            raise HTTPException(status_code=404, detail="Recarga no encontrada")

        if transaction.type != TransactionType.TOPUP:
            raise HTTPException(status_code=409, detail="La transaccion no corresponde a una recarga")

        if transaction.status != TransactionStatus.PENDING:
            raise HTTPException(
                status_code=409,
                detail="La recarga ya fue procesada o no puede confirmarse",
            )

        previous_balance = wallet.balance
        new_balance = (previous_balance + transaction.amount).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        try:
            wallet.balance = new_balance
            wallet.modified_date = datetime.utcnow()
            transaction.status = TransactionStatus.POSTED
            transaction.balance_before = previous_balance
            transaction.balance_after = new_balance
            transaction.modified_date = datetime.utcnow()
            self.db.add(wallet)
            self.db.add(transaction)
            self.db.commit()
            self.db.refresh(wallet)
            self.db.refresh(transaction)
        except Exception:
            self.db.rollback()
            raise

        return OwnerWalletTopupConfirmResponse(
            transaction_id=transaction.id,
            status=transaction.status.value,
            previous_balance=self._to_float(previous_balance),
            new_balance=self._to_float(wallet.balance),
        )

    def _to_float(self, value: Decimal) -> float:
        return float(value)

    def _to_money_decimal(self, value: float) -> Decimal:
        return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _build_internal_reference(self) -> str:
        timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        random_suffix = uuid4().hex[:6].upper()
        return f"TOPUP-{timestamp}-{random_suffix}"

    def _build_qr_payload(
        self,
        *,
        internal_reference: str,
        transaction_id: UUID,
        amount: Decimal,
        wallet_id: UUID,
        repair_shop_id: UUID,
        generated_at: datetime,
    ) -> str:
        payload = {
            "reference": internal_reference,
            "transaction_id": str(transaction_id),
            "amount": f"{amount:.2f}",
            "wallet_id": str(wallet_id),
            "repair_shop_id": str(repair_shop_id),
            "generated_at": generated_at.isoformat(),
        }
        return json.dumps(payload, separators=(",", ":"))

    def _build_qr_image_url(self, qr_payload: str) -> str:
        encoded_payload = quote(qr_payload, safe="")
        return f"https://quickchart.io/qr?text={encoded_payload}&size=280"
