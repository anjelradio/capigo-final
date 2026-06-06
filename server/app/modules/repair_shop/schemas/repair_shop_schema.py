from datetime import datetime, timezone
from typing import Annotated, Literal
from uuid import UUID

from pydantic import StringConstraints, field_validator
from sqlmodel import SQLModel

from app.modules.user.schemas import UserRead


class RepairShopCreate(SQLModel):
    name: Annotated[str, StringConstraints(min_length=5, max_length=70)]
    latitude: float
    longitude: float

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if len(normalized) < 5:
            raise ValueError("El nombre del taller debe tener al menos 5 caracteres")
        return normalized

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, value: float) -> float:
        if value < -90 or value > 90:
            raise ValueError("La latitud debe estar entre -90 y 90")
        return value

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, value: float) -> float:
        if value < -180 or value > 180:
            raise ValueError("La longitud debe estar entre -180 y 180")
        return value


class RepairShopRead(SQLModel):
    id: UUID
    name: str
    text_address: str
    latitude: float
    longitude: float
    model_config = {"from_attributes": True}


class RepairShopAddressPreviewRead(SQLModel):
    name: str
    latitude: float
    longitude: float
    text_address: str


class RepairShopCreateResponse(SQLModel):
    user: UserRead
    shop: RepairShopRead


RepairShopOnboardingResponse = RepairShopCreateResponse


class ServiceRead(SQLModel):
    id: UUID
    name: str

    model_config = {"from_attributes": True}


class ShopMechanicRead(SQLModel):
    id: UUID
    shop_id: UUID
    user_id: UUID
    is_available: bool
    created_date: datetime
    user: UserRead


class AdminRepairShopRead(SQLModel):
    id: UUID
    name: str
    text_address: str
    latitude: float
    longitude: float
    is_available: bool
    state: bool
    owner_id: UUID
    owner_name: str
    owner_email: str
    created_date: datetime
    deleted_date: datetime | None = None


class AdminRepairShopsResponse(SQLModel):
    shops: list[AdminRepairShopRead]


class AdminShopMechanicStatsRead(SQLModel):
    total: int
    available: int
    unavailable: int
    active_records: int
    inactive_records: int


class AdminRepairShopOverviewRead(SQLModel):
    shop: AdminRepairShopRead
    mechanic_stats: AdminShopMechanicStatsRead
    recent_activity: list[str]


class AdminRecentServiceRead(SQLModel):
    assignment_id: UUID
    incident_id: UUID
    incident_description: str | None = None
    incident_address: str | None = None
    incident_status: str
    problem_name: str | None = None
    mechanic_name: str | None = None
    accepted_at: datetime | None = None
    created_date: datetime


class AdminRecentServicesResponse(SQLModel):
    services: list[AdminRecentServiceRead]


class RepairShopDashboardKpisRead(SQLModel):
    requests_received: int
    accepted_services: int
    completed_services: int
    cancelled_cases: int
    acceptance_rate: float
    cancellation_rate: float
    revenue_total: float
    average_resolution_minutes: float
    average_ticket_value: float
    top_mechanic_name: str | None = None
    top_mechanic_completed: int = 0


class RepairShopDashboardBreakdownRead(SQLModel):
    label: str
    count: int
    percentage: float


class RepairShopDashboardZoneRead(SQLModel):
    label: str
    count: int
    percentage: float
    latitude: float | None = None
    longitude: float | None = None


class RepairShopDashboardRead(SQLModel):
    period_days: int
    generated_at: datetime
    kpis: RepairShopDashboardKpisRead
    services_by_type: list[RepairShopDashboardBreakdownRead]
    zones_by_services: list[RepairShopDashboardZoneRead]


class ShopServicesAssignRequest(SQLModel):
    service_ids: list[UUID]

    @field_validator("service_ids")
    @classmethod
    def validate_service_ids(cls, value: list[UUID]) -> list[UUID]:
        unique_ids = list(dict.fromkeys(value))
        if len(unique_ids) == 0:
            raise ValueError("Debes seleccionar al menos un servicio")
        return unique_ids


class RepairShopProfileUpdateRequest(SQLModel):
    name: Annotated[str, StringConstraints(min_length=5, max_length=70)]
    text_address: Annotated[str, StringConstraints(min_length=5, max_length=240)]

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if len(normalized) < 5:
            raise ValueError("El nombre del taller debe tener al menos 5 caracteres")
        return normalized

    @field_validator("text_address")
    @classmethod
    def normalize_text_address(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if len(normalized) < 5:
            raise ValueError("La direccion debe tener al menos 5 caracteres")
        return normalized


class RepairShopLocationUpdateRequest(SQLModel):
    latitude: float
    longitude: float

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, value: float) -> float:
        if value < -90 or value > 90:
            raise ValueError("La latitud debe estar entre -90 y 90")
        return value

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, value: float) -> float:
        if value < -180 or value > 180:
            raise ValueError("La longitud debe estar entre -180 y 180")
        return value


class ShopInvitationCreateRequest(SQLModel):
    expires_at: datetime

    @field_validator("expires_at")
    @classmethod
    def validate_expires_at(cls, value: datetime) -> datetime:
        now_utc = datetime.now(timezone.utc)

        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)

        if value <= now_utc:
            raise ValueError("La fecha de expiracion debe ser futura")

        return value


class ShopInvitationRead(SQLModel):
    code: str
    expires_at: datetime
    expires_at_label: str
    status: Literal["active", "expired"]


class JoinShopByCodeRequest(SQLModel):
    code: Annotated[str, StringConstraints(min_length=6, max_length=6)]

    @field_validator("code")
    @classmethod
    def validate_code(cls, value: str) -> str:
        normalized = value.strip().upper()
        if len(normalized) != 6:
            raise ValueError("El codigo debe tener 6 caracteres")
        if not normalized.isalnum():
            raise ValueError("El codigo solo permite letras y numeros")
        return normalized
