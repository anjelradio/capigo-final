from uuid import UUID

from sqlmodel import Session, select

from app.modules.wallet.models import Wallet


class WalletLookupRepository:
    def __init__(self, db: Session):
        self.db = db

    def map_active_wallets_by_shop_ids(self, shop_ids: list[UUID]) -> dict[str, Wallet]:
        if not shop_ids:
            return {}

        query = select(Wallet).where(
            Wallet.repair_shop_id.in_(shop_ids),
            Wallet.state == True,
        )
        wallets = self.db.exec(query).all()
        return {str(wallet.repair_shop_id): wallet for wallet in wallets}
