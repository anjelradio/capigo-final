import logging
from fastapi import HTTPException
from sqlmodel import Session

from app.modules.incidents.models import Incident, IncidentStatus

logger = logging.getLogger(__name__)


class IncidentStateTransitionService:
    CLIENT_CANCELLABLE_STATUSES = {
        IncidentStatus.PENDING,
        IncidentStatus.CLASSIFYING,
        IncidentStatus.CLASSIFIED,
        IncidentStatus.SEARCHING_SHOP,
        IncidentStatus.ASSIGNED,
        IncidentStatus.ON_THE_WAY,
        IncidentStatus.ARRIVED,
    }

    MECHANIC_STATUS_FLOW: dict[IncidentStatus, tuple[IncidentStatus, ...]] = {
        IncidentStatus.ASSIGNED: (IncidentStatus.ON_THE_WAY, IncidentStatus.CANCELLED),
        IncidentStatus.ON_THE_WAY: (IncidentStatus.ARRIVED, IncidentStatus.CANCELLED),
        IncidentStatus.ARRIVED: (IncidentStatus.COMPLETED, IncidentStatus.CANCELLED),
    }

    def __init__(self, db: Session):
        self.db = db

    @classmethod
    def ensure_client_can_cancel(cls, status: IncidentStatus) -> None:
        if status in cls.CLIENT_CANCELLABLE_STATUSES:
            return

        raise HTTPException(
            status_code=409,
            detail="No se puede cancelar el incidente en su estado actual",
        )

    @classmethod
    def ensure_mechanic_can_transition(
        cls,
        *,
        current: IncidentStatus,
        target: IncidentStatus,
    ) -> None:
        allowed_targets = cls.MECHANIC_STATUS_FLOW.get(current, ())
        if target in allowed_targets:
            return

        raise HTTPException(
            status_code=409,
            detail=f"No se puede cambiar de {current.value} a {target.value}",
        )

    def transition_incident(
        self,
        incident: Incident,
        target_status: IncidentStatus,
    ) -> None:
        """Centralized method to transition incident status and persist in session."""
        logger.info(
            "Transitioning incident_id=%s from=%s to=%s",
            incident.id,
            incident.status,
            target_status,
        )
        incident.status = target_status
        self.db.add(incident)
