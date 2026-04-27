from uuid import UUID

from sqlmodel import Field

from app.core.base_model import UUIDBaseModel


class DevicePushToken(UUIDBaseModel, table=True):
    __tablename__ = "device_push_token"

    user_id: UUID = Field(foreign_key="user.id", index=True)
    platform: str = Field(default="android", min_length=2, max_length=20)
    device_id: str | None = Field(default=None, min_length=4, max_length=120, index=True)
    push_token: str = Field(min_length=20, max_length=400, index=True, unique=True)
