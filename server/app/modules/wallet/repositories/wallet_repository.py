from uuid import UUID

from sqlmodel import Session, select

from app.modules.wallet.models import Wallet


class WalletRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_active_by_repair_shop_id(self, repair_shop_id: UUID) -> Wallet | None:
        query = select(Wallet).where(
            Wallet.repair_shop_id == repair_shop_id,
            Wallet.state == True,
        )
        return self.db.exec(query).first()

    def create(self, wallet: Wallet) -> Wallet:
        self.db.add(wallet)
        return wallet
