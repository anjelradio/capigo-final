import asyncio
from decimal import Decimal
from datetime import UTC, datetime
from enum import Enum
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException
from sqlmodel import Session

from app.modules.assignments.repositories import RequestAssignmentRepository
from app.modules.incidents.repositories import IncidentRepository
from app.modules.realtime.repositories import IncidentRealtimeRepository
from app.modules.repair_shop.repositories import RepairShopRepository, ShopMechanicRepository
from app.modules.user.models import User, UserRole

from .connection_manager import shop_realtime_manager


class IncidentRealtimeService:
    def __init__(self, db: Session):
        self.db = db
        self.incident = IncidentRepository(db)
        self.request_assignment = RequestAssignmentRepository(db)
        self.repair_shop = RepairShopRepository(db)
        self.shop_mechanic = ShopMechanicRepository(db)
        self.realtime = IncidentRealtimeRepository(db)

    async def publish_incident_event(
        self,
        *,
        incident_id: UUID,
        event_type: str,
        payload: dict,
        status: str | None = None,
        assignment_id: UUID | None = None,
        repair_shop_id: UUID | None = None,
        mechanic_id: UUID | None = None,
        mechanic_latitude: float | None = None,
        mechanic_longitude: float | None = None,
        mechanic_location_updated_at: datetime | None = None,
    ) -> dict:
        safe_payload = self._to_json_safe(payload)
        safe_status = self._to_scalar_status(status)

        event = self.realtime.create_event(
            incident_id=incident_id,
            event_type=event_type,
            payload=safe_payload,
        )
        self.realtime.upsert_live_state(
            incident_id=incident_id,
            status=safe_status,
            assignment_id=assignment_id,
            repair_shop_id=repair_shop_id,
            mechanic_id=mechanic_id,
            mechanic_latitude=mechanic_latitude,
            mechanic_longitude=mechanic_longitude,
            mechanic_location_updated_at=mechanic_location_updated_at,
        )
        self.db.commit()
        self.db.refresh(event)

        envelope = {
            "type": event_type,
            "payload": safe_payload,
            "meta": {
                "incident_id": incident_id,
                "event_id": event.id,
                "created_at": event.created_date,
            },
        }
        await shop_realtime_manager.send_to_incident(incident_id, envelope)
        return envelope

    def publish_incident_event_sync(self, **kwargs) -> dict:
        return asyncio.run(self.publish_incident_event(**kwargs))

    def get_incident_snapshot_for_user(self, *, user: User, incident_id: UUID) -> dict:
        if not self.can_access_incident(user=user, incident_id=incident_id):
            raise HTTPException(status_code=403, detail="No autorizado para ver este incidente")

        incident = self.incident.get_by_id(incident_id)
        if not incident:
            raise HTTPException(status_code=404, detail="Incidente no encontrado")

        live = self.realtime.get_live_state_by_incident_id(incident_id)
        events = self.realtime.list_recent_events_by_incident_id(incident_id=incident_id, limit=50)
        events.reverse()

        return {
            "incident_id": incident.id,
            "snapshot": {
                "status": live.status if live else incident.status,
                "assignment_id": live.assignment_id if live else None,
                "repair_shop_id": live.repair_shop_id if live else None,
                "mechanic_id": live.mechanic_id if live else None,
                "mechanic_latitude": live.mechanic_latitude if live else None,
                "mechanic_longitude": live.mechanic_longitude if live else None,
                "mechanic_location_updated_at": (
                    live.mechanic_location_updated_at if live else None
                ),
                "last_event_at": live.last_event_at if live else None,
            },
            "events": [
                {
                    "id": event.id,
                    "type": event.event_type,
                    "payload": event.payload,
                    "created_at": event.created_date,
                }
                for event in events
            ],
        }

    def can_access_incident(self, *, user: User, incident_id: UUID) -> bool:
        if user.role == UserRole.ADMIN:
            return True

        if user.role == UserRole.CLIENT:
            incident = self.incident.get_by_id_and_user(incident_id, user.id)
            return incident is not None

        if user.role == UserRole.OWNER:
            shop = self.repair_shop.get_by_owner_id(user.id)
            if not shop:
                return False
            return self.request_assignment.exists_by_incident_and_shop(
                incident_id=incident_id,
                shop_id=shop.id,
            )

        if user.role == UserRole.MECHANIC:
            mechanic_link = self.shop_mechanic.get_active_by_user_id(user.id)
            if not mechanic_link:
                return False
            return self.request_assignment.exists_by_incident_and_mechanic(
                incident_id=incident_id,
                mechanic_id=mechanic_link.id,
            )

        return False

    def _to_json_safe(self, payload: dict) -> dict:
        encoded = jsonable_encoder(payload)
        if isinstance(encoded, dict):
            return encoded
        return {"value": encoded}

    def _to_scalar_status(self, status: str | None) -> str | None:
        if status is None:
            return None
        if isinstance(status, Enum):
            return str(status.value)
        if isinstance(status, Decimal):
            return str(status)
        return str(status)
