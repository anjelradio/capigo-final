from uuid import UUID

from sqlmodel import Session, select

from app.modules.incidents.models import Evidence


class EvidenceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, evidence: Evidence) -> Evidence:
        self.db.add(evidence)
        return evidence

    def list_by_incident_id(self, incident_id: UUID) -> list[Evidence]:
        query = (
            select(Evidence)
            .where(
                Evidence.incident_id == incident_id,
                Evidence.state == True,
            )
            .order_by(Evidence.created_date.asc())
        )
        return list(self.db.exec(query).all())
