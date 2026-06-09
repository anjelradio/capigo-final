import logging
from sqlmodel import Session

from app.modules.assignments.models import AssignmentStatus, RequestAssignment

logger = logging.getLogger(__name__)


class AssignmentStateTransitionService:
    def __init__(self, db: Session):
        self.db = db

    def transition_assignment(
        self,
        assignment: RequestAssignment,
        target_status: AssignmentStatus,
    ) -> None:
        """Centralized method to transition assignment status and persist in session."""
        logger.info(
            "Transitioning assignment_id=%s from=%s to=%s",
            assignment.id,
            assignment.status,
            target_status,
        )
        assignment.status = target_status
        self.db.add(assignment)
