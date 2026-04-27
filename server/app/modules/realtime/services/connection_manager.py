import asyncio
import json
from collections import defaultdict
from datetime import datetime
from uuid import UUID

from fastapi import WebSocket


class ShopRealtimeConnectionManager:
    def __init__(self):
        self._shop_connections: dict[str, set[WebSocket]] = defaultdict(set)
        self._incident_connections: dict[str, set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def connect_shop(self, websocket: WebSocket, shop_id: UUID) -> None:
        await websocket.accept()
        async with self._lock:
            self._shop_connections[str(shop_id)].add(websocket)

    async def disconnect_shop(self, websocket: WebSocket, shop_id: UUID) -> None:
        async with self._lock:
            shop_key = str(shop_id)
            pool = self._shop_connections.get(shop_key)
            if not pool:
                return
            pool.discard(websocket)
            if not pool:
                self._shop_connections.pop(shop_key, None)

    async def send_to_shop(self, shop_id: UUID, event: dict) -> bool:
        shop_key = str(shop_id)
        async with self._lock:
            sockets = list(self._shop_connections.get(shop_key, set()))

        if not sockets:
            return False

        message = json.dumps(event, default=_json_default)
        failed: list[WebSocket] = []

        for socket in sockets:
            try:
                await socket.send_text(message)
            except Exception:
                failed.append(socket)

        if failed:
            async with self._lock:
                pool = self._shop_connections.get(shop_key)
                if pool:
                    for socket in failed:
                        pool.discard(socket)
                    if not pool:
                        self._shop_connections.pop(shop_key, None)

        return True

    async def connect_incident(self, websocket: WebSocket, incident_id: UUID) -> None:
        await websocket.accept()
        async with self._lock:
            self._incident_connections[str(incident_id)].add(websocket)

    async def disconnect_incident(self, websocket: WebSocket, incident_id: UUID) -> None:
        async with self._lock:
            incident_key = str(incident_id)
            pool = self._incident_connections.get(incident_key)
            if not pool:
                return
            pool.discard(websocket)
            if not pool:
                self._incident_connections.pop(incident_key, None)

    async def send_to_incident(self, incident_id: UUID, event: dict) -> bool:
        incident_key = str(incident_id)
        async with self._lock:
            sockets = list(self._incident_connections.get(incident_key, set()))

        if not sockets:
            return False

        message = json.dumps(event, default=_json_default)
        failed: list[WebSocket] = []

        for socket in sockets:
            try:
                await socket.send_text(message)
            except Exception:
                failed.append(socket)

        if failed:
            async with self._lock:
                pool = self._incident_connections.get(incident_key)
                if pool:
                    for socket in failed:
                        pool.discard(socket)
                    if not pool:
                        self._incident_connections.pop(incident_key, None)

        return True


shop_realtime_manager = ShopRealtimeConnectionManager()


def _json_default(value):
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, UUID):
        return str(value)
    return str(value)
