from uuid import UUID

from pydantic import field_validator
from sqlmodel import SQLModel


class CandidateOfferEvaluationRequest(SQLModel):
    radius_steps_km: list[float] = [3, 6, 10, 15]
    min_candidates: int = 5
    limit_per_radius: int = 20
    base_fee_bob: float = 5.0
    price_per_km_bob: float = 2.5

    @field_validator("radius_steps_km")
    @classmethod
    def validate_radius_steps(cls, value: list[float]) -> list[float]:
        if not value:
            raise ValueError("Debes definir al menos un radio de busqueda")
        sanitized = sorted({float(step) for step in value if float(step) > 0})
        if not sanitized:
            raise ValueError("Los radios deben ser valores positivos")
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

    @field_validator("base_fee_bob", "price_per_km_bob")
    @classmethod
    def validate_price_params(cls, value: float) -> float:
        if value < 0:
            raise ValueError("Los parametros de precio no pueden ser negativos")
        return value


class CandidateOfferCreatedRead(SQLModel):
    request_assignment_id: UUID
    shop_id: UUID
    shop_name: str
    distance_km: float
    delivery_price: float


class CandidateOfferDiscardedRead(SQLModel):
    shop_id: UUID
    shop_name: str
    reason: str


class CandidateOfferEvaluationResponse(SQLModel):
    incident_id: UUID
    problem_id: UUID
    searched_candidates: int
    offers_created: int
    offers: list[CandidateOfferCreatedRead]
    discarded: list[CandidateOfferDiscardedRead]
