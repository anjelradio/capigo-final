from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session

from app.modules.incidents.models import IncidentFeedback

from .incident_base_service import IncidentBaseService


class IncidentFeedbackService(IncidentBaseService):
    def __init__(self, db: Session):
        super().__init__(db)

    def submit_incident_feedback(
        self,
        *,
        user_id: UUID,
        incident_id: UUID,
        rating: int,
        comment: str | None,
    ) -> dict:
        self._validate_client_user(user_id)

        incident = self.incident.get_by_id_and_user(incident_id, user_id)
        if not incident:
            raise HTTPException(status_code=404, detail="Incidente no encontrado")

        if rating < 1 or rating > 5:
            raise HTTPException(
                status_code=400,
                detail="La calificacion debe estar en el rango de 1 a 5 estrellas",
            )

        existing_feedback = self.incident_feedback.get_by_incident_id(incident.id)
        if existing_feedback:
            raise HTTPException(
                status_code=409,
                detail="El incidente ya cuenta con una calificacion registrada",
            )

        feedback = IncidentFeedback(
            rating=rating,
            comment=" ".join((comment or "").split()) or None,
            incident_id=incident.id,
        )

        try:
            self.incident_feedback.create(feedback)
            self.db.commit()
            self.db.refresh(feedback)
        except Exception:
            self.db.rollback()
            raise

        return {
            "id": feedback.id,
            "incident_id": feedback.incident_id,
            "rating": feedback.rating,
            "comment": feedback.comment,
            "created_date": feedback.created_date,
        }

    def list_pending_feedback_reminders(self, user_id: UUID, *, limit: int = 8) -> dict:
        self._validate_client_user(user_id)

        incidents = self.incident.list_completed_without_feedback_by_user(user_id, limit=limit)
        if not incidents:
            return {"reminders": []}

        problem_ids = [incident.problem_id for incident in incidents if incident.problem_id is not None]
        problem_names_by_id: dict[UUID, str] = {}
        if problem_ids:
            problems = self.problem.list_active_by_ids(problem_ids)
            for problem in problems:
                problem_names_by_id[problem.id] = problem.name

        reminders = []
        for incident in incidents:
            reminders.append(
                {
                    "incident_id": incident.id,
                    "description": incident.description,
                    "problem_name": problem_names_by_id.get(incident.problem_id)
                    if incident.problem_id
                    else None,
                    "completed_at": incident.modified_date,
                }
            )

        return {"reminders": reminders}
