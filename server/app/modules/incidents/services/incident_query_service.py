from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session

from app.modules.assignments.models import AssignmentStatus

from .incident_base_service import IncidentBaseService


class IncidentQueryService(IncidentBaseService):
    def __init__(self, db: Session):
        super().__init__(db)

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
                "quoted_price": active_assignment.quoted_price,
                "final_price": active_assignment.final_price,
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
            problem = self.problem.get_active_by_id(incident.problem_id)
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
