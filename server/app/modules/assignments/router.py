from uuid import UUID

from fastapi import APIRouter, Response, status

from app.dependencies.auth import CurrentUser, DBSession
from app.modules.assignments.schemas import (
    CandidateOfferEvaluationRequest,
    CandidateOfferEvaluationResponse,
    OwnerOfferAcceptRequest,
    OwnerOfferActionResponse,
    OwnerAssignmentsResponse,
    OwnerOfferHistoryResponse,
    CandidateShopSearchRequest,
    CandidateShopSearchResponse,
    OwnerOfferDetailRead,
    OwnerPendingOffersResponse,
    MechanicAssignmentRead,
    MechanicActiveAssignmentResponse,
    MechanicAssignmentStatusUpdateRequest,
    MechanicAssignmentLocationUpdateRequest,
    MechanicAssignmentActionResponse,
    MechanicAssignmentCompleteRequest,
    MechanicServiceListResponse,
    MechanicTodayStatsRead,
)
from app.modules.assignments.services import (
    AssignmentOrchestratorService,
    CandidateShopSearchService,
    MechanicAssignmentService,
    OfferEvaluationService,
    OwnerOfferService,
)
from app.modules.incidents.services import IncidentService
from app.modules.realtime.services import ShopOfferNotificationService

router = APIRouter(prefix="/assignments", tags=["Asignaciones"])


@router.post(
    "/incidents/{incident_id}/candidate-shops/search",
    response_model=CandidateShopSearchResponse,
    status_code=status.HTTP_200_OK,
)
def search_candidate_shops(
    db: DBSession,
    user: CurrentUser,
    incident_id: UUID,
    payload: CandidateShopSearchRequest,
):
    return CandidateShopSearchService(db).search_candidate_shops(
        incident_id=incident_id,
        user_id=user.id,
        radius_steps_km=payload.radius_steps_km,
        min_candidates=payload.min_candidates,
        limit_per_radius=payload.limit_per_radius,
    )


@router.post(
    "/incidents/{incident_id}/candidate-offers/evaluate",
    response_model=CandidateOfferEvaluationResponse,
    status_code=status.HTTP_200_OK,
)
def evaluate_candidate_offers(
    db: DBSession,
    user: CurrentUser,
    incident_id: UUID,
    payload: CandidateOfferEvaluationRequest,
):
    return OfferEvaluationService(db).evaluate_and_create_offers(
        incident_id=incident_id,
        user_id=user.id,
        radius_steps_km=payload.radius_steps_km,
        min_candidates=payload.min_candidates,
        limit_per_radius=payload.limit_per_radius,
        base_fee_bob=payload.base_fee_bob,
        price_per_km_bob=payload.price_per_km_bob,
    )


@router.post(
    "/incidents/{incident_id}/orchestrate",
    status_code=status.HTTP_200_OK,
)
def orchestrate_incident_assignment(db: DBSession, user: CurrentUser, incident_id: UUID):
    IncidentService(db).get_incident_by_id(user.id, incident_id)
    return AssignmentOrchestratorService(db).run_after_classification(incident_id)


@router.post(
    "/incidents/{incident_id}/queue/notify-next",
    status_code=status.HTTP_200_OK,
)
def notify_next_offer_in_queue(db: DBSession, user: CurrentUser, incident_id: UUID):
    IncidentService(db).get_incident_by_id(user.id, incident_id)
    return ShopOfferNotificationService(db).notify_next_offer_in_incident_queue_sync(
        incident_id
    )


@router.get(
    "/me/offers/pending",
    response_model=OwnerPendingOffersResponse,
    status_code=status.HTTP_200_OK,
)
def list_my_pending_offers(db: DBSession, user: CurrentUser):
    return OwnerOfferService(db).list_my_pending_offers(user_id=user.id)


@router.get(
    "/me/offers/history",
    response_model=OwnerOfferHistoryResponse,
    status_code=status.HTTP_200_OK,
)
def list_my_offer_history(db: DBSession, user: CurrentUser):
    return OwnerOfferService(db).list_my_offer_history(user_id=user.id)


@router.get(
    "/me/assignments",
    response_model=OwnerAssignmentsResponse,
    status_code=status.HTTP_200_OK,
)
def list_my_assignments(db: DBSession, user: CurrentUser):
    return OwnerOfferService(db).list_my_assignments(user_id=user.id)


@router.get(
    "/{assignment_id}/offer-detail",
    response_model=OwnerOfferDetailRead,
    status_code=status.HTTP_200_OK,
)
def get_my_offer_detail(db: DBSession, user: CurrentUser, assignment_id: UUID):
    return OwnerOfferService(db).get_my_offer_detail(
        user_id=user.id,
        assignment_id=assignment_id,
    )


