from .user_schema import (
    UpdateEmailRequest,
    UpdatePasswordRequest,
    UserCreate,
    UserProfileUpdate,
    UserRead,
    VerifyEmailChangeOtpRequest,
    VerifyEmailChangeOtpResponse,
)
from .vehicle_schema import VehicleCreate, VehicleRead, VehicleTypeRead, VehicleUpdate

__all__ = [
    "UserRead",
    "UserCreate",
    "UserProfileUpdate",
    "UpdatePasswordRequest",
    "VerifyEmailChangeOtpRequest",
    "VerifyEmailChangeOtpResponse",
    "UpdateEmailRequest",
    "VehicleCreate",
    "VehicleUpdate",
    "VehicleRead",
    "VehicleTypeRead",
]
