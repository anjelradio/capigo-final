from uuid import UUID

from fastapi import HTTPException

from app.modules.repair_shop.models import RepairShop
from app.modules.repair_shop.schemas import ShopServicesAssignRequest

from .base_service import RepairShopBaseService


class ShopCatalogService(RepairShopBaseService):
    def list_services(self):
        return self.service.list_available()

    def assign_shop_services(
        self, payload: ShopServicesAssignRequest, owner_id: UUID
    ) -> RepairShop:
        self._ensure_owner_role(
            owner_id,
            detail="Solo usuarios owner pueden configurar servicios del taller",
        )
        shop = self._get_shop_by_owner_or_404(owner_id)

        existing_ids = self.service.get_existing_ids(payload.service_ids)
        sent_ids = set(payload.service_ids)
        missing_ids = sent_ids - existing_ids
        if missing_ids:
            raise HTTPException(
                status_code=400,
                detail="Uno o mas servicios no existen o no estan disponibles",
            )

        try:
            self.shop_service.replace_services(shop.id, payload.service_ids)
            self.db.commit()
            self.db.refresh(shop)
            return shop
        except Exception:
            self.db.rollback()
            raise

    def list_my_shop_services(self, owner_id: UUID):
        shop = self._get_shop_by_owner_or_404(owner_id)
        return self.shop_service.list_services_by_shop(shop.id)
