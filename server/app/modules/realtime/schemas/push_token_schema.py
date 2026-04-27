from sqlmodel import SQLModel


class DevicePushTokenUpsertRequest(SQLModel):
    push_token: str
    platform: str = "android"
    device_id: str | None = None


class DevicePushTokenUpsertResponse(SQLModel):
    registered: bool
    detail: str
