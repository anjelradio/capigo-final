from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session

from app.modules.user.models import UserRole

from .base_service import AssignmentBaseService


class MechanicBaseService(AssignmentBaseService):
    def __init__(self, db: Session):
        super().__init__(db)

    def _resolve_mechanic_link(self, user_id: UUID):
        user = self._get_user_or_404(user_id)
        if user.role != UserRole.MECHANIC:
            raise HTTPException(status_code=403, detail="Solo mecanicos pueden operar asignaciones")

        mechanic_link = self.shop_mechanic.get_active_by_user_id(user.id)
        if not mechanic_link:
            raise HTTPException(status_code=404, detail="Mecanico no vinculado a un taller")
        return mechanic_link

    def _build_assignment_read(self, assignment) -> dict:
        incident = self.incident.get_by_id(assignment.incident_id)
        if not incident:
            raise HTTPException(status_code=404, detail="Incidente no encontrado")

        shop = self.repair_shop.get_by_id(assignment.repair_shop_id)
        payload = self.request_assignment.get_offer_notification_payload(assignment.id) or {}
        evidences = self.evidence.list_by_incident_id(incident.id)
        vehicle_with_type = self.vehicle.get_active_by_id_with_type(incident.vehicle_id)
        client_user = self.user.get_by_id(incident.user_id)

        vehicle_data = None
        if vehicle_with_type:
            vehicle, vehicle_type = vehicle_with_type
            vehicle_data = {
                "id": vehicle.id,
                "make": vehicle.make,
                "model": vehicle.model,
                "plate": vehicle.plate,
                "color": vehicle.color,
                "year": vehicle.year,
                "type_name": vehicle_type.name.value if vehicle_type else None,
            }

        return {
            "assignment_id": assignment.id,
            "assignment_status": assignment.status.value,
            "repair_shop_id": assignment.repair_shop_id,
            "repair_shop_name": shop.name if shop else None,
            "repair_shop_latitude": shop.latitude if shop else None,
            "repair_shop_longitude": shop.longitude if shop else None,
            "mechanic_id": assignment.mechanic_id,
            "assigned_at": assignment.created_date,
            "incident": {
                "id": incident.id,
                "status": incident.status.value,
                "description": incident.description,
                "address": incident.address,
                "latitude": incident.latitude,
                "longitude": incident.longitude,
                "problem_id": payload.get("problem_id"),
                "problem_name": payload.get("problem_name"),
                "distance_km": payload.get("distance_km"),
                "delivery_price": payload.get("delivery_price"),
                "estimated_minutes": payload.get("estimated_minutes"),
                "client_email": client_user.email if client_user else None,
                "client_name": (
                    f"{client_user.first_name} {client_user.last_name}".strip()
                    if client_user
                    else None
                ),
                "client_phone": client_user.phone if client_user else None,
                "evidence_urls": [evidence.url for evidence in evidences],
                "vehicle": vehicle_data,
            },
        }
