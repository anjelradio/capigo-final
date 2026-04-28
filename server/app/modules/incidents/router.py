import base64
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, File, Form, UploadFile, status

from app.dependencies.auth import CurrentUser, DBSession
from app.modules.ai.services import IncidentClassificationService
from app.modules.incidents.schemas import (
    ActiveIncidentDetailRead,
    IncidentActionResponse,
    ClientServiceDetailRead,
    ClientServiceListResponse,
    IncidentCreateResponse,
    IncidentFeedbackCreateRequest,
    IncidentFeedbackRead,
    IncidentRead,
    PendingIncidentFeedbackListResponse,
)
from app.modules.incidents.services import IncidentService

router = APIRouter(prefix="/incidents", tags=["Incidentes"])


@router.post(
    "",
    response_model=IncidentCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_incident(
    db: DBSession,
    background_tasks: BackgroundTasks,
    user: CurrentUser,
    vehicle_id: UUID = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    description: str | None = Form(default=None),
    audio: UploadFile | None = File(default=None),
    photos: list[UploadFile] = File(...),
):
    incident = IncidentService(db).create_incident(
        user_id=user.id,
        vehicle_id=vehicle_id,
        latitude=latitude,
        longitude=longitude,
        description=description,
        audio=audio,
        photos=photos,
    )

    audio_payload: dict | None = None
    if audio is not None:
        audio_bytes = audio.file.read()
        if audio_bytes:
            audio_payload = {
                "filename": audio.filename or "incident_audio.m4a",
                "mime_type": audio.content_type or "audio/m4a",
                "data_base64": base64.b64encode(audio_bytes).decode("utf-8"),
            }

    background_tasks.add_task(
        IncidentClassificationService.classify_incident_background,
        incident["id"],
        audio_payload,
    )

    return {"incident": incident}


@router.get("/me", response_model=list[IncidentRead], status_code=status.HTTP_200_OK)
def list_my_incidents(db: DBSession, user: CurrentUser):
    return IncidentService(db).list_my_incidents(user.id)


@router.get(
    "/me/services/completed",
    response_model=ClientServiceListResponse,
    status_code=status.HTTP_200_OK,
)
def list_my_completed_services(db: DBSession, user: CurrentUser):
    return IncidentService(db).list_completed_services(user.id)


@router.get(
    "/me/services/history",
    response_model=ClientServiceListResponse,
    status_code=status.HTTP_200_OK,
)
def list_my_service_history(db: DBSession, user: CurrentUser):
    return IncidentService(db).list_service_history(user.id)


@router.get(
    "/me/services/{incident_id}/detail",
    response_model=ClientServiceDetailRead,
    status_code=status.HTTP_200_OK,
)
def get_my_service_detail(db: DBSession, user: CurrentUser, incident_id: UUID):
    return IncidentService(db).get_client_service_detail(
        user_id=user.id,
        incident_id=incident_id,
    )


@router.get(
    "/me/active",
    response_model=ActiveIncidentDetailRead | None,
    status_code=status.HTTP_200_OK,
)
def get_active_incident_detail(db: DBSession, user: CurrentUser):
    return IncidentService(db).get_active_incident_detail(user.id)


@router.get(
    "/me/feedback/pending",
    response_model=PendingIncidentFeedbackListResponse,
    status_code=status.HTTP_200_OK,
)
def list_my_pending_feedback_reminders(db: DBSession, user: CurrentUser):
    return IncidentService(db).list_pending_feedback_reminders(user.id)


@router.get("/{incident_id}", response_model=IncidentRead, status_code=status.HTTP_200_OK)
def get_incident_by_id(db: DBSession, incident_id: UUID, user: CurrentUser):
    return IncidentService(db).get_incident_by_id(user.id, incident_id)


@router.post(
    "/{incident_id}/cancel",
    response_model=IncidentActionResponse,
    status_code=status.HTTP_200_OK,
)
def cancel_my_incident(db: DBSession, incident_id: UUID, user: CurrentUser):
    return IncidentService(db).cancel_my_incident(
        user_id=user.id,
        incident_id=incident_id,
    )


@router.post(
    "/{incident_id}/feedback",
    response_model=IncidentFeedbackRead,
    status_code=status.HTTP_201_CREATED,
)
def submit_incident_feedback(
    db: DBSession,
    incident_id: UUID,
    user: CurrentUser,
    payload: IncidentFeedbackCreateRequest,
):
    return IncidentService(db).submit_incident_feedback(
        user_id=user.id,
        incident_id=incident_id,
        rating=payload.rating,
        comment=payload.comment,
    )


@router.post(
    "/{incident_id}/classify",
    status_code=status.HTTP_200_OK,
)
def classify_incident_now(db: DBSession, incident_id: UUID, user: CurrentUser):
    IncidentService(db).get_incident_by_id(user.id, incident_id)
    return IncidentClassificationService(db).classify_incident(incident_id)
