from datetime import UTC, datetime, timedelta
from uuid import UUID
from zoneinfo import ZoneInfo

from fastapi import HTTPException
from sqlmodel import Session

from app.core.config import settings

from .mechanic_base_service import MechanicBaseService


class MechanicQueryService(MechanicBaseService):
    def __init__(self, db: Session):
        super().__init__(db)

    def get_my_active_assignment(self, *, user_id: UUID) -> dict:
        mechanic_link = self._resolve_mechanic_link(user_id)
        assignment = self.request_assignment.get_latest_active_by_mechanic(mechanic_link.id)
        if not assignment:
            return {"assignment": None}

        return {
            "assignment": self._build_assignment_read(assignment),
        }

    def get_my_assignment_detail(self, *, user_id: UUID, assignment_id: UUID) -> dict:
        mechanic_link = self._resolve_mechanic_link(user_id)
        assignment = self.request_assignment.get_by_id_and_mechanic(
            assignment_id=assignment_id,
            mechanic_id=mechanic_link.id,
        )
        if not assignment:
            raise HTTPException(status_code=404, detail="Asignacion no encontrada")

        return self._build_assignment_read(assignment)

    def get_my_today_stats(self, *, user_id: UUID) -> dict:
        mechanic_link = self._resolve_mechanic_link(user_id)

        start_utc, end_utc = self._today_utc_window()
        return self.request_assignment.get_today_status_totals_for_mechanic(
            mechanic_id=mechanic_link.id,
            start_utc=start_utc,
            end_utc=end_utc,
        )

    def list_my_completed_services(self, *, user_id: UUID) -> dict:
        mechanic_link = self._resolve_mechanic_link(user_id)
        services = self.request_assignment.list_services_by_mechanic(
            mechanic_id=mechanic_link.id,
            only_completed=True,
        )
        return {"services": services}

    def list_my_service_history(self, *, user_id: UUID) -> dict:
        mechanic_link = self._resolve_mechanic_link(user_id)
        services = self.request_assignment.list_services_by_mechanic(
            mechanic_id=mechanic_link.id,
            only_completed=False,
        )
        return {"services": services}

    def get_my_incident_detail(self, *, user_id: UUID, incident_id: UUID) -> dict:
        mechanic_link = self._resolve_mechanic_link(user_id)
        assignment = self.request_assignment.get_latest_by_incident_and_mechanic(
            incident_id=incident_id,
            mechanic_id=mechanic_link.id,
        )
        if not assignment:
            raise HTTPException(status_code=404, detail="Servicio no encontrado")

        return self._build_assignment_read(assignment)

    def _today_utc_window(self) -> tuple[datetime, datetime]:
        local_now = datetime.now(ZoneInfo(settings.TIME_ZONE))
        start_local = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_local = start_local + timedelta(days=1)

        start_utc = start_local.astimezone(UTC).replace(tzinfo=None)
        end_utc = end_local.astimezone(UTC).replace(tzinfo=None)
        return start_utc, end_utc
