import uuid
from typing import Annotated

from pydantic import EmailStr, StringConstraints, field_validator
from sqlmodel import SQLModel

from app.modules.user.models.user import UserRole


class UserRead(SQLModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    email: str
    phone: str
    role: UserRole
    model_config = {"from_attributes": True}


class UserCreate(SQLModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    password: str


class UserProfileUpdate(SQLModel):
    first_name: Annotated[str, StringConstraints(min_length=2, max_length=50)]
    last_name: Annotated[str, StringConstraints(min_length=2, max_length=70)]
    phone: Annotated[str, StringConstraints(min_length=7, max_length=9)]

    @field_validator("first_name", "last_name", "phone")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if len(normalized) < 2:
            raise ValueError("El campo debe tener al menos 2 caracteres")
        return normalized


class UpdatePasswordRequest(SQLModel):
    current_password: Annotated[str, StringConstraints(min_length=1)]
    new_password: Annotated[str, StringConstraints(min_length=1)]
    confirm_new_password: Annotated[str, StringConstraints(min_length=1)]

    @field_validator("current_password", "new_password", "confirm_new_password")
    @classmethod
    def validate_password_required(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("La contraseña es requerida")
        return value


class VerifyEmailChangeOtpRequest(SQLModel):
    otp: Annotated[str, StringConstraints(min_length=1)]

    @field_validator("otp")
    @classmethod
    def validate_otp_required(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("El codigo OTP es requerido")
        return normalized


class VerifyEmailChangeOtpResponse(SQLModel):
    change_email_token: str


class UpdateEmailRequest(SQLModel):
    new_email: EmailStr
    change_email_token: Annotated[str, StringConstraints(min_length=1)]
