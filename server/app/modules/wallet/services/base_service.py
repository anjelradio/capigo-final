from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session

from app.modules.repair_shop.models import RepairShop
from app.modules.repair_shop.repositories import RepairShopRepository
from app.modules.user.models import User, UserRole
from app.modules.user.repositories import UserRepository
from app.modules.wallet.models import Wallet
from app.modules.wallet.repositories import TransactionRepository, WalletRepository


class WalletBaseService:
    def __init__(self, db: Session):
        self.db = db
        self.user = UserRepository(db)
        self.repair_shop = RepairShopRepository(db)
        self.wallet = WalletRepository(db)
        self.transaction = TransactionRepository(db)

    def _get_user_or_404(self, user_id: UUID) -> User:
        user = self.user.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return user

    def _ensure_owner_role(self, owner_id: UUID, detail: str) -> User:
        owner = self._get_user_or_404(owner_id)
        if owner.role != UserRole.OWNER:
            raise HTTPException(status_code=403, detail=detail)
        return owner

    def _get_owner_shop_or_404(self, owner_id: UUID) -> RepairShop:
        shop = self.repair_shop.get_by_owner_id(owner_id)
        if not shop:
            raise HTTPException(status_code=404, detail="Taller no encontrado")
        return shop

    def _get_active_wallet_by_owner_or_404(self, owner_id: UUID) -> Wallet:
        self._ensure_owner_role(
            owner_id,
            detail="Solo usuarios owner pueden consultar su billetera",
        )
        shop = self._get_owner_shop_or_404(owner_id)
        wallet = self.wallet.get_active_by_repair_shop_id(shop.id)
        if not wallet:
            raise HTTPException(status_code=404, detail="Billetera activa no encontrada")
        return wallet
