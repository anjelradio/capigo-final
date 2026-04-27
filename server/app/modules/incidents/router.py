import base64
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, File, Form, UploadFile, status

from app.dependencies.auth import CurrentUser, DBSession
from app.modules.ai.services import IncidentClassificationService
from app.modules.incidents.schemas import (
    ActiveIncidentDetailRead,
    IncidentCreateResponse,
    IncidentRead,
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
    "/me/active",
    response_model=ActiveIncidentDetailRead | None,
    status_code=status.HTTP_200_OK,
)
def get_active_incident_detail(db: DBSession, user: CurrentUser):
    return IncidentService(db).get_active_incident_detail(user.id)


@router.get("/{incident_id}", response_model=IncidentRead, status_code=status.HTTP_200_OK)
def get_incident_by_id(db: DBSession, incident_id: UUID, user: CurrentUser):
    return IncidentService(db).get_incident_by_id(user.id, incident_id)


@router.post(
    "/{incident_id}/classify",
    status_code=status.HTTP_200_OK,
)
def classify_incident_now(db: DBSession, incident_id: UUID, user: CurrentUser):
    IncidentService(db).get_incident_by_id(user.id, incident_id)
    return IncidentClassificationService(db).classify_incident(incident_id)
