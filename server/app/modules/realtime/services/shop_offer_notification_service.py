import asyncio
import logging
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlmodel import Session

from app.core.config import settings
from app.modules.assignments.repositories import RequestAssignmentRepository
from app.modules.assignments.models import AssignmentStatus

from .connection_manager import shop_realtime_manager

logger = logging.getLogger(__name__)


class ShopOfferNotificationService:
    def __init__(self, db: Session):
        self.db = db
        self.request_assignment = RequestAssignmentRepository(db)

    async def notify_next_offer_in_incident_queue(self, incident_id: UUID) -> dict:
        pending = self.request_assignment.list_pending_not_notified_by_incident(incident_id)
        if not pending:
            return {
                "incident_id": incident_id,
                "notified": False,
                "detail": "no_pending_offer_in_queue",
            }

        assignment = pending[0]
        now_utc = datetime.now(UTC)
        assignment.notified_at = now_utc
        assignment.expires_at = now_utc + timedelta(
            seconds=max(settings.ASSIGNMENT_OFFER_TIMEOUT_SEC, 10)
        )
        assignment.notification_attempts += 1
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)

        payload = self.request_assignment.get_offer_notification_payload(assignment.id)
        if not payload:
            return {
                "incident_id": incident_id,
                "notified": False,
                "detail": "assignment_payload_not_found",
            }

        delivered = await shop_realtime_manager.send_to_shop(
            assignment.repair_shop_id,
            event={
                "type": "assignment.offer.created",
                "payload": payload,
            },
        )

        await self._emit_incident_realtime_event(
            incident_id=incident_id,
            event_type="assignment.shop.notified",
            payload={
                "assignment_id": assignment.id,
                "repair_shop_id": assignment.repair_shop_id,
                "expires_at": assignment.expires_at,
                "delivered": delivered,
            },
            assignment_id=assignment.id,
            repair_shop_id=assignment.repair_shop_id,
        )

        return {
            "incident_id": incident_id,
            "assignment_id": assignment.id,
            "shop_id": assignment.repair_shop_id,
            "delivered": delivered,
        }

    def notify_next_offer_in_incident_queue_sync(self, incident_id: UUID) -> dict:
        return asyncio.run(self.notify_next_offer_in_incident_queue(incident_id))

    async def notify_shop_pending_offers(self, shop_id: UUID) -> int:
        now_utc = datetime.now(UTC)
        pending = self.request_assignment.list_pending_active_by_shop(shop_id, now_utc)
        sent = 0

        for assignment in pending:
            payload = self.request_assignment.get_offer_notification_payload(assignment.id)
            if not payload:
                continue

            delivered = await shop_realtime_manager.send_to_shop(
                shop_id,
                event={
                    "type": "assignment.offer.created",
                    "payload": payload,
                },
            )
            if delivered:
                sent += 1

        return sent

    async def expire_overdue_offers_and_notify_next(self, *, limit: int = 100) -> dict:
        now_utc = datetime.now(UTC)
        overdue = self.request_assignment.list_pending_expired(now_utc=now_utc, limit=limit)
        if not overdue:
            return {
                "expired_count": 0,
                "incidents_advanced": 0,
            }

        expired_count = 0
        incident_ids: set[UUID] = set()
        for assignment in overdue:
            if not self._is_assignment_expired(assignment.expires_at):
                continue
            if assignment.status != AssignmentStatus.PENDING:
                continue

            assignment.status = AssignmentStatus.EXPIRED
            assignment.responded_at = now_utc
            self.db.add(assignment)
            expired_count += 1
            incident_ids.add(assignment.incident_id)

        if expired_count == 0:
            return {
                "expired_count": 0,
                "incidents_advanced": 0,
            }

        self.db.commit()

        incidents_advanced = 0
        for incident_id in sorted(incident_ids, key=str):
            await self._emit_incident_realtime_event(
                incident_id=incident_id,
                event_type="assignment.offer.expired",
                payload={
                    "description": "Una oferta expiro y se intentara notificar al siguiente taller",
                },
            )
            result = await self.notify_next_offer_in_incident_queue(incident_id)
            if result.get("assignment_id"):
                incidents_advanced += 1

        return {
            "expired_count": expired_count,
            "incidents_advanced": incidents_advanced,
        }

    def expire_assignment_if_needed(self, assignment_id: UUID) -> bool:
        assignment = self.request_assignment.get_by_id(assignment_id)
        if not assignment:
            return False
        if assignment.status != AssignmentStatus.PENDING:
            return False
        if not self._is_assignment_expired(assignment.expires_at):
            return False

        assignment.status = AssignmentStatus.EXPIRED
        assignment.responded_at = datetime.now(UTC)
        self.db.add(assignment)
        self.db.commit()
        return True

    def _is_assignment_expired(self, expires_at: datetime | None) -> bool:
        if expires_at is None:
            return False

        expires_at_naive = self._to_utc_naive(expires_at)
        return expires_at_naive <= datetime.utcnow()

    def _to_utc_naive(self, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value
        return value.astimezone(UTC).replace(tzinfo=None)

    async def _emit_incident_realtime_event(
        self,
        *,
        incident_id: UUID,
        event_type: str,
        payload: dict,
        assignment_id: UUID | None = None,
        repair_shop_id: UUID | None = None,
    ) -> None:
        try:
            from app.modules.realtime.services.incident_realtime_service import (
                IncidentRealtimeService,
            )

            await IncidentRealtimeService(self.db).publish_incident_event(
                incident_id=incident_id,
                event_type=event_type,
                payload=payload,
                assignment_id=assignment_id,
                repair_shop_id=repair_shop_id,
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
