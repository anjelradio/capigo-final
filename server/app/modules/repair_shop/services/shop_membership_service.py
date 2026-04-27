from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException

from app.modules.repair_shop.models import ShopMechanic
from app.modules.repair_shop.schemas import JoinShopByCodeRequest
from app.modules.user.models import User, UserRole

from .base_service import RepairShopBaseService


class ShopMembershipService(RepairShopBaseService):
    def join_shop_by_code(self, payload: JoinShopByCodeRequest, user_id: UUID) -> User:
        user = self._get_user_or_404(user_id)

        if user.role != UserRole.CLIENT:
            raise HTTPException(
                status_code=409,
                detail="Solo usuarios client pueden unirse a un taller",
            )

        existing_link = self.shop_mechanic.get_active_by_user_id(user_id)
        if existing_link:
            raise HTTPException(
                status_code=409,
                detail="El usuario ya pertenece a un taller como mecanico",
            )

        invitation = self.shop_invitation.get_active_by_code(payload.code)
        if not invitation:
            raise HTTPException(status_code=404, detail="Codigo de invitacion invalido")

        expires_at = invitation.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if expires_at <= datetime.now(timezone.utc):
            raise HTTPException(status_code=409, detail="El codigo de invitacion expiro")

        shop = self.repair_shop.get_by_id(invitation.shop_id)
        if not shop or not shop.state:
            raise HTTPException(status_code=404, detail="Taller no encontrado")

        try:
            previous_link = self.shop_mechanic.get_by_user_and_shop(user_id, shop.id)
            if previous_link:
                previous_link.state = True
                previous_link.deleted_date = None
                previous_link.is_available = True
                self.db.add(previous_link)
            else:
                self.shop_mechanic.create(
                    ShopMechanic(
                        user_id=user_id,
                        shop_id=shop.id,
                    )
                )

            user.role = UserRole.MECHANIC
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception:
            self.db.rollback()
            raise

    def unlink_mechanic_from_shop(self, user_id: UUID) -> User:
        user = self._get_user_or_404(user_id)

        if user.role != UserRole.MECHANIC:
            raise HTTPException(
                status_code=409,
                detail="Solo usuarios mechanic pueden desvincularse de un taller",
            )

        active_link = self.shop_mechanic.get_active_by_user_id(user_id)
        if not active_link:
            raise HTTPException(
                status_code=404, detail="El usuario no pertenece a un taller"
            )

        try:
            active_link.state = False
            active_link.deleted_date = datetime.utcnow()
            active_link.is_available = False
            self.db.add(active_link)

            user.role = UserRole.CLIENT
            self.db.add(user)

            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception:
            self.db.rollback()
            raise
