from fastapi import HTTPException

from app.modules.incidents.models import IncidentStatus


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
