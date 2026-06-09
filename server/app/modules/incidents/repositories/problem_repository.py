from uuid import UUID

from sqlmodel import Session, select

from app.modules.incidents.models import Problem


class ProblemRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_active_by_id(self, problem_id: UUID) -> Problem | None:
        query = select(Problem).where(
            Problem.id == problem_id,
            Problem.state == True,
        )
        return self.db.exec(query).first()

    def list_active_by_ids(self, problem_ids: list[UUID]) -> list[Problem]:
        if not problem_ids:
            return []
        query = select(Problem).where(
            Problem.id.in_(tuple(problem_ids)),
            Problem.state == True,
        )
        return list(self.db.exec(query).all())
