from uuid import UUID

from sqlmodel import Session, delete, select

from app.modules.repair_shop.models import Service, ShopService


class ShopServiceRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_shop(self, shop_id: UUID) -> list[ShopService]:
        query = select(ShopService).where(
            ShopService.shop_id == shop_id,
            ShopService.state == True,
        )
        return list(self.db.exec(query).all())

    def create_many(self, shop_id: UUID, service_ids: list[UUID]) -> None:
        for service_id in service_ids:
            self.db.add(ShopService(shop_id=shop_id, service_id=service_id))

    def replace_services(self, shop_id: UUID, service_ids: list[UUID]) -> None:
        self.db.exec(
            delete(ShopService).where(
                ShopService.shop_id == shop_id,
                ShopService.state == True,
            )
        )

        for service_id in set(service_ids or []):
            self.db.add(ShopService(shop_id=shop_id, service_id=service_id))

    def list_services_by_shop(self, shop_id: UUID) -> list[Service]:
        query = (
            select(Service)
            .join(ShopService, ShopService.service_id == Service.id)
            .where(
                ShopService.shop_id == shop_id,
                ShopService.state == True,
                Service.state == True,
                Service.is_available == True,
            )
            .order_by(Service.name)
        )
        return list(self.db.exec(query).all())
