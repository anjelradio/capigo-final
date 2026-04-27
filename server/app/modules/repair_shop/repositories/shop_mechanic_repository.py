from uuid import UUID

from sqlmodel import Session, select

from app.modules.repair_shop.models import ShopMechanic
from app.modules.user.models import User, UserRole


class ShopMechanicRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_active_by_user_id(self, user_id: UUID) -> ShopMechanic | None:
        query = select(ShopMechanic).where(
            ShopMechanic.user_id == user_id,
            ShopMechanic.state == True,
        )
        return self.db.exec(query).first()

    def create(self, shop_mechanic: ShopMechanic) -> ShopMechanic:
        self.db.add(shop_mechanic)
        return shop_mechanic

    def get_by_user_and_shop(self, user_id: UUID, shop_id: UUID) -> ShopMechanic | None:
        query = (
            select(ShopMechanic)
            .where(
                ShopMechanic.user_id == user_id,
                ShopMechanic.shop_id == shop_id,
            )
            .order_by(ShopMechanic.created_date.desc())
        )
        return self.db.exec(query).first()

    def get_active_by_id_and_shop(self, mechanic_id: UUID, shop_id: UUID) -> ShopMechanic | None:
        query = select(ShopMechanic).where(
            ShopMechanic.id == mechanic_id,
            ShopMechanic.shop_id == shop_id,
            ShopMechanic.state == True,
        )
        return self.db.exec(query).first()

    def list_with_user_by_shop(
        self, *, shop_id: UUID, only_available: bool
    ) -> list[tuple[ShopMechanic, User]]:
        query = (
            select(ShopMechanic, User)
            .join(User, User.id == ShopMechanic.user_id)
            .where(
                ShopMechanic.shop_id == shop_id,
                ShopMechanic.state == True,
                User.state == True,
                User.role == UserRole.MECHANIC,
            )
            .order_by(User.first_name.asc(), User.last_name.asc())
        )

        if only_available:
            query = query.where(ShopMechanic.is_available == True)

        return list(self.db.exec(query).all())

    def list_by_shop_including_inactive(self, *, shop_id: UUID) -> list[ShopMechanic]:
        query = (
            select(ShopMechanic)
            .where(ShopMechanic.shop_id == shop_id)
            .order_by(ShopMechanic.created_date.desc())
        )
        return list(self.db.exec(query).all())
