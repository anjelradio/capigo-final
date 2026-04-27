from uuid import UUID

from sqlmodel import Session, select

from app.modules.incidents.models import Incident, IncidentStatus


class IncidentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, incident: Incident) -> Incident:
        self.db.add(incident)
        return incident

    def get_by_id(self, incident_id: UUID) -> Incident | None:
        query = select(Incident).where(
            Incident.id == incident_id,
            Incident.state == True,
        )
        return self.db.exec(query).first()

    def get_by_id_and_user(self, incident_id: UUID, user_id: UUID) -> Incident | None:
        query = select(Incident).where(
            Incident.id == incident_id,
            Incident.user_id == user_id,
            Incident.state == True,
        )
        return self.db.exec(query).first()

    def list_by_user(self, user_id: UUID) -> list[Incident]:
        query = (
            select(Incident)
            .where(
                Incident.user_id == user_id,
                Incident.state == True,
            )
            .order_by(Incident.created_date.desc())
        )
        return list(self.db.exec(query).all())

    def get_latest_active_by_user(self, user_id: UUID) -> Incident | None:
        active_statuses = (
            IncidentStatus.PENDING,
            IncidentStatus.CLASSIFYING,
            IncidentStatus.CLASSIFIED,
            IncidentStatus.SEARCHING_SHOP,
            IncidentStatus.ASSIGNED,
            IncidentStatus.ON_THE_WAY,
            IncidentStatus.ARRIVED,
        )

        query = (
            select(Incident)
            .where(
                Incident.user_id == user_id,
                Incident.state == True,
                Incident.status.in_(active_statuses),
            )
            .order_by(Incident.created_date.desc())
        )
        return self.db.exec(query).first()
