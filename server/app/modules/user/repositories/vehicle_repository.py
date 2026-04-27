from uuid import UUID

from sqlmodel import Session, func, select

from app.modules.user.models import Vehicle, VehicleType


class VehicleRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_user_with_type(self, user_id: UUID) -> list[tuple[Vehicle, VehicleType]]:
        query = (
            select(Vehicle, VehicleType)
            .join(VehicleType, Vehicle.type_id == VehicleType.id)
            .where(
                Vehicle.user_id == user_id,
                Vehicle.state == True,
                VehicleType.state == True,
            )
            .order_by(Vehicle.created_date.desc())
        )
        return list(self.db.exec(query).all())

    def list_active_types(self) -> list[VehicleType]:
        query = select(VehicleType).where(VehicleType.state == True).order_by(VehicleType.name.asc())
        return list(self.db.exec(query).all())

    def get_by_id_and_user_with_type(
        self, vehicle_id: UUID, user_id: UUID
    ) -> tuple[Vehicle, VehicleType] | None:
        query = (
            select(Vehicle, VehicleType)
            .join(VehicleType, Vehicle.type_id == VehicleType.id)
            .where(
                Vehicle.id == vehicle_id,
                Vehicle.user_id == user_id,
                Vehicle.state == True,
                VehicleType.state == True,
            )
        )
        return self.db.exec(query).first()

    def get_active_by_id_and_user(self, vehicle_id: UUID, user_id: UUID) -> Vehicle | None:
        query = select(Vehicle).where(
            Vehicle.id == vehicle_id,
            Vehicle.user_id == user_id,
            Vehicle.state == True,
        )
        return self.db.exec(query).first()

    def get_active_by_id_with_type(self, vehicle_id: UUID) -> tuple[Vehicle, VehicleType] | None:
        query = (
            select(Vehicle, VehicleType)
            .join(VehicleType, Vehicle.type_id == VehicleType.id)
            .where(
                Vehicle.id == vehicle_id,
                Vehicle.state == True,
                VehicleType.state == True,
            )
        )
        return self.db.exec(query).first()

    def get_active_type_by_id(self, type_id: UUID) -> VehicleType | None:
        query = select(VehicleType).where(
            VehicleType.id == type_id,
            VehicleType.state == True,
        )
        return self.db.exec(query).first()

    def get_active_vehicle_by_plate(self, plate: str) -> Vehicle | None:
        query = select(Vehicle).where(
            func.upper(func.trim(Vehicle.plate)) == plate,
            Vehicle.state == True,
        )
        return self.db.exec(query).first()

    def get_active_vehicle_by_plate_excluding_id(
        self,
        plate: str,
        vehicle_id: UUID,
    ) -> Vehicle | None:
        query = select(Vehicle).where(
            func.upper(func.trim(Vehicle.plate)) == plate,
            Vehicle.id != vehicle_id,
            Vehicle.state == True,
        )
        return self.db.exec(query).first()

    def create(self, vehicle: Vehicle) -> Vehicle:
        self.db.add(vehicle)
        self.db.commit()
        self.db.refresh(vehicle)
        return vehicle

    def update(self, vehicle: Vehicle) -> Vehicle:
        self.db.add(vehicle)
        self.db.commit()
        self.db.refresh(vehicle)
        return vehicle

    def soft_delete(self, vehicle: Vehicle) -> None:
        self.db.add(vehicle)
        self.db.commit()
