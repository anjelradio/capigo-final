from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session

from app.modules.assignments.repositories import (
    CandidateShopRepository,
    RequestAssignmentRepository,
    WalletLookupRepository,
)
from app.modules.incidents.models import Incident, IncidentStatus
from app.modules.incidents.repositories import EvidenceRepository, IncidentRepository
from app.modules.repair_shop.repositories import RepairShopRepository, ShopMechanicRepository
from app.modules.user.models import User, UserRole
from app.modules.user.repositories import UserRepository, VehicleRepository


class AssignmentBaseService:
    def __init__(self, db: Session):
        self.db = db
        self.user = UserRepository(db)
        self.incident = IncidentRepository(db)
        self.repair_shop = RepairShopRepository(db)
        self.shop_mechanic = ShopMechanicRepository(db)
        self.candidate_shop = CandidateShopRepository(db)
        self.request_assignment = RequestAssignmentRepository(db)
        self.wallet_lookup = WalletLookupRepository(db)
        self.evidence = EvidenceRepository(db)
        self.vehicle = VehicleRepository(db)

    def _get_user_or_404(self, user_id: UUID) -> User:
        user = self.user.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return user

    def _ensure_client_role(self, user_id: UUID, detail: str) -> User:
        user = self._get_user_or_404(user_id)
        if user.role != UserRole.CLIENT:
            raise HTTPException(status_code=403, detail=detail)
        return user

    def _get_client_incident_or_404(self, *, user_id: UUID, incident_id: UUID) -> Incident:
        incident = self.incident.get_by_id_and_user(incident_id, user_id)
        if not incident:
            raise HTTPException(status_code=404, detail="Incidente no encontrado")
        return incident

    def _ensure_classified_incident(self, incident: Incident) -> None:
        if incident.problem_id is None:
            raise HTTPException(
                status_code=400,
                detail="El incidente aun no tiene problema clasificado",
            )

        if incident.status not in (
            IncidentStatus.CLASSIFIED,
            IncidentStatus.SEARCHING_SHOP,
        ):
            raise HTTPException(
                status_code=400,
                detail="El incidente no esta listo para buscar talleres candidatos",
            )
