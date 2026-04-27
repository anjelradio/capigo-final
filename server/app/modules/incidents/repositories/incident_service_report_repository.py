from uuid import UUID

from sqlmodel import Session, select

from app.modules.incidents.models import IncidentServiceReport


class IncidentServiceReportRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, report: IncidentServiceReport) -> IncidentServiceReport:
        self.db.add(report)
        return report

    def get_by_incident_id(self, incident_id: UUID) -> IncidentServiceReport | None:
        query = select(IncidentServiceReport).where(
            IncidentServiceReport.incident_id == incident_id,
            IncidentServiceReport.state == True,
        )
        return self.db.exec(query).first()
