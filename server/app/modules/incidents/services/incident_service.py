import hashlib
import logging
import time
from uuid import UUID

import httpx
from fastapi import HTTPException, UploadFile
from sqlmodel import Session

from app.core.config import settings
from app.modules.incidents.models import Evidence, Incident, IncidentPriority, IncidentStatus
from app.modules.incidents.repositories import EvidenceRepository, IncidentRepository
from app.modules.user.models import UserRole
from app.modules.user.repositories import UserRepository, VehicleRepository

logger = logging.getLogger(__name__)


class IncidentService:
    def __init__(self, db: Session):
        self.db = db
        self.user = UserRepository(db)
        self.vehicle = VehicleRepository(db)
        self.incident = IncidentRepository(db)
        self.evidence = EvidenceRepository(db)

    def create_incident(
        self,
        user_id: UUID,
        vehicle_id: UUID,
        latitude: float,
        longitude: float,
        description: str | None,
        audio: UploadFile | None,
        photos: list[UploadFile],
    ) -> dict:
        self._validate_client_user(user_id)
        self._ensure_no_active_incident(user_id)
        self._validate_vehicle_owner(user_id, vehicle_id)

        if not photos:
            raise HTTPException(
                status_code=400,
                detail="Debes adjuntar al menos una imagen del incidente",
            )

        final_description = self._resolve_incident_description(description, audio)

        incident = Incident(
            description=final_description,
            status=IncidentStatus.PENDING,
            priority=IncidentPriority.MEDIUM,
            latitude=latitude,
            longitude=longitude,
            user_id=user_id,
            vehicle_id=vehicle_id,
        )

        try:
            self.incident.create(incident)
            self.db.flush()

            uploaded_urls = self._upload_incident_photos(incident.id, photos)
            for url in uploaded_urls:
                self.evidence.create(
                    Evidence(
                        incident_id=incident.id,
                        url=url,
                    )
                )

            self.db.commit()
            self.db.refresh(incident)
        except Exception:
            self.db.rollback()
            raise

        evidences = self.evidence.list_by_incident_id(incident.id)
        self._emit_incident_realtime_event(
            incident_id=incident.id,
            event_type="incident.status.changed",
            payload={
                "status": incident.status,
                "description": "Incidente creado y pendiente de clasificacion",
            },
            status=incident.status,
        )
        return self._to_incident_read(incident, evidences)

    def get_incident_by_id(self, user_id: UUID, incident_id: UUID) -> dict:
        self._validate_client_user(user_id)
        incident = self.incident.get_by_id_and_user(incident_id, user_id)
        if not incident:
            raise HTTPException(status_code=404, detail="Incidente no encontrado")

        evidences = self.evidence.list_by_incident_id(incident.id)
        return self._to_incident_read(incident, evidences)

    def list_my_incidents(self, user_id: UUID) -> list[dict]:
        self._validate_client_user(user_id)
        incidents = self.incident.list_by_user(user_id)

        response: list[dict] = []
        for incident in incidents:
            evidences = self.evidence.list_by_incident_id(incident.id)
            response.append(self._to_incident_read(incident, evidences))

        return response

    def get_active_incident_detail(self, user_id: UUID) -> dict | None:
        self._validate_client_user(user_id)

        incident = self.incident.get_latest_active_by_user(user_id)
        if not incident:
            return None

        vehicle_row = self.vehicle.get_by_id_and_user_with_type(incident.vehicle_id, user_id)
        if not vehicle_row:
            raise HTTPException(
                status_code=404,
                detail="No se encontro el vehiculo vinculado al incidente activo",
            )

        vehicle, vehicle_type = vehicle_row
        evidences = self.evidence.list_by_incident_id(incident.id)

        return {
            "incident": {
                "id": incident.id,
                "description": incident.description,
                "status": incident.status,
                "priority": incident.priority,
                "latitude": incident.latitude,
                "longitude": incident.longitude,
                "delivery_price": incident.delivery_price,
                "distance_km": incident.distance_km,
                "created_date": incident.created_date,
            },
            "vehicle": {
                "id": vehicle.id,
                "make": vehicle.make,
                "model": vehicle.model,
                "plate": vehicle.plate,
                "color": vehicle.color,
                "year": vehicle.year,
                "type": {
                    "id": vehicle_type.id,
                    "name": vehicle_type.name,
                },
            },
            "evidences": [
                {
                    "id": evidence.id,
                    "url": evidence.url,
                }
                for evidence in evidences
            ],
            "assignment": None,
        }

    def _validate_client_user(self, user_id: UUID) -> None:
        user = self.user.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        if user.role != UserRole.CLIENT:
            raise HTTPException(
                status_code=403,
                detail="Solo usuarios client pueden crear incidentes",
            )

    def _validate_vehicle_owner(self, user_id: UUID, vehicle_id: UUID) -> None:
        vehicle = self.vehicle.get_active_by_id_and_user(vehicle_id, user_id)
        if not vehicle:
            raise HTTPException(
                status_code=400,
                detail="El vehiculo seleccionado no pertenece al usuario",
            )

    def _ensure_no_active_incident(self, user_id: UUID) -> None:
        active_incident = self.incident.get_latest_active_by_user(user_id)
        if active_incident:
            raise HTTPException(
                status_code=409,
                detail="Ya tienes un servicio activo",
            )

    def _resolve_incident_description(
        self,
        description: str | None,
        audio: UploadFile | None,
    ) -> str | None:
        normalized_description = " ".join((description or "").split())
        if normalized_description:
            return normalized_description

        if audio:
            return None

        raise HTTPException(
            status_code=400,
            detail="Debes enviar descripcion en texto o audio del incidente",
        )

    def _upload_incident_photos(
        self,
        incident_id: UUID,
        photos: list[UploadFile],
    ) -> list[str]:
        uploaded_urls: list[str] = []
        for photo in photos:
            if not str(photo.content_type or "").startswith("image/"):
                raise HTTPException(
                    status_code=400,
                    detail="Solo se permiten imagenes en evidencias del incidente",
                )

            photo_bytes = photo.file.read()
            if not photo_bytes:
                raise HTTPException(status_code=400, detail="Una imagen enviada esta vacia")

            uploaded_urls.append(
                self._upload_to_cloudinary(
                    incident_id=incident_id,
                    file_name=photo.filename or "photo.jpg",
                    content_type=photo.content_type or "image/jpeg",
                    content=photo_bytes,
                )
            )

        return uploaded_urls

    def _upload_to_cloudinary(
        self,
        incident_id: UUID,
        file_name: str,
        content_type: str,
        content: bytes,
    ) -> str:
        missing_vars: list[str] = []
        if not settings.CLOUDINARY_CLOUD_NAME:
            missing_vars.append("CLOUDINARY_CLOUD_NAME")
        if not settings.CLOUDINARY_API_KEY:
            missing_vars.append("CLOUDINARY_API_KEY")
        if not settings.CLOUDINARY_API_SECRET:
            missing_vars.append("CLOUDINARY_API_SECRET")

        if missing_vars:
            raise HTTPException(
                status_code=500,
                detail=(
                    "Cloudinary no esta configurado correctamente. "
                    f"Faltan: {', '.join(missing_vars)}"
                ),
            )

        timestamp = int(time.time())
        folder = f"apico/evidences/{incident_id}"
        public_id = hashlib.sha1(content).hexdigest()
        params_to_sign = (
            f"folder={folder}"
            f"&public_id={public_id}"
            f"&timestamp={timestamp}{settings.CLOUDINARY_API_SECRET}"
        )
        signature = hashlib.sha1(params_to_sign.encode("utf-8")).hexdigest()

        endpoint = (
            f"https://api.cloudinary.com/v1_1/{settings.CLOUDINARY_CLOUD_NAME}/image/upload"
        )
        files = {
            "file": (file_name, content, content_type),
        }
        data = {
            "api_key": settings.CLOUDINARY_API_KEY,
            "timestamp": str(timestamp),
            "folder": folder,
            "public_id": public_id,
            "signature": signature,
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(endpoint, data=data, files=files)
                response.raise_for_status()
            payload = response.json()
        except httpx.HTTPStatusError as error:
            cloudinary_error = ""
            try:
                cloudinary_payload = error.response.json()
                cloudinary_error = str(cloudinary_payload.get("error", {}).get("message", ""))
            except Exception:
                cloudinary_error = error.response.text

            cloudinary_error = cloudinary_error.strip() or "Sin detalle"
            raise HTTPException(
                status_code=502,
                detail=(
                    "No fue posible subir una imagen a Cloudinary. "
                    f"status={error.response.status_code} detail={cloudinary_error}"
                ),
            )
        except Exception:
            raise HTTPException(
                status_code=502,
                detail="No fue posible subir una imagen a Cloudinary",
            )

        secure_url = str(payload.get("secure_url") or "").strip()
        if not secure_url:
            raise HTTPException(
                status_code=502,
                detail="Cloudinary no devolvio una URL valida",
            )

        return secure_url

    def _to_incident_read(self, incident: Incident, evidences: list[Evidence]) -> dict:
        return {
            "id": incident.id,
            "description": incident.description,
            "status": incident.status,
            "priority": incident.priority,
            "latitude": incident.latitude,
            "longitude": incident.longitude,
            "vehicle_id": incident.vehicle_id,
            "problem_id": incident.problem_id,
            "created_date": incident.created_date,
            "evidences": [
                {
                    "id": evidence.id,
                    "url": evidence.url,
                }
                for evidence in evidences
            ],
        }

    def _emit_incident_realtime_event(
        self,
        *,
        incident_id: UUID,
        event_type: str,
        payload: dict,
        status: str | None = None,
    ) -> None:
        try:
            from app.modules.realtime.services.incident_realtime_service import (
                IncidentRealtimeService,
            )

            IncidentRealtimeService(self.db).publish_incident_event_sync(
                incident_id=incident_id,
                event_type=event_type,
                payload=payload,
                status=status,
            )
        except Exception as error:
            try:
                self.db.rollback()
            except Exception:
                pass
            logger.warning(
                "No se pudo emitir evento realtime incident_id=%s type=%s error=%s",
                incident_id,
                event_type,
                error,
            )
