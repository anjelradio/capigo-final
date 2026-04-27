from uuid import UUID
from datetime import datetime

from fastapi import HTTPException

from app.modules.user.models import UserRole

from .base_service import RepairShopBaseService


class ShopMechanicService(RepairShopBaseService):
    def list_my_shop_mechanics(self, *, owner_id: UUID, only_available: bool) -> list[dict]:
        self._ensure_owner_role(owner_id, "Solo los propietarios pueden listar mecanicos")
        shop = self._get_shop_by_owner_or_404(owner_id)
        rows = self.shop_mechanic.list_with_user_by_shop(
            shop_id=shop.id,
            only_available=only_available,
        )

        mechanics: list[dict] = []
        for mechanic, user in rows:
            mechanics.append(
                {
                    "id": mechanic.id,
                    "shop_id": mechanic.shop_id,
                    "user_id": mechanic.user_id,
                    "is_available": mechanic.is_available,
                    "created_date": mechanic.created_date,
                    "user": user,
                }
            )

        return mechanics

    def delete_my_shop_mechanic(self, *, owner_id: UUID, mechanic_id: UUID) -> None:
        self._ensure_owner_role(owner_id, "Solo los propietarios pueden eliminar mecanicos")
        shop = self._get_shop_by_owner_or_404(owner_id)

        shop_mechanic = self.shop_mechanic.get_active_by_id_and_shop(mechanic_id, shop.id)
        if not shop_mechanic:
            raise HTTPException(status_code=404, detail="Mecanico no encontrado")

        mechanic_user = self._get_user_or_404(shop_mechanic.user_id)

        now_utc = datetime.utcnow()
        shop_mechanic.state = False
        shop_mechanic.deleted_date = now_utc
        shop_mechanic.modified_date = now_utc
        self.db.add(shop_mechanic)

        mechanic_user.role = UserRole.CLIENT
        mechanic_user.modified_date = now_utc
        self.db.add(mechanic_user)

        self.db.commit()
