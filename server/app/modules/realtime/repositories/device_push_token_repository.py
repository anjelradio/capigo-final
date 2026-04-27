from uuid import UUID

from sqlmodel import Session, select

from app.modules.realtime.models import DevicePushToken


class DevicePushTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_push_token(self, push_token: str) -> DevicePushToken | None:
        query = select(DevicePushToken).where(
            DevicePushToken.push_token == push_token,
            DevicePushToken.state == True,
        )
        return self.db.exec(query).first()

    def get_active_by_user_and_device(
        self,
        *,
        user_id: UUID,
        device_id: str,
    ) -> DevicePushToken | None:
        query = select(DevicePushToken).where(
            DevicePushToken.user_id == user_id,
            DevicePushToken.device_id == device_id,
            DevicePushToken.state == True,
        )
        return self.db.exec(query).first()

    def list_active_by_user(self, user_id: UUID) -> list[DevicePushToken]:
        query = (
            select(DevicePushToken)
            .where(
                DevicePushToken.user_id == user_id,
                DevicePushToken.state == True,
            )
            .order_by(DevicePushToken.modified_date.desc())
        )
        return list(self.db.exec(query).all())

    def create(self, token: DevicePushToken) -> DevicePushToken:
        self.db.add(token)
        return token

    def save(self, token: DevicePushToken) -> DevicePushToken:
        self.db.add(token)
        return token
