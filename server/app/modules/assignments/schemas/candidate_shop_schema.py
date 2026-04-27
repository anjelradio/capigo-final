from uuid import UUID

from pydantic import field_validator
from sqlmodel import SQLModel


class CandidateShopSearchRequest(SQLModel):
    radius_steps_km: list[float] = [3, 6, 10, 15]
    min_candidates: int = 5
    limit_per_radius: int = 20

    @field_validator("radius_steps_km")
    @classmethod
    def validate_radius_steps(cls, value: list[float]) -> list[float]:
        if not value:
            raise ValueError("Debes definir al menos un radio de busqueda")

        sanitized = sorted({float(step) for step in value if float(step) > 0})
        if not sanitized:
            raise ValueError("Los radios deben ser valores positivos")
        if len(sanitized) > 8:
            raise ValueError("No se permiten mas de 8 radios de busqueda")
        return sanitized

    @field_validator("min_candidates")
    @classmethod
    def validate_min_candidates(cls, value: int) -> int:
        if value < 1:
            raise ValueError("min_candidates debe ser al menos 1")
        if value > 50:
            raise ValueError("min_candidates no puede ser mayor a 50")
        return value

    @field_validator("limit_per_radius")
    @classmethod
    def validate_limit_per_radius(cls, value: int) -> int:
        if value < 1:
            raise ValueError("limit_per_radius debe ser al menos 1")
        if value > 200:
            raise ValueError("limit_per_radius no puede ser mayor a 200")
        return value


class CandidateShopRead(SQLModel):
    shop_id: UUID
    shop_name: str
    shop_latitude: float
    shop_longitude: float
    distance_km: float


class CandidateShopSearchResponse(SQLModel):
    incident_id: UUID
    problem_id: UUID
    searched_radius_steps_km: list[float]
    candidates_found: int
    candidates: list[CandidateShopRead]
