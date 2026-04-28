from uuid import UUID

from sqlmodel import Session, select

from app.modules.incidents.models import IncidentFeedback


class IncidentFeedbackRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, feedback: IncidentFeedback) -> IncidentFeedback:
        self.db.add(feedback)
        return feedback

    def get_by_incident_id(self, incident_id: UUID) -> IncidentFeedback | None:
        query = select(IncidentFeedback).where(
            IncidentFeedback.incident_id == incident_id,
            IncidentFeedback.state == True,
        )
        return self.db.exec(query).first()
