from datetime import datetime
from uuid import UUID
from sqlmodel import Session

from .base_service import AssignmentBaseService
from .mechanic_query_service import MechanicQueryService
from .mechanic_status_service import MechanicStatusService
from .mechanic_report_service import MechanicReportService


class MechanicAssignmentService(AssignmentBaseService):
    def __init__(self, db: Session):
        super().__init__(db)
        self._query = MechanicQueryService(db)
        self._status = MechanicStatusService(db)
        self._report = MechanicReportService(db)

    def get_my_active_assignment(self, *, user_id: UUID) -> dict:
        return self._query.get_my_active_assignment(user_id=user_id)

    def get_my_assignment_detail(self, *, user_id: UUID, assignment_id: UUID) -> dict:
        return self._query.get_my_assignment_detail(user_id=user_id, assignment_id=assignment_id)

    def get_my_today_stats(self, *, user_id: UUID) -> dict:
        return self._query.get_my_today_stats(user_id=user_id)

    def list_my_completed_services(self, *, user_id: UUID) -> dict:
        return self._query.list_my_completed_services(user_id=user_id)

    def list_my_service_history(self, *, user_id: UUID) -> dict:
        return self._query.list_my_service_history(user_id=user_id)

    def get_my_incident_detail(self, *, user_id: UUID, incident_id: UUID) -> dict:
        return self._query.get_my_incident_detail(user_id=user_id, incident_id=incident_id)

    def update_my_assignment_status(
        self,
        *,
        user_id: UUID,
        assignment_id: UUID,
        target_status: str,
    ) -> dict:
        return self._status.update_my_assignment_status(
            user_id=user_id,
            assignment_id=assignment_id,
            target_status=target_status,
        )

    def update_my_assignment_location(
        self,
        *,
        user_id: UUID,
        assignment_id: UUID,
        latitude: float,
        longitude: float,
        recorded_at: datetime | None,
    ) -> dict:
        return self._status.update_my_assignment_location(
            user_id=user_id,
            assignment_id=assignment_id,
            latitude=latitude,
            longitude=longitude,
            recorded_at=recorded_at,
        )

    def complete_my_assignment(
        self,
        *,
        user_id: UUID,
        assignment_id: UUID,
        description: str,
        labor_price: float,
    ) -> dict:
        return self._report.complete_my_assignment(
            user_id=user_id,
            assignment_id=assignment_id,
            description=description,
            labor_price=labor_price,
        )

    def submit_final_report(
        self,
        *,
        user_id: UUID,
        assignment_id: UUID,
        description: str,
        final_price: float,
    ) -> dict:
        return self._report.submit_final_report(
            user_id=user_id,
            assignment_id=assignment_id,
            description=description,
            final_price=final_price,
        )
