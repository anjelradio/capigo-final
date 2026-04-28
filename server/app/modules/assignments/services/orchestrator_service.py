import logging
from uuid import UUID

from sqlmodel import Session

from app.core.config import settings
from app.modules.incidents.repositories import IncidentRepository

from .offer_evaluation_service import OfferEvaluationService

logger = logging.getLogger(__name__)


class AssignmentOrchestratorService:
    DEFAULT_RADIUS_STEPS_KM = [3, 6, 10, 15]
    DEFAULT_MIN_CANDIDATES = 5
    DEFAULT_LIMIT_PER_RADIUS = 20
    DEFAULT_BASE_FEE_BOB = settings.ASSIGNMENT_BASE_FEE_BOB
    DEFAULT_PRICE_PER_KM_BOB = settings.ASSIGNMENT_PRICE_PER_KM_BOB

    def __init__(self, db: Session):
        self.db = db
        self.incident = IncidentRepository(db)

    def run_after_classification(self, incident_id: UUID) -> dict:
        incident = self.incident.get_by_id(incident_id)
        if not incident:
            logger.warning(
                "No se pudo orquestar asignaciones. Incidente no encontrado id=%s",
                incident_id,
            )
            return {
                "incident_id": incident_id,
                "offers_created": 0,
                "detail": "incident_not_found",
            }

        result = OfferEvaluationService(self.db).evaluate_and_create_offers(
            incident_id=incident.id,
            user_id=incident.user_id,
            radius_steps_km=self.DEFAULT_RADIUS_STEPS_KM,
            min_candidates=self.DEFAULT_MIN_CANDIDATES,
            limit_per_radius=self.DEFAULT_LIMIT_PER_RADIUS,
            base_fee_bob=self.DEFAULT_BASE_FEE_BOB,
            price_per_km_bob=self.DEFAULT_PRICE_PER_KM_BOB,
        )

        logger.info(
            "Orquestacion de asignaciones finalizada incident_id=%s offers_created=%s searched_candidates=%s",
            result["incident_id"],
            result["offers_created"],
            result["searched_candidates"],
        )
        return result
