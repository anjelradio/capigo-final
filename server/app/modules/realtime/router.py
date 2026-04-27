import json
import logging
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from sqlmodel import Session

from app.core.db import engine
from app.core.security import decode_token
from app.dependencies.auth import CurrentUser, DBSession
from app.modules.realtime.schemas import (
    DevicePushTokenUpsertRequest,
    DevicePushTokenUpsertResponse,
)
from app.modules.realtime.services import (
    IncidentRealtimeService,
    PushNotificationService,
    ShopOfferNotificationService,
    shop_realtime_manager,
)
from app.modules.user.models import User
from app.modules.repair_shop.repositories import RepairShopRepository
from app.modules.user.models import UserRole
from app.modules.user.repositories import UserRepository

router = APIRouter(prefix="/realtime", tags=["Realtime"])
logger = logging.getLogger(__name__)


@router.post(
    "/me/push-token",
    response_model=DevicePushTokenUpsertResponse,
    status_code=status.HTTP_200_OK,
)
def upsert_my_push_token(
    db: DBSession,
    user: CurrentUser,
    payload: DevicePushTokenUpsertRequest,
):
    return PushNotificationService(db).register_device_token(
        user_id=user.id,
        push_token=payload.push_token,
        platform=payload.platform,
        device_id=payload.device_id,
    )


@router.websocket("/ws/shops/me/offers")
async def shop_offers_websocket(websocket: WebSocket):
    token = websocket.query_params.get("token", "").strip()
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    with Session(engine) as db:
        owner = _resolve_ws_owner(db, token)
        if not owner:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        shop = RepairShopRepository(db).get_by_owner_id(owner.id)
        if not shop:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        shop_id: UUID = shop.id

    await shop_realtime_manager.connect_shop(websocket, shop_id)

    with Session(engine) as db:
        await ShopOfferNotificationService(db).notify_shop_pending_offers(shop_id)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await shop_realtime_manager.disconnect_shop(websocket, shop_id)
    except Exception:
        await shop_realtime_manager.disconnect_shop(websocket, shop_id)


def _resolve_ws_owner(db: Session, token: str):
    try:
        payload = decode_token(token)
        user_id = UUID(payload.get("sub"))
    except Exception:
        return None

    user = UserRepository(db).get_by_id(user_id)
    if not user:
        return None
    if user.role != UserRole.OWNER:
        return None
    return user


@router.websocket("/ws/incidents/{incident_id}")
async def incident_realtime_websocket(websocket: WebSocket, incident_id: UUID):
    token = websocket.query_params.get("token", "").strip()
    if not token:
        logger.warning("WS incident rejected: token missing incident_id=%s", incident_id)
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    with Session(engine) as db:
        user = _resolve_ws_user(db, token)
        if not user:
            logger.warning("WS incident rejected: invalid token incident_id=%s", incident_id)
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        if not IncidentRealtimeService(db).can_access_incident(user=user, incident_id=incident_id):
            logger.warning(
                "WS incident rejected: unauthorized user_id=%s role=%s incident_id=%s",
                user.id,
                user.role,
                incident_id,
            )
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

    await shop_realtime_manager.connect_incident(websocket, incident_id)

    with Session(engine) as db:
        snapshot = IncidentRealtimeService(db).get_incident_snapshot_for_user(
            user=user,
            incident_id=incident_id,
        )
        await websocket.send_text(
            json.dumps(
                {
                    "type": "incident.snapshot",
                    "payload": snapshot,
                },
                default=_json_default,
            )
        )

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await shop_realtime_manager.disconnect_incident(websocket, incident_id)
    except Exception:
        await shop_realtime_manager.disconnect_incident(websocket, incident_id)


@router.get("/incidents/{incident_id}/snapshot", status_code=status.HTTP_200_OK)
def get_incident_realtime_snapshot(db: DBSession, user: CurrentUser, incident_id: UUID):
    return IncidentRealtimeService(db).get_incident_snapshot_for_user(
        user=user,
        incident_id=incident_id,
    )


def _resolve_ws_user(db: Session, token: str) -> User | None:
    try:
        payload = decode_token(token)
        user_id = UUID(payload.get("sub"))
    except Exception:
        return None

    return UserRepository(db).get_by_id(user_id)


def _json_default(value):
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, UUID):
        return str(value)
    return str(value)
