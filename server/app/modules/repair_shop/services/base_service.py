from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session

from app.modules.repair_shop.models import RepairShop
from app.modules.repair_shop.repositories import (
    RepairShopRepository,
    ServiceRepository,
    ShopInvitationRepository,
    ShopMechanicRepository,
    ShopServiceRepository,
)
from app.modules.user.models import User, UserRole
from app.modules.user.repositories import UserRepository


class RepairShopBaseService:
    def __init__(self, db: Session):
        self.db = db
        self.repair_shop = RepairShopRepository(db)
        self.service = ServiceRepository(db)
        self.shop_invitation = ShopInvitationRepository(db)
        self.shop_mechanic = ShopMechanicRepository(db)
        self.shop_service = ShopServiceRepository(db)
        self.user = UserRepository(db)

    def _get_user_or_404(self, user_id: UUID) -> User:
        user = self.user.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return user

    def _get_shop_by_owner_or_404(self, owner_id: UUID) -> RepairShop:
        shop = self.repair_shop.get_by_owner_id(owner_id)
        if not shop:
            raise HTTPException(status_code=404, detail="Taller no encontrado")
        return shop

    def _ensure_owner_role(self, owner_id: UUID, detail: str) -> User:
        owner = self._get_user_or_404(owner_id)
        if owner.role != UserRole.OWNER:
            raise HTTPException(status_code=403, detail=detail)
        return owner

    def _ensure_admin_role(self, admin_id: UUID, detail: str) -> User:
        admin = self._get_user_or_404(admin_id)
        if admin.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail=detail)
        return admin
