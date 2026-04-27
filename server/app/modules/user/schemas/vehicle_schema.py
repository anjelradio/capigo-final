from uuid import UUID
from datetime import datetime
from typing import Annotated

from pydantic import StringConstraints, field_validator
from sqlmodel import SQLModel

from app.modules.user.models import VehicleTypeName


class VehicleBase(SQLModel):
    make: Annotated[str, StringConstraints(min_length=2, max_length=60)]
    model: Annotated[str, StringConstraints(min_length=1, max_length=80)]
    plate: Annotated[str, StringConstraints(min_length=5, max_length=12)]
    color: Annotated[str, StringConstraints(min_length=2, max_length=30)]
    year: int
    type_id: UUID

    @field_validator("make", "model", "color")
    @classmethod
    def normalize_text_fields(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if not normalized:
            raise ValueError("El campo es requerido")
        return normalized

    @field_validator("plate")
    @classmethod
    def normalize_plate(cls, value: str) -> str:
        normalized = "".join(value.upper().split())
        if not normalized:
            raise ValueError("La placa es requerida")
        return normalized

    @field_validator("year")
    @classmethod
    def validate_year(cls, value: int) -> int:
        max_allowed_year = datetime.now().year + 1
        if value < 1900 or value > max_allowed_year:
            raise ValueError(
                f"El anio del vehiculo debe estar entre 1900 y {max_allowed_year}"
            )
        return value


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(VehicleBase):
    pass


class VehicleTypeRead(SQLModel):
    id: UUID
    name: VehicleTypeName

    model_config = {"from_attributes": True}


class VehicleRead(SQLModel):
    id: UUID
    make: str
    model: str
    plate: str
    color: str
    year: int
    type: VehicleTypeRead

    model_config = {"from_attributes": True}
