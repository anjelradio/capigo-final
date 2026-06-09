from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, UploadFile
from sqlmodel import Session

from app.modules.assignments.models import AssignmentStatus
from app.modules.assignments.services.assignment_state_transition_service import AssignmentStateTransitionService
from app.modules.incidents.models import Evidence, Incident, IncidentPriority, IncidentStatus
from app.modules.incidents.services.incident_state_transition_service import IncidentStateTransitionService
from app.modules.repair_shop.services.shop_profile_service import ShopProfileService

from .cloudinary_upload_service import CloudinaryUploadService
from .incident_base_service import IncidentBaseService


class IncidentCreationService(IncidentBaseService):
    def __init__(self, db: Session):
        super().__init__(db)
        self.cloudinary_upload = CloudinaryUploadService(db)
        self.incident_transition = IncidentStateTransitionService(db)
        self.assignment_transition = AssignmentStateTransitionService(db)

    def create_incident(
        self,
        user_id: UUID,
        vehicle_id: UUID,
        latitude: float,
        longitude: float,
        description: str | None,
        audio: UploadFile | None,
        photos: list[UploadFile],
        client_request_id: str | None = None,
    ) -> dict:
        self._validate_client_user(user_id)

        normalized_client_request_id = self._normalize_client_request_id(client_request_id)
        if normalized_client_request_id:
            existing = self.incident.get_by_user_and_client_request_id(
                user_id=user_id,
                client_request_id=normalized_client_request_id,
            )
            if existing:
                evidences = self.evidence.list_by_incident_id(existing.id)
                return self._to_incident_read(existing, evidences)

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
            client_request_id=normalized_client_request_id,
            user_id=user_id,
            vehicle_id=vehicle_id,
        )

        try:
            self.incident.create(incident)
            self.db.flush()

            uploaded_urls = self.cloudinary_upload.upload_photos(incident.id, photos)
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
        self.workflow.incident_created(incident=incident)
        return self._to_incident_read(incident, evidences)

    def cancel_my_incident(self, *, user_id: UUID, incident_id: UUID) -> dict:
        self._validate_client_user(user_id)

        incident = self.incident.get_by_id_and_user(incident_id, user_id)
        if not incident:
            raise HTTPException(status_code=404, detail="Incidente no encontrado")

        self.incident_transition.ensure_client_can_cancel(incident.status)

        assignments = self.request_assignment.list_by_incident(incident.id)
        for assignment in assignments:
            if assignment.status in (AssignmentStatus.PENDING, AssignmentStatus.ACCEPTED):
                self.assignment_transition.transition_assignment(assignment, AssignmentStatus.CANCELLED)
                assignment.responded_at = datetime.now(UTC)
                self.db.add(assignment)

                if assignment.mechanic_id:
                    mechanic = self.shop_mechanic.get_active_by_id_and_shop(
                        assignment.mechanic_id,
                        assignment.repair_shop_id,
                    )
                    if mechanic:
                        mechanic.is_available = True
                        self.db.add(mechanic)

        self.incident_transition.transition_incident(incident, IncidentStatus.CANCELLED)

        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

        self.workflow.incident_cancelled_by_client(incident=incident)

        return {
            "incident_id": incident.id,
            "status": IncidentStatus.CANCELLED.value,
            "detail": "Incidente cancelado",
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

    def _normalize_client_request_id(self, client_request_id: str | None) -> str | None:
        if client_request_id is None:
            return None

        normalized = client_request_id.strip()
        return normalized or None
