import asyncio
import logging
from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from sqlmodel import Session

logger = logging.getLogger(__name__)


class RealtimeEventPublisher:
    def __init__(self, db: Session):
        self.db = db

    def publish_incident_event(
        self,
        *,
        incident_id: UUID,
        event_type: str,
        payload: dict,
        status=None,
        assignment_id: UUID | None = None,
        repair_shop_id: UUID | None = None,
        mechanic_id: UUID | None = None,
        mechanic_latitude: float | None = None,
        mechanic_longitude: float | None = None,
        mechanic_location_updated_at: datetime | None = None,
    ) -> None:
        try:
            from app.modules.realtime.services.incident_realtime_service import (
                IncidentRealtimeService,
            )

            IncidentRealtimeService(self.db).publish_incident_event_sync(
                incident_id=incident_id,
                event_type=event_type,
                payload=payload,
                status=status,
                assignment_id=assignment_id,
                repair_shop_id=repair_shop_id,
                mechanic_id=mechanic_id,
                mechanic_latitude=mechanic_latitude,
                mechanic_longitude=mechanic_longitude,
                mechanic_location_updated_at=mechanic_location_updated_at,
            )
        except Exception as error:
            try:
                self.db.rollback()
            except Exception:
                pass
            logger.warning(
                "No se pudo emitir evento realtime incident_id=%s type=%s error=%s",
                incident_id,
                event_type,
                error,
            )

    def publish_shop_event(
        self,
        *,
        repair_shop_id: UUID,
        event: dict,
        log_context: str,
    ) -> None:
        try:
            from app.modules.realtime.services.connection_manager import (
                shop_realtime_manager,
            )

            asyncio.run(shop_realtime_manager.send_to_shop(repair_shop_id, event=event))
        except Exception as error:
            logger.warning(
                "No se pudo emitir evento realtime a taller shop_id=%s context=%s error=%s",
                repair_shop_id,
                log_context,
                error,
            )

    def value(self, value) -> str:
        if isinstance(value, Enum):
            return str(value.value)
        return str(value)

    def decimal_to_float(self, value: Decimal | None) -> float | None:
        return float(value) if value is not None else None
