from uuid import UUID

from sqlmodel import Session, select

from app.modules.repair_shop.models import Service


class ServiceRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_available(self) -> list[Service]:
        query = (
            select(Service)
            .where(Service.state == True, Service.is_available == True)
            .order_by(Service.name)
        )
        return list(self.db.exec(query).all())

    def get_existing_ids(self, ids: list[UUID]) -> set[UUID]:
        if not ids:
            return set()

        query = select(Service.id).where(
            Service.id.in_(ids),
            Service.state == True,
            Service.is_available == True,
        )
        return set(self.db.exec(query).all())

    def get_by_slug(self, slug: str) -> Service | None:
        query = select(Service).where(Service.slug == slug, Service.state == True)
        return self.db.exec(query).first()

    def create(self, service: Service) -> Service:
        self.db.add(service)
        return service
