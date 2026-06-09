from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID
from datetime import datetime
import logging

from fastapi import HTTPException
from sqlmodel import Session

from app.modules.wallet.models import Transactions, TransactionType, TransactionStatus
from app.modules.wallet.repositories.wallet_repository import WalletRepository

logger = logging.getLogger(__name__)


class WalletDebitService:
    def __init__(self, db: Session):
        self.db = db
        self.wallet_repo = WalletRepository(db)

    def debit_for_completed_service(
        self,
        *,
        assignment_id: UUID,
        repair_shop_id: UUID,
        debit_amount: Decimal,
        is_payment_flow: bool = False,
    ) -> dict | None:
        if debit_amount <= Decimal("0.00"):
            return None

        wallet = self.wallet_repo.get_active_by_repair_shop_id(repair_shop_id)
        if not wallet:
            if is_payment_flow:
                logger.warning(
                    "No se encontro billetera activa para debito de servicio shop_id=%s assignment_id=%s",
                    repair_shop_id,
                    assignment_id,
                )
                return None
            else:
                raise HTTPException(status_code=404, detail="No se encontro billetera activa del taller")

        balance_before = Decimal(str(wallet.balance)).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
        balance_after = (balance_before - debit_amount).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
        wallet.balance = balance_after
        wallet.modified_date = datetime.utcnow()
        self.db.add(wallet)

        description = (
            f"Debito por servicio pagado assignment_id={assignment_id}"
            if is_payment_flow
            else f"Debito por servicio completado assignment_id={assignment_id}"
        )

        transaction = Transactions(
            type=TransactionType.DEBIT_SERVICE,
            status=TransactionStatus.POSTED,
            amount=debit_amount,
            balance_before=balance_before,
            balance_after=balance_after,
            description=description,
            wallet_id=wallet.id,
        )
        self.db.add(transaction)

        return {
            "balance_before": balance_before,
            "balance_after": balance_after,
            "debit_amount": debit_amount,
        }
