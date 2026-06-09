from datetime import UTC, datetime
import logging
from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session

from app.modules.assignments.models import AssignmentStatus
from app.modules.assignments.services.assignment_state_transition_service import AssignmentStateTransitionService
from app.modules.incidents.models import IncidentStatus
from app.modules.incidents.services import IncidentStateTransitionService, IncidentWorkflowService
from app.modules.realtime.services import PushNotificationService

from .mechanic_base_service import MechanicBaseService

logger = logging.getLogger(__name__)


class MechanicStatusService(MechanicBaseService):
    _ACTIVE_INCIDENT_STATUSES = (
        IncidentStatus.ASSIGNED,
        IncidentStatus.ON_THE_WAY,
        IncidentStatus.ARRIVED,
    )

    def __init__(self, db: Session):
        super().__init__(db)
        self.incident_transition = IncidentStateTransitionService(db)
        self.assignment_transition = AssignmentStateTransitionService(db)

    def update_my_assignment_status(
        self,
        *,
        user_id: UUID,
        assignment_id: UUID,
        target_status: str,
    ) -> dict:
        mechanic_link = self._resolve_mechanic_link(user_id)
        assignment = self.request_assignment.get_by_id_and_mechanic(
            assignment_id=assignment_id,
            mechanic_id=mechanic_link.id,
        )
        if not assignment:
            raise HTTPException(status_code=404, detail="Asignacion no encontrada")
        if assignment.status != AssignmentStatus.ACCEPTED:
            raise HTTPException(status_code=409, detail="La asignacion ya no esta activa")

        incident = self.incident.get_by_id(assignment.incident_id)
        if not incident:
            raise HTTPException(status_code=404, detail="Incidente no encontrado")

        next_status = self._parse_incident_status(target_status)
        if next_status == IncidentStatus.COMPLETED:
            raise HTTPException(
                status_code=400,
                detail="Para finalizar el trabajo debes enviar reporte en el endpoint /submit-final-report",
            )
        self.incident_transition.ensure_mechanic_can_transition(
            current=incident.status,
            target=next_status,
        )

        self.incident_transition.transition_incident(incident, next_status)

        if next_status in (IncidentStatus.COMPLETED, IncidentStatus.CANCELLED):
            target_assignment_status = (
                AssignmentStatus.COMPLETED
                if next_status == IncidentStatus.COMPLETED
                else AssignmentStatus.CANCELLED
            )
            self.assignment_transition.transition_assignment(assignment, target_assignment_status)
            assignment.responded_at = datetime.now(UTC)
            self.db.add(assignment)

            mechanic_link.is_available = True
            self.db.add(mechanic_link)

        self.db.commit()

        detail = self._status_detail(next_status)
        IncidentWorkflowService(self.db).mechanic_status_updated(
            incident=incident,
            assignment=assignment,
            mechanic_id=mechanic_link.id,
            detail=detail,
        )

        if next_status in (
            IncidentStatus.ON_THE_WAY,
            IncidentStatus.ARRIVED,
        ):
            self._send_client_status_push(
                client_user_id=incident.user_id,
                incident_id=incident.id,
                assignment_id=assignment.id,
                status=next_status.value,
            )

        return {
            "assignment_id": assignment.id,
            "incident_id": incident.id,
            "incident_status": incident.status.value,
            "assignment_status": assignment.status.value,
            "detail": detail,
        }

    def update_my_assignment_location(
        self,
        *,
        user_id: UUID,
        assignment_id: UUID,
        latitude: float,
        longitude: float,
        recorded_at: datetime | None,
    ) -> dict:
        mechanic_link = self._resolve_mechanic_link(user_id)
        assignment = self.request_assignment.get_by_id_and_mechanic(
            assignment_id=assignment_id,
            mechanic_id=mechanic_link.id,
        )
        if not assignment:
            raise HTTPException(status_code=404, detail="Asignacion no encontrada")
        if assignment.status != AssignmentStatus.ACCEPTED:
            raise HTTPException(status_code=409, detail="La asignacion ya no esta activa")

        incident = self.incident.get_by_id(assignment.incident_id)
        if not incident:
            raise HTTPException(status_code=404, detail="Incidente no encontrado")
        if incident.status not in self._ACTIVE_INCIDENT_STATUSES:
            raise HTTPException(status_code=409, detail="El incidente no acepta ubicacion en este estado")

        location_time = recorded_at or datetime.now(UTC)
        IncidentWorkflowService(self.db).mechanic_location_updated(
            incident=incident,
            assignment=assignment,
            mechanic_id=mechanic_link.id,
            latitude=latitude,
            longitude=longitude,
            location_time=location_time,
        )

        return {
            "assignment_id": assignment.id,
            "incident_id": incident.id,
            "incident_status": incident.status.value,
            "assignment_status": assignment.status.value,
            "detail": "Ubicacion de mecanico actualizada",
        }

    def _parse_incident_status(self, raw_status: str) -> IncidentStatus:
        normalized = raw_status.strip().lower()
        try:
            return IncidentStatus(normalized)
        except ValueError:
            raise HTTPException(status_code=400, detail="Estado de incidente invalido")

    def _status_detail(self, status: IncidentStatus) -> str:
        if status == IncidentStatus.ON_THE_WAY:
            return "Mecanico en camino"
        if status == IncidentStatus.ARRIVED:
            return "Mecanico llego al incidente"
        if status == IncidentStatus.COMPLETED:
            return "Incidente completado por el mecanico"
        if status == IncidentStatus.PAYMENT_PENDING:
            return "Reporte final enviado, pago pendiente"
        if status == IncidentStatus.CANCELLED:
            return "Incidente cancelado por el mecanico"
        return "Estado actualizado por el mecanico"

    def _send_client_status_push(
        self,
        *,
        client_user_id: UUID,
        incident_id: UUID,
        assignment_id: UUID,
        status: str,
    ) -> None:
        try:
            PushNotificationService(self.db).notify_client_incident_status_changed(
                client_user_id=client_user_id,
                incident_id=incident_id,
                assignment_id=assignment_id,
                status=status,
            )
        except Exception as error:
            logger.warning(
                "No se pudo enviar push al cliente user_id=%s incident_id=%s status=%s error=%s",
                client_user_id,
                incident_id,
                status,
                error,
            )
