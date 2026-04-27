from uuid import UUID
from datetime import datetime

from fastapi import HTTPException
from sqlmodel import Session

from app.modules.assignments.repositories import RequestAssignmentRepository
from app.modules.repair_shop.schemas import (
    AdminRecentServicesResponse,
    AdminRepairShopOverviewRead,
    AdminRepairShopsResponse,
    ShopMechanicRead,
)
from app.modules.user.models import UserRole

from .base_service import RepairShopBaseService


class AdminService(RepairShopBaseService):
    def __init__(self, db: Session):
        super().__init__(db)
        self.request_assignment = RequestAssignmentRepository(db)

    def list_all_repair_shops(self, *, admin_id: UUID) -> AdminRepairShopsResponse:
        self._ensure_admin_role(
            admin_id,
            detail="Solo usuarios admin pueden listar talleres",
        )

        rows = self.repair_shop.list_all_with_owner()
        return AdminRepairShopsResponse(shops=[self._serialize_shop(shop, owner) for shop, owner in rows])

    def get_repair_shop_overview(
        self,
        *,
        admin_id: UUID,
        shop_id: UUID,
    ) -> AdminRepairShopOverviewRead:
        self._ensure_admin_role(
            admin_id,
            detail="Solo usuarios admin pueden consultar talleres",
        )

        shop = self.repair_shop.get_by_id(shop_id)
        if not shop:
            raise HTTPException(status_code=404, detail="Taller no encontrado")

        owner = self._get_user_or_404(shop.owner_id)
        mechanic_rows = self.shop_mechanic.list_by_shop_including_inactive(shop_id=shop.id)

        total = len(mechanic_rows)
        available = sum(1 for row in mechanic_rows if row.is_available)
        unavailable = total - available
        active_records = sum(1 for row in mechanic_rows if row.state)
        inactive_records = total - active_records

        return AdminRepairShopOverviewRead(
            shop=self._serialize_shop(shop, owner),
            mechanic_stats={
                "total": total,
                "available": available,
                "unavailable": unavailable,
                "active_records": active_records,
                "inactive_records": inactive_records,
            },
            recent_activity=[],
        )

    def list_shop_mechanics_for_admin(
        self,
        *,
        admin_id: UUID,
        shop_id: UUID,
        only_available: bool,
    ) -> list[ShopMechanicRead]:
        self._ensure_admin_role(
            admin_id,
            detail="Solo usuarios admin pueden listar mecanicos",
        )

        shop = self.repair_shop.get_by_id(shop_id)
        if not shop:
            raise HTTPException(status_code=404, detail="Taller no encontrado")

        rows = self.shop_mechanic.list_with_user_by_shop(
            shop_id=shop.id,
            only_available=only_available,
        )

        mechanics: list[ShopMechanicRead] = []
        for mechanic, user in rows:
            mechanics.append(
                ShopMechanicRead(
                    id=mechanic.id,
                    shop_id=mechanic.shop_id,
                    user_id=mechanic.user_id,
                    is_available=mechanic.is_available,
                    created_date=mechanic.created_date,
                    user=user,
                )
            )

        return mechanics

    def delete_shop_mechanic_for_admin(
        self,
        *,
        admin_id: UUID,
        shop_id: UUID,
        mechanic_id: UUID,
    ) -> None:
        self._ensure_admin_role(
            admin_id,
            detail="Solo usuarios admin pueden eliminar mecanicos",
        )

        shop = self.repair_shop.get_by_id(shop_id)
        if not shop:
            raise HTTPException(status_code=404, detail="Taller no encontrado")

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

    def list_recent_services_for_shop(
        self,
        *,
        admin_id: UUID,
        shop_id: UUID,
        limit: int = 5,
    ) -> AdminRecentServicesResponse:
        self._ensure_admin_role(
            admin_id,
            detail="Solo usuarios admin pueden consultar servicios del taller",
        )

        shop = self.repair_shop.get_by_id(shop_id)
        if not shop:
            raise HTTPException(status_code=404, detail="Taller no encontrado")

        services = self.request_assignment.list_recent_accepted_services_by_shop(
            shop_id=shop.id,
            limit=limit,
        )

        return AdminRecentServicesResponse(services=services)

    def _serialize_shop(self, shop, owner) -> dict:
        return {
            "id": shop.id,
            "name": shop.name,
            "text_address": shop.text_address,
            "latitude": shop.latitude,
            "longitude": shop.longitude,
            "is_available": shop.is_available,
            "state": shop.state,
            "owner_id": owner.id,
            "owner_name": f"{owner.first_name} {owner.last_name}".strip(),
            "owner_email": owner.email,
            "created_date": shop.created_date,
            "deleted_date": shop.deleted_date,
        }
