from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session

from app.modules.user.models import UserRole

from .base_service import AssignmentBaseService


class OwnerBaseService(AssignmentBaseService):
    def __init__(self, db: Session):
        super().__init__(db)

    def _resolve_owner_shop_id(self, user_id: UUID) -> UUID:
        owner = self._get_user_or_404(user_id)
        if owner.role != UserRole.OWNER:
            raise HTTPException(
                status_code=403,
                detail="Solo los propietarios de taller pueden revisar ofertas",
            )

        shop = self.repair_shop.get_by_owner_id(owner.id)
        if not shop:
            raise HTTPException(status_code=404, detail="Taller no encontrado")

        return shop.id
