from uuid import UUID

from sqlmodel import Session, func, select

from app.modules.repair_shop.models import RepairShop
from app.modules.user.models import User


class RepairShopRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_name(self, name: str) -> RepairShop | None:
        query = select(RepairShop).where(
            func.lower(func.trim(RepairShop.name)) == func.lower(func.trim(name)),
            RepairShop.state == True,
        )
        return self.db.exec(query).first()

    def create(self, repair_shop: RepairShop) -> RepairShop:
        self.db.add(repair_shop)
        return repair_shop

    def get_by_id(self, shop_id: UUID) -> RepairShop | None:
        return self.db.get(RepairShop, shop_id)

    def get_by_owner_id(self, owner_id: UUID) -> RepairShop | None:
        query = select(RepairShop).where(
            RepairShop.owner_id == owner_id,
            RepairShop.state == True,
        )
        return self.db.exec(query).first()

    def list_all_with_owner(self) -> list[tuple[RepairShop, User]]:
        query = (
            select(RepairShop, User)
            .join(User, User.id == RepairShop.owner_id)
            .order_by(RepairShop.created_date.desc())
        )
        return list(self.db.exec(query).all())
