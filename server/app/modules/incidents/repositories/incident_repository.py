from uuid import UUID

from sqlmodel import Session, select

from app.modules.incidents.models import Incident, IncidentFeedback, IncidentStatus, Problem
from app.modules.user.models import Vehicle


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

    def get_by_user_and_client_request_id(self, *, user_id: UUID, client_request_id: str) -> Incident | None:
        query = select(Incident).where(
            Incident.user_id == user_id,
            Incident.client_request_id == client_request_id,
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
            IncidentStatus.PAYMENT_PENDING,
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

    def list_completed_without_feedback_by_user(
        self,
        user_id: UUID,
        *,
        limit: int = 10,
    ) -> list[Incident]:
        query = (
            select(Incident)
            .outerjoin(
                IncidentFeedback,
                (IncidentFeedback.incident_id == Incident.id)
                & (IncidentFeedback.state == True),
            )
            .where(
                Incident.user_id == user_id,
                Incident.state == True,
                Incident.status == IncidentStatus.COMPLETED,
                IncidentFeedback.id.is_(None),
            )
            .order_by(Incident.modified_date.desc(), Incident.created_date.desc())
            .limit(limit)
        )
        return list(self.db.exec(query).all())

    def list_service_cards_by_user(self, user_id: UUID, *, only_completed: bool) -> list[dict]:
        query = (
            select(
                Incident.id,
                Incident.description,
                Incident.status,
                Incident.created_date,
                Incident.modified_date,
                Problem.name,
                Vehicle.plate,
            )
            .outerjoin(Problem, Problem.id == Incident.problem_id)
            .outerjoin(Vehicle, Vehicle.id == Incident.vehicle_id)
            .where(
                Incident.user_id == user_id,
                Incident.state == True,
            )
            .order_by(Incident.modified_date.desc(), Incident.created_date.desc())
        )

        if only_completed:
            query = query.where(Incident.status == IncidentStatus.COMPLETED)

        rows = self.db.exec(query).all()

        return [
            {
                "incident_id": row[0],
                "description": row[1],
                "status": row[2].value if hasattr(row[2], "value") else str(row[2]),
                "created_date": row[3],
                "updated_date": row[4],
                "problem_name": row[5],
                "vehicle_plate": row[6],
            }
            for row in rows
        ]
