from uuid import UUID

from sqlalchemy import desc
from sqlmodel import Session, select

from app.modules.wallet.models import Transactions


class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_active_by_wallet_id(self, wallet_id: UUID) -> list[Transactions]:
        query = (
            select(Transactions)
            .where(
                Transactions.wallet_id == wallet_id,
                Transactions.state == True,
            )
            .order_by(desc(Transactions.created_date))
        )
        return self.db.exec(query).all()

    def create(self, transaction: Transactions) -> Transactions:
        self.db.add(transaction)
        return transaction

    def get_active_by_id(self, transaction_id: UUID) -> Transactions | None:
        query = select(Transactions).where(
            Transactions.id == transaction_id,
            Transactions.state == True,
        )
        return self.db.exec(query).first()
