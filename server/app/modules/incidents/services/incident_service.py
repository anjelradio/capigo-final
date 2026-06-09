from uuid import UUID
from fastapi import UploadFile
from sqlmodel import Session

from .incident_base_service import IncidentBaseService
from .incident_creation_service import IncidentCreationService
from .incident_query_service import IncidentQueryService
from .incident_feedback_service import IncidentFeedbackService


class IncidentService(IncidentBaseService):
    def __init__(self, db: Session):
        super().__init__(db)
        self._creation = IncidentCreationService(db)
        self._query = IncidentQueryService(db)
        self._feedback = IncidentFeedbackService(db)

    def create_incident(
        self,
        user_id: UUID,
        vehicle_id: UUID,
        latitude: float,
        longitude: float,
        description: str | None,
        audio: UploadFile | None,
        photos: list[UploadFile],
        client_request_id: str | None = None,
    ) -> dict:
        return self._creation.create_incident(
            user_id=user_id,
            vehicle_id=vehicle_id,
            latitude=latitude,
            longitude=longitude,
            description=description,
            audio=audio,
            photos=photos,
            client_request_id=client_request_id,
        )

    def get_incident_by_id(self, user_id: UUID, incident_id: UUID) -> dict:
        return self._query.get_incident_by_id(user_id=user_id, incident_id=incident_id)

    def list_my_incidents(self, user_id: UUID) -> list[dict]:
        return self._query.list_my_incidents(user_id=user_id)

    def cancel_my_incident(self, *, user_id: UUID, incident_id: UUID) -> dict:
        return self._creation.cancel_my_incident(user_id=user_id, incident_id=incident_id)

    def get_active_incident_detail(self, user_id: UUID) -> dict | None:
        return self._query.get_active_incident_detail(user_id=user_id)

    def submit_incident_feedback(
        self,
        *,
        user_id: UUID,
        incident_id: UUID,
        rating: int,
        comment: str | None,
    ) -> dict:
        return self._feedback.submit_incident_feedback(
            user_id=user_id,
            incident_id=incident_id,
            rating=rating,
            comment=comment,
        )

    def list_pending_feedback_reminders(self, user_id: UUID, *, limit: int = 8) -> dict:
        return self._feedback.list_pending_feedback_reminders(user_id=user_id, limit=limit)

    def list_completed_services(self, user_id: UUID) -> dict:
        return self._query.list_completed_services(user_id=user_id)

    def list_service_history(self, user_id: UUID) -> dict:
        return self._query.list_service_history(user_id=user_id)

    def get_client_service_detail(self, *, user_id: UUID, incident_id: UUID) -> dict:
        return self._query.get_client_service_detail(user_id=user_id, incident_id=incident_id)
