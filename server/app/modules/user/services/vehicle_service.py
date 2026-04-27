from uuid import UUID
from datetime import datetime

from fastapi import HTTPException
from sqlmodel import Session

from app.modules.user.models import UserRole, Vehicle, VehicleType
from app.modules.user.repositories import UserRepository, VehicleRepository
from app.modules.user.schemas import VehicleCreate, VehicleUpdate


class VehicleService:
    def __init__(self, db: Session):
        self.user = UserRepository(db)
        self.vehicle = VehicleRepository(db)

    def list_my_vehicles(self, user_id: UUID) -> list[dict]:
        self._validate_client_user(user_id)

        rows = self.vehicle.list_by_user_with_type(user_id)

        return [self._to_vehicle_read(vehicle, vehicle_type) for vehicle, vehicle_type in rows]

    def list_vehicle_types(self, user_id: UUID) -> list[dict]:
        self._validate_client_user(user_id)

        vehicle_types = self.vehicle.list_active_types()
        return [
            {
                "id": vehicle_type.id,
                "name": vehicle_type.name,
            }
            for vehicle_type in vehicle_types
        ]

    def get_my_vehicle_by_id(self, user_id: UUID, vehicle_id: UUID) -> dict:
        self._validate_client_user(user_id)

        row = self.vehicle.get_by_id_and_user_with_type(vehicle_id, user_id)
        if not row:
            raise HTTPException(status_code=404, detail="Vehiculo no encontrado")

        vehicle, vehicle_type = row
        return self._to_vehicle_read(vehicle, vehicle_type)

    def create_vehicle(self, user_id: UUID, payload: VehicleCreate) -> dict:
        self._validate_client_user(user_id)

        vehicle_type = self.vehicle.get_active_type_by_id(payload.type_id)
        if not vehicle_type:
            raise HTTPException(status_code=400, detail="Tipo de vehiculo invalido")

        existing_plate = self.vehicle.get_active_vehicle_by_plate(payload.plate)
        if existing_plate:
            raise HTTPException(status_code=409, detail="La placa ya esta registrada")

        vehicle = Vehicle(
            make=payload.make,
            model=payload.model,
            plate=payload.plate,
            color=payload.color,
            year=payload.year,
            user_id=user_id,
            type_id=payload.type_id,
        )
        created = self.vehicle.create(vehicle)

        return self._to_vehicle_read(created, vehicle_type)

    def update_vehicle(
        self,
        user_id: UUID,
        vehicle_id: UUID,
        payload: VehicleUpdate,
    ) -> dict:
        self._validate_client_user(user_id)

        row = self.vehicle.get_by_id_and_user_with_type(vehicle_id, user_id)
        if not row:
            raise HTTPException(status_code=404, detail="Vehiculo no encontrado")

        vehicle, _ = row

        vehicle_type = self.vehicle.get_active_type_by_id(payload.type_id)
        if not vehicle_type:
            raise HTTPException(status_code=400, detail="Tipo de vehiculo invalido")

        existing_plate = self.vehicle.get_active_vehicle_by_plate_excluding_id(
            payload.plate,
            vehicle_id,
        )
        if existing_plate:
            raise HTTPException(status_code=409, detail="La placa ya esta registrada")

        vehicle.make = payload.make
        vehicle.model = payload.model
        vehicle.plate = payload.plate
        vehicle.color = payload.color
        vehicle.year = payload.year
        vehicle.type_id = payload.type_id

        updated = self.vehicle.update(vehicle)

        return self._to_vehicle_read(updated, vehicle_type)

    def delete_vehicle(self, user_id: UUID, vehicle_id: UUID) -> None:
        self._validate_client_user(user_id)

        vehicle = self.vehicle.get_active_by_id_and_user(vehicle_id, user_id)
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehiculo no encontrado")

        vehicle.state = False
        vehicle.deleted_date = datetime.utcnow()
        self.vehicle.soft_delete(vehicle)

    def _validate_client_user(self, user_id: UUID) -> None:
        user = self.user.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        if user.role != UserRole.CLIENT:
            raise HTTPException(
                status_code=403,
                detail="Solo usuarios client pueden administrar vehiculos",
            )

    def _to_vehicle_read(self, vehicle: Vehicle, vehicle_type: VehicleType) -> dict:
        return {
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
        }
