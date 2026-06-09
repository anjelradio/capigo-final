from decimal import Decimal, ROUND_HALF_UP
import logging
from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session

from app.modules.assignments.models import AssignmentStatus
from app.modules.assignments.services.assignment_state_transition_service import AssignmentStateTransitionService
from app.modules.incidents.models import IncidentServiceReport, IncidentStatus
from app.modules.incidents.services import IncidentStateTransitionService, IncidentWorkflowService
from app.modules.realtime.services import PushNotificationService

from .mechanic_base_service import MechanicBaseService

logger = logging.getLogger(__name__)


class MechanicReportService(MechanicBaseService):
    def __init__(self, db: Session):
        super().__init__(db)
        self.incident_transition = IncidentStateTransitionService(db)
        self.assignment_transition = AssignmentStateTransitionService(db)

    def complete_my_assignment(
        self,
        *,
        user_id: UUID,
        assignment_id: UUID,
        description: str,
        labor_price: float,
    ) -> dict:
        return self.submit_final_report(
            user_id=user_id,
            assignment_id=assignment_id,
            description=description,
            final_price=labor_price,
        )

    def submit_final_report(
        self,
        *,
        user_id: UUID,
        assignment_id: UUID,
        description: str,
        final_price: float,
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
        if incident.status != IncidentStatus.ARRIVED:
            raise HTTPException(
                status_code=409,
                detail="Solo se puede completar un incidente cuando ya fue marcado como llegado",
            )

        normalized_description = " ".join((description or "").split())
        if len(normalized_description) < 8:
            raise HTTPException(
                status_code=400,
                detail="Debes registrar una descripcion valida del trabajo realizado",
            )

        final_price_decimal = Decimal(str(final_price)).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
        if final_price_decimal <= Decimal("0.00"):
            raise HTTPException(
                status_code=400,
                detail="El precio final debe ser mayor a cero",
            )

        existing_report = self.incident_service_report.get_by_incident_id(incident.id)
        if existing_report:
            raise HTTPException(
                status_code=409,
                detail="El incidente ya tiene un reporte final registrado",
            )

        report = IncidentServiceReport(
            incident_id=incident.id,
            description=normalized_description,
            labor_price=final_price_decimal,
        )
        self.incident_service_report.create(report)

        self.incident_transition.transition_incident(incident, IncidentStatus.PAYMENT_PENDING)

        self.assignment_transition.transition_assignment(assignment, AssignmentStatus.PAYMENT_PENDING)
        assignment.final_price = final_price_decimal
        self.db.add(assignment)

        mechanic_link.is_available = True
        self.db.add(mechanic_link)

        self.db.commit()
        self.db.refresh(report)

        detail = "Reporte final enviado, pago pendiente"
        IncidentWorkflowService(self.db).final_report_submitted(
            incident=incident,
            assignment=assignment,
            mechanic_id=mechanic_link.id,
            report=report,
            detail=detail,
        )

        self._send_client_status_push(
            client_user_id=incident.user_id,
            incident_id=incident.id,
            assignment_id=assignment.id,
            status=IncidentStatus.PAYMENT_PENDING.value,
        )

        return {
            "assignment_id": assignment.id,
            "incident_id": incident.id,
            "incident_status": incident.status.value,
            "assignment_status": assignment.status.value,
            "detail": "Reporte final registrado, pago pendiente",
        }

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
