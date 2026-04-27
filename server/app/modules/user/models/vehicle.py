from enum import Enum
from uuid import UUID

from sqlmodel import Field, Index, text

from app.core.base_model import UUIDBaseModel


class VehicleTypeName(str, Enum):
    CAR = "car"
    MOTORCYCLE = "motorcycle"
    TRUCK = "truck"


class VehicleType(UUIDBaseModel, table=True):
    __tablename__ = "vehicle_type"
    __table_args__ = (
        Index(
            "uq_vehicle_type_name_active",
            "name",
            unique=True,
            sqlite_where=text("state = 1"),
            postgresql_where=text("state = true"),
        ),
    )

    name: VehicleTypeName = Field(default=VehicleTypeName.CAR, index=True)


class Vehicle(UUIDBaseModel, table=True):
    __tablename__ = "vehicle"
    __table_args__ = (
        Index(
            "uq_vehicle_plate_active",
            "plate",
            unique=True,
            sqlite_where=text("state = 1"),
            postgresql_where=text("state = true"),
        ),
    )

    make: str = Field(min_length=2, max_length=60)
    model: str = Field(min_length=1, max_length=80)
    plate: str = Field(min_length=5, max_length=12, index=True)
    color: str = Field(min_length=2, max_length=30)
    year: int = Field(ge=1900, le=2100)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    type_id: UUID = Field(foreign_key="vehicle_type.id", index=True)
