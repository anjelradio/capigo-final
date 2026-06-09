from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session

from app.modules.assignments.models import AssignmentStatus

from .assignment_report_pdf_service import AssignmentReportPdfService
from .owner_base_service import OwnerBaseService


class OwnerAssignmentQueryService(OwnerBaseService):
    def __init__(self, db: Session):
        super().__init__(db)
        self.report_pdf = AssignmentReportPdfService(db)

    def list_my_offer_history(self, *, user_id: UUID) -> dict:
        shop_id = self._resolve_owner_shop_id(user_id)
        now_utc = datetime.now(UTC)
        assignments = self.request_assignment.list_history_by_shop(shop_id, now_utc)

        offers: list[dict] = []
        for assignment in assignments:
            payload = self.request_assignment.get_offer_notification_payload(assignment.id)
            if not payload:
                continue

            offers.append(
                {
                    "assignment_id": assignment.id,
                    "incident_id": assignment.incident_id,
                    "problem_id": payload.get("problem_id"),
                    "problem_name": payload.get("problem_name"),
                    "incident_description": payload.get("incident_description"),
                    "distance_km": payload.get("distance_km"),
                    "delivery_price": payload.get("delivery_price"),
                    "quoted_price": float(assignment.quoted_price)
                    if assignment.quoted_price is not None
                    else None,
                    "status": self._resolve_history_status(assignment.status, assignment.expires_at),
                    "notified_at": assignment.notified_at,
                    "expires_at": assignment.expires_at,
                    "responded_at": assignment.responded_at,
                }
            )

        return {"offers": offers}

    def list_my_assignments(self, *, user_id: UUID) -> dict:
        shop_id = self._resolve_owner_shop_id(user_id)
        assignments = self.request_assignment.list_assignments_for_shop(shop_id)

        items: list[dict] = []
        for assignment in assignments:
            payload = self.request_assignment.get_offer_notification_payload(assignment.id)
            if not payload:
                continue

            items.append(
                {
                    "assignment_id": assignment.id,
                    "incident_id": assignment.incident_id,
                    "problem_id": payload.get("problem_id"),
                    "problem_name": payload.get("problem_name"),
                    "incident_description": payload.get("incident_description"),
                    "distance_km": payload.get("distance_km"),
                    "delivery_price": payload.get("delivery_price"),
                    "quoted_price": float(assignment.quoted_price)
                    if assignment.quoted_price is not None
                    else None,
                    "status": assignment.status.value,
                    "mechanic_name": self.request_assignment.get_mechanic_full_name(
                        assignment.mechanic_id
                    ),
                    "created_at": assignment.created_date,
                }
            )

        return {"assignments": items}

    def download_my_assignment_report_pdf(self, *, user_id: UUID, assignment_id: UUID) -> tuple[bytes, str]:
        shop_id = self._resolve_owner_shop_id(user_id)
        assignment = self.request_assignment.get_by_id(assignment_id)
        if not assignment or assignment.repair_shop_id != shop_id:
            raise HTTPException(status_code=404, detail="Asignacion no encontrada")

        payload = self.request_assignment.get_service_report_payload(assignment.id)
        if not payload:
            raise HTTPException(status_code=404, detail="No se encontro informacion de reporte")

        report_id = payload.get("report_id")
        if not report_id:
            raise HTTPException(
                status_code=409,
                detail="El incidente aun no tiene un reporte final del mecanico",
            )

        return self.report_pdf.build_report_pdf(payload=payload)

    def _resolve_history_status(
        self, status: AssignmentStatus, expires_at: datetime | None
    ) -> str:
        now_utc_naive = datetime.utcnow()
        expires_at_naive = self._to_utc_naive(expires_at)

        if (
            status == AssignmentStatus.PENDING
            and expires_at_naive is not None
            and expires_at_naive <= now_utc_naive
        ):
            return AssignmentStatus.EXPIRED.value

        return status.value

    def _to_utc_naive(self, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value
        return value.astimezone(UTC).replace(tzinfo=None)
