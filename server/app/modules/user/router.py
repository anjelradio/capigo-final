from uuid import UUID

from fastapi import APIRouter, Response, status

from app.dependencies.auth import CurrentUser, DBSession
from app.modules.user.schemas import (
    UpdateEmailRequest,
    UpdatePasswordRequest,
    VehicleCreate,
    VehicleRead,
    VehicleTypeRead,
    VehicleUpdate,
    UserProfileUpdate,
    UserRead,
    VerifyEmailChangeOtpRequest,
    VerifyEmailChangeOtpResponse,
)
from app.modules.user.services import UserService, VehicleService

router = APIRouter(prefix="/user", tags=["Usuarios"])


@router.patch("/me/profile", response_model=UserRead)
def update_profile(db: DBSession, payload: UserProfileUpdate, user: CurrentUser):
    service = UserService(db)
    return service.update_profile(user.id, payload)


@router.patch("/me/password", status_code=status.HTTP_204_NO_CONTENT)
def update_password(db: DBSession, payload: UpdatePasswordRequest, user: CurrentUser):
    service = UserService(db)
    service.update_password(user.id, payload)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/me/email/change/request-otp", status_code=status.HTTP_200_OK)
async def request_email_change_otp(db: DBSession, user: CurrentUser):
    service = UserService(db)
    await service.request_email_change_otp(user.id)
    return Response(status_code=status.HTTP_200_OK)


@router.post(
    "/me/email/change/verify-otp", response_model=VerifyEmailChangeOtpResponse
)
def verify_email_change_otp(
    db: DBSession, payload: VerifyEmailChangeOtpRequest, user: CurrentUser
):
    service = UserService(db)
    token = service.verify_email_change_otp(user.id, payload)
    return {"change_email_token": token}


@router.patch("/me/email", response_model=UserRead)
def update_email(db: DBSession, payload: UpdateEmailRequest, user: CurrentUser):
    service = UserService(db)
    return service.update_email(user.id, payload)


@router.get("/me/vehicles", response_model=list[VehicleRead])
def list_my_vehicles(db: DBSession, user: CurrentUser):
    service = VehicleService(db)
    return service.list_my_vehicles(user.id)


@router.get("/me/vehicles/types", response_model=list[VehicleTypeRead])
def list_vehicle_types(db: DBSession, user: CurrentUser):
    service = VehicleService(db)
    return service.list_vehicle_types(user.id)


@router.get("/me/vehicles/{vehicle_id}", response_model=VehicleRead)
def get_my_vehicle_by_id(db: DBSession, vehicle_id: UUID, user: CurrentUser):
    service = VehicleService(db)
    return service.get_my_vehicle_by_id(user.id, vehicle_id)


@router.post(
    "/me/vehicles",
    response_model=VehicleRead,
    status_code=status.HTTP_201_CREATED,
)
def create_my_vehicle(db: DBSession, payload: VehicleCreate, user: CurrentUser):
    service = VehicleService(db)
    return service.create_vehicle(user.id, payload)


@router.patch("/me/vehicles/{vehicle_id}", response_model=VehicleRead)
def update_my_vehicle(
    db: DBSession,
    vehicle_id: UUID,
    payload: VehicleUpdate,
    user: CurrentUser,
):
    service = VehicleService(db)
    return service.update_vehicle(user.id, vehicle_id, payload)


@router.delete("/me/vehicles/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_vehicle(db: DBSession, vehicle_id: UUID, user: CurrentUser):
    service = VehicleService(db)
    service.delete_vehicle(user.id, vehicle_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
