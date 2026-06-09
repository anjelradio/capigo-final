from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session

from app.modules.assignments.repositories import RequestAssignmentRepository
from app.modules.incidents.models import Evidence, Incident
from app.modules.incidents.repositories import (
    EvidenceRepository,
    IncidentFeedbackRepository,
    IncidentRepository,
    IncidentServiceReportRepository,
    ProblemRepository,
)
from app.modules.incidents.services.incident_workflow_service import IncidentWorkflowService
from app.modules.repair_shop.repositories import RepairShopRepository, ShopMechanicRepository
from app.modules.user.models import UserRole
from app.modules.user.repositories import UserRepository, VehicleRepository


class IncidentBaseService:
    def __init__(self, db: Session):
        self.db = db
        self.user = UserRepository(db)
        self.vehicle = VehicleRepository(db)
        self.incident = IncidentRepository(db)
        self.evidence = EvidenceRepository(db)
        self.incident_feedback = IncidentFeedbackRepository(db)
        self.incident_service_report = IncidentServiceReportRepository(db)
        self.request_assignment = RequestAssignmentRepository(db)
        self.repair_shop = RepairShopRepository(db)
        self.shop_mechanic = ShopMechanicRepository(db)
        self.problem = ProblemRepository(db)
        self.workflow = IncidentWorkflowService(db)

    def _validate_client_user(self, user_id: UUID) -> None:
        user = self.user.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        if user.role != UserRole.CLIENT:
            raise HTTPException(
                status_code=403,
                detail="Solo usuarios client pueden crear incidentes",
            )

    def _to_incident_read(self, incident: Incident, evidences: list[Evidence]) -> dict:
        return {
            "id": incident.id,
            "description": incident.description,
            "status": incident.status,
            "priority": incident.priority,
            "latitude": incident.latitude,
            "longitude": incident.longitude,
            "vehicle_id": incident.vehicle_id,
            "problem_id": incident.problem_id,
            "created_date": incident.created_date,
            "client_request_id": incident.client_request_id,
            "evidences": [
                {
                    "id": evidence.id,
                    "url": evidence.url,
                }
                for evidence in evidences
            ],
        }