@router.get(
    "/{assignment_id}/service-report/pdf",
    status_code=status.HTTP_200_OK,
)
def download_my_service_report_pdf(db: DBSession, user: CurrentUser, assignment_id: UUID):
    pdf_bytes, filename = OwnerOfferService(db).download_my_assignment_report_pdf(
        user_id=user.id,
        assignment_id=assignment_id,
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.post(
    "/{assignment_id}/accept",
    response_model=OwnerOfferActionResponse,
    status_code=status.HTTP_200_OK,
)
def accept_my_offer(
    db: DBSession,
    user: CurrentUser,
    assignment_id: UUID,
    payload: OwnerOfferAcceptRequest,
):
    return OwnerOfferService(db).accept_my_offer(
        user_id=user.id,
        assignment_id=assignment_id,
        mechanic_id=payload.mechanic_id,
    )


@router.post(
    "/{assignment_id}/reject",
    response_model=OwnerOfferActionResponse,
    status_code=status.HTTP_200_OK,
)
def reject_my_offer(db: DBSession, user: CurrentUser, assignment_id: UUID):
    return OwnerOfferService(db).reject_my_offer(
        user_id=user.id,
        assignment_id=assignment_id,
    )


@router.get(
    "/me/mechanic/active",
    response_model=MechanicActiveAssignmentResponse,
    status_code=status.HTTP_200_OK,
)
def get_my_active_assignment(db: DBSession, user: CurrentUser):
    return MechanicAssignmentService(db).get_my_active_assignment(user_id=user.id)


@router.get(
    "/me/mechanic/assignments/{assignment_id}",
    response_model=MechanicAssignmentRead,
    status_code=status.HTTP_200_OK,
)
def get_my_assignment_detail(db: DBSession, user: CurrentUser, assignment_id: UUID):
    return MechanicAssignmentService(db).get_my_assignment_detail(
        user_id=user.id,
        assignment_id=assignment_id,
    )


@router.get(
    "/me/mechanic/stats/today",
    response_model=MechanicTodayStatsRead,
    status_code=status.HTTP_200_OK,
)
def get_my_today_stats(db: DBSession, user: CurrentUser):
    return MechanicAssignmentService(db).get_my_today_stats(user_id=user.id)


@router.get(
    "/me/mechanic/services/completed",
    response_model=MechanicServiceListResponse,
    status_code=status.HTTP_200_OK,
)
def list_my_completed_services(db: DBSession, user: CurrentUser):
    return MechanicAssignmentService(db).list_my_completed_services(user_id=user.id)


@router.get(
    "/me/mechanic/services/history",
    response_model=MechanicServiceListResponse,
    status_code=status.HTTP_200_OK,
)
def list_my_service_history(db: DBSession, user: CurrentUser):
    return MechanicAssignmentService(db).list_my_service_history(user_id=user.id)


@router.get(
    "/me/mechanic/incidents/{incident_id}/detail",
    response_model=MechanicAssignmentRead,
    status_code=status.HTTP_200_OK,
)
def get_my_incident_detail(db: DBSession, user: CurrentUser, incident_id: UUID):
    return MechanicAssignmentService(db).get_my_incident_detail(
        user_id=user.id,
        incident_id=incident_id,
    )


@router.post(
    "/me/mechanic/assignments/{assignment_id}/status",
    response_model=MechanicAssignmentActionResponse,
    status_code=status.HTTP_200_OK,
)
def update_my_assignment_status(
    db: DBSession,
    user: CurrentUser,
    assignment_id: UUID,
    payload: MechanicAssignmentStatusUpdateRequest,
):
    return MechanicAssignmentService(db).update_my_assignment_status(
        user_id=user.id,
        assignment_id=assignment_id,
        target_status=payload.status,
    )


@router.post(
    "/me/mechanic/assignments/{assignment_id}/complete",
    response_model=MechanicAssignmentActionResponse,
    status_code=status.HTTP_200_OK,
)
def complete_my_assignment(
    db: DBSession,
    user: CurrentUser,
    assignment_id: UUID,
    payload: MechanicAssignmentCompleteRequest,
):
    return MechanicAssignmentService(db).complete_my_assignment(
        user_id=user.id,
        assignment_id=assignment_id,
        description=payload.description,
        labor_price=payload.labor_price,
    )


@router.post(
    "/me/mechanic/assignments/{assignment_id}/location",
    response_model=MechanicAssignmentActionResponse,
    status_code=status.HTTP_200_OK,
)
def update_my_assignment_location(
    db: DBSession,
    user: CurrentUser,
    assignment_id: UUID,
    payload: MechanicAssignmentLocationUpdateRequest,
):
    return MechanicAssignmentService(db).update_my_assignment_location(
        user_id=user.id,
        assignment_id=assignment_id,
        latitude=payload.latitude,
        longitude=payload.longitude,
        recorded_at=payload.recorded_at,
    )
