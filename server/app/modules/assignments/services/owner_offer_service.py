from uuid import UUID
from sqlmodel import Session

from .base_service import AssignmentBaseService
from .owner_offer_management_service import OwnerOfferManagementService
from .owner_assignment_query_service import OwnerAssignmentQueryService


class OwnerOfferService(AssignmentBaseService):
    def __init__(self, db: Session):
        super().__init__(db)
        self._management = OwnerOfferManagementService(db)
        self._query = OwnerAssignmentQueryService(db)

    def list_my_pending_offers(self, *, user_id: UUID) -> dict:
        return self._management.list_my_pending_offers(user_id=user_id)

    def get_my_offer_detail(self, *, user_id: UUID, assignment_id: UUID) -> dict:
        return self._management.get_my_offer_detail(user_id=user_id, assignment_id=assignment_id)

    def list_my_offer_history(self, *, user_id: UUID) -> dict:
        return self._query.list_my_offer_history(user_id=user_id)

    def list_my_assignments(self, *, user_id: UUID) -> dict:
        return self._query.list_my_assignments(user_id=user_id)

    def download_my_assignment_report_pdf(self, *, user_id: UUID, assignment_id: UUID) -> tuple[bytes, str]:
        return self._query.download_my_assignment_report_pdf(user_id=user_id, assignment_id=assignment_id)

    def reject_my_offer(self, *, user_id: UUID, assignment_id: UUID) -> dict:
        return self._management.reject_my_offer(user_id=user_id, assignment_id=assignment_id)

    def submit_my_offer(
        self,
        *,
        user_id: UUID,
        assignment_id: UUID,
        mechanic_id: UUID,
        quoted_price: float,
    ) -> dict:
        return self._management.submit_my_offer(
            user_id=user_id,
            assignment_id=assignment_id,
            mechanic_id=mechanic_id,
            quoted_price=quoted_price,
        )
