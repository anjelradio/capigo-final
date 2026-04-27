from sqlmodel import Session, select

from app.modules.repair_shop.models import ShopInvitation


class ShopInvitationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_shop_id(self, shop_id):
        query = (
            select(ShopInvitation)
            .where(ShopInvitation.shop_id == shop_id, ShopInvitation.state == True)
            .order_by(ShopInvitation.created_date.desc())
        )
        return self.db.exec(query).first()

    def get_active_by_code(self, code: str) -> ShopInvitation | None:
        query = select(ShopInvitation).where(
            ShopInvitation.code == code,
            ShopInvitation.state == True,
        )
        return self.db.exec(query).first()

    def exists_code(self, code: str) -> bool:
        query = select(ShopInvitation.id).where(
            ShopInvitation.code == code,
            ShopInvitation.state == True,
        )
        return self.db.exec(query).first() is not None

    def create(self, invitation: ShopInvitation) -> ShopInvitation:
        self.db.add(invitation)
        return invitation

    def soft_delete(self, invitation: ShopInvitation) -> None:
        invitation.state = False
        self.db.add(invitation)
