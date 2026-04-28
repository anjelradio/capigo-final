import hashlib
import logging
import time
from datetime import UTC, datetime
from uuid import UUID

import httpx
from fastapi import HTTPException, UploadFile
from sqlmodel import Session, select

from app.core.config import settings
from app.modules.assignments.models import AssignmentStatus
from app.modules.assignments.repositories import RequestAssignmentRepository
from app.modules.incidents.models import (
    Evidence,
    Incident,
    IncidentFeedback,
    IncidentPriority,
    Problem,
    IncidentStatus,
)
from app.modules.incidents.repositories import (
    EvidenceRepository,
    IncidentFeedbackRepository,
    IncidentRepository,
    IncidentServiceReportRepository,
)
from app.modules.repair_shop.services.shop_profile_service import ShopProfileService
from app.modules.repair_shop.repositories import ShopMechanicRepository
from app.modules.repair_shop.repositories import RepairShopRepository
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
        self.incident_feedback = IncidentFeedbackRepository(db)
        self.incident_service_report = IncidentServiceReportRepository(db)
        self.request_assignment = RequestAssignmentRepository(db)
        self.repair_shop = RepairShopRepository(db)
        self.shop_mechanic = ShopMechanicRepository(db)

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
        resolved_address = ShopProfileService(self.db).resolve_text_address(
            latitude=latitude,
            longitude=longitude,
        )

        incident = Incident(
            description=final_description,
            status=IncidentStatus.PENDING,
            priority=IncidentPriority.MEDIUM,
            address=resolved_address,
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

    def cancel_my_incident(self, *, user_id: UUID, incident_id: UUID) -> dict:
        self._validate_client_user(user_id)

        incident = self.incident.get_by_id_and_user(incident_id, user_id)
        if not incident:
            raise HTTPException(status_code=404, detail="Incidente no encontrado")

        cancellable_statuses = {
            IncidentStatus.PENDING,
            IncidentStatus.CLASSIFYING,
            IncidentStatus.CLASSIFIED,
            IncidentStatus.SEARCHING_SHOP,
            IncidentStatus.ASSIGNED,
            IncidentStatus.ON_THE_WAY,
            IncidentStatus.ARRIVED,
        }
        if incident.status not in cancellable_statuses:
            raise HTTPException(
                status_code=409,
                detail="No se puede cancelar el incidente en su estado actual",
            )

        assignments = self.request_assignment.list_by_incident(incident.id)
        for assignment in assignments:
            if assignment.status in (AssignmentStatus.PENDING, AssignmentStatus.ACCEPTED):
                assignment.status = AssignmentStatus.CANCELLED
                assignment.responded_at = datetime.now(UTC)
                self.db.add(assignment)

                if assignment.mechanic_id:
                    mechanic = self.shop_mechanic.get_by_id(assignment.mechanic_id)
                    if mechanic:
                        mechanic.is_available = True
                        self.db.add(mechanic)

        incident.status = IncidentStatus.CANCELLED
        self.db.add(incident)

        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

        self._emit_incident_realtime_event(
            incident_id=incident.id,
            event_type="incident.status.changed",
            payload={
                "status": IncidentStatus.CANCELLED.value,
                "description": "Incidente cancelado por el cliente",
                "cancelled_by": "client",
            },
            status=IncidentStatus.CANCELLED,
        )

        return {
            "incident_id": incident.id,
            "status": IncidentStatus.CANCELLED.value,
            "detail": "Incidente cancelado",
        }

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

        active_assignment = self.request_assignment.get_latest_active_by_incident(incident.id)
        assignment_payload = None
        if active_assignment:
            shop = self.repair_shop.get_by_id(active_assignment.repair_shop_id)
            mechanic_contact = self.request_assignment.get_mechanic_contact(
                active_assignment.mechanic_id
            )
            assignment_payload = {
                "request_assignment_id": active_assignment.id,
                "status": active_assignment.status.value,
                "repair_shop_id": active_assignment.repair_shop_id,
                "repair_shop_name": shop.name if shop else None,
                "repair_shop_latitude": shop.latitude if shop else None,
                "repair_shop_longitude": shop.longitude if shop else None,
                "mechanic_id": active_assignment.mechanic_id,
                "mechanic_name": mechanic_contact["full_name"] if mechanic_contact else None,
                "mechanic_phone": mechanic_contact["phone"] if mechanic_contact else None,
                "estimated_minutes": active_assignment.estimated_minutes,
            }

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
            "assignment": assignment_payload,
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

    def submit_incident_feedback(
        self,
        *,
        user_id: UUID,
        incident_id: UUID,
        rating: int,
        comment: str | None,
    ) -> dict:
        self._validate_client_user(user_id)

        incident = self.incident.get_by_id_and_user(incident_id, user_id)
        if not incident:
            raise HTTPException(status_code=404, detail="Incidente no encontrado")

        if incident.status != IncidentStatus.COMPLETED:
            raise HTTPException(
                status_code=409,
                detail="Solo puedes calificar servicios completados",
            )

        if rating < 1 or rating > 5:
            raise HTTPException(status_code=400, detail="La calificacion debe estar entre 1 y 5")

        existing_feedback = self.incident_feedback.get_by_incident_id(incident.id)
        if existing_feedback:
            raise HTTPException(
                status_code=409,
                detail="Este servicio ya fue calificado",
            )

        normalized_comment = " ".join((comment or "").split())
        if len(normalized_comment) > 1000:
            raise HTTPException(
                status_code=400,
                detail="El comentario no puede superar 1000 caracteres",
            )

        feedback = IncidentFeedback(
            incident_id=incident.id,
            rating=rating,
            comment=normalized_comment or None,
        )

        try:
            self.incident_feedback.create(feedback)
            self.db.commit()
            self.db.refresh(feedback)
        except Exception:
            self.db.rollback()
            raise

        return {
            "id": feedback.id,
            "incident_id": feedback.incident_id,
            "rating": feedback.rating,
            "comment": feedback.comment,
            "created_date": feedback.created_date,
        }

    def list_pending_feedback_reminders(self, user_id: UUID, *, limit: int = 8) -> dict:
        self._validate_client_user(user_id)

        incidents = self.incident.list_completed_without_feedback_by_user(user_id, limit=limit)
        if not incidents:
            return {"reminders": []}

        problem_ids = {incident.problem_id for incident in incidents if incident.problem_id is not None}
        problem_names_by_id: dict[UUID, str] = {}
        if problem_ids:
            query = select(Problem).where(
                Problem.id.in_(tuple(problem_ids)),
                Problem.state == True,
            )
            for problem in self.db.exec(query).all():
                problem_names_by_id[problem.id] = problem.name

        reminders = []
        for incident in incidents:
            reminders.append(
                {
                    "incident_id": incident.id,
                    "description": incident.description,
                    "problem_name": problem_names_by_id.get(incident.problem_id)
                    if incident.problem_id
                    else None,
                    "completed_at": incident.modified_date,
                }
            )

        return {"reminders": reminders}

    def list_completed_services(self, user_id: UUID) -> dict:
        self._validate_client_user(user_id)
        services = self.incident.list_service_cards_by_user(user_id, only_completed=True)
        return {"services": services}

    def list_service_history(self, user_id: UUID) -> dict:
        self._validate_client_user(user_id)
        services = self.incident.list_service_cards_by_user(user_id, only_completed=False)
        return {"services": services}

    def get_client_service_detail(self, *, user_id: UUID, incident_id: UUID) -> dict:
        self._validate_client_user(user_id)
        incident = self.incident.get_by_id_and_user(incident_id, user_id)
        if not incident:
            raise HTTPException(status_code=404, detail="Incidente no encontrado")

        vehicle_row = self.vehicle.get_by_id_and_user_with_type(incident.vehicle_id, user_id)
        if not vehicle_row:
            raise HTTPException(status_code=404, detail="Vehiculo vinculado no encontrado")

        vehicle, vehicle_type = vehicle_row

        problem_name = None
        if incident.problem_id:
            problem = self.db.exec(
                select(Problem).where(
                    Problem.id == incident.problem_id,
                    Problem.state == True,
                )
            ).first()
            problem_name = problem.name if problem else None

        assignment = self.request_assignment.get_latest_by_incident(incident.id)
        repair_shop_name = None
        mechanic_name = None
        if assignment:
            shop = self.repair_shop.get_by_id(assignment.repair_shop_id)
            repair_shop_name = shop.name if shop else None
            mechanic_name = self.request_assignment.get_mechanic_full_name(assignment.mechanic_id)

        report = self.incident_service_report.get_by_incident_id(incident.id)

        return {
            "incident_id": incident.id,
            "status": incident.status.value,
            "description": incident.description,
            "problem_name": problem_name,
            "delivery_price": incident.delivery_price,
            "distance_km": incident.distance_km,
            "address": incident.address,
            "created_date": incident.created_date,
            "updated_date": incident.modified_date,
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
            "repair_shop_name": repair_shop_name,
            "mechanic_name": mechanic_name,
            "report_description": report.description if report else None,
            "labor_price": report.labor_price if report else None,
        }

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
