from datetime import UTC, datetime
from uuid import UUID

from sqlmodel import Session, select

from app.modules.realtime.models import IncidentLiveState, IncidentRealtimeEvent


class IncidentRealtimeRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_event(self, *, incident_id: UUID, event_type: str, payload: dict) -> IncidentRealtimeEvent:
        event = IncidentRealtimeEvent(
            incident_id=incident_id,
            event_type=event_type,
            payload=payload,
        )
        self.db.add(event)
        return event

    def get_live_state_by_incident_id(self, incident_id: UUID) -> IncidentLiveState | None:
        query = select(IncidentLiveState).where(
            IncidentLiveState.incident_id == incident_id,
            IncidentLiveState.state == True,
        )
        return self.db.exec(query).first()

    def upsert_live_state(
        self,
        *,
        incident_id: UUID,
        status: str | None,
        assignment_id: UUID | None,
        repair_shop_id: UUID | None,
        mechanic_id: UUID | None,
        mechanic_latitude: float | None,
        mechanic_longitude: float | None,
        mechanic_location_updated_at: datetime | None,
    ) -> IncidentLiveState:
        live = self.get_live_state_by_incident_id(incident_id)
        if not live:
            live = IncidentLiveState(incident_id=incident_id)

        if status is not None:
            live.status = status
        if assignment_id is not None:
            live.assignment_id = assignment_id
        if repair_shop_id is not None:
            live.repair_shop_id = repair_shop_id
        if mechanic_id is not None:
            live.mechanic_id = mechanic_id
        if mechanic_latitude is not None:
            live.mechanic_latitude = mechanic_latitude
        if mechanic_longitude is not None:
            live.mechanic_longitude = mechanic_longitude
        if mechanic_location_updated_at is not None:
            live.mechanic_location_updated_at = mechanic_location_updated_at

        live.last_event_at = datetime.now(UTC)
        self.db.add(live)
        return live

    def list_recent_events_by_incident_id(
        self, *, incident_id: UUID, limit: int = 50
    ) -> list[IncidentRealtimeEvent]:
        query = (
            select(IncidentRealtimeEvent)
            .where(
                IncidentRealtimeEvent.incident_id == incident_id,
                IncidentRealtimeEvent.state == True,
            )
            .order_by(IncidentRealtimeEvent.created_date.desc())
            .limit(limit)
        )
        return list(self.db.exec(query).all())
