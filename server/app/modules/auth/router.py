from fastapi import APIRouter, Depends, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from app.dependencies.auth import CurrentUser, DBSession
from app.modules.auth.schema import (
    LoginRequest,
    LoginResponse,
    RequestPasswordResetOtpRequest,
    VerifyPasswordResetOtpRequest,
)
from app.modules.auth.service import AuthService
from app.modules.user.schemas import UserCreate

router = APIRouter(prefix="/auth", tags=["Autenticacion y Seguridad"])


@router.post(
    "/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED
)
def register(db: DBSession, payload: UserCreate):
    service = AuthService(db)
    token, user = service.register_with_token(payload)

    return {"user": user, "access_token": token}


@router.post("/login", response_model=LoginResponse)
def login(db: DBSession, payload: LoginRequest):
    service = AuthService(db)
    token, user = service.login(payload.email, payload.password)

    return {"user": user, "access_token": token}


@router.post("/token", response_model=LoginResponse)
def login_token(db: DBSession, form: OAuth2PasswordRequestForm = Depends()):
    email = form.username
    password = form.password
    service = AuthService(db)
    token, user = service.login(email, password)

    return {"user": user, "access_token": token}


@router.post("/check-status", response_model=LoginResponse)
def check_status(db: DBSession, user: CurrentUser):
    service = AuthService(db)
    token, current_user = service.check_auth_status(user)
    return {"user": current_user, "access_token": token}


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(response: Response):
    response.delete_cookie("auth_token")
    return {"detail": "Sesion cerrada"}


@router.post(
    "/password/request-otp",
    status_code=status.HTTP_200_OK,
)
async def request_password_reset_otp(
    db: DBSession, payload: RequestPasswordResetOtpRequest
):
    service = AuthService(db)
    await service.request_password_reset_otp(payload)
    return Response(status_code=status.HTTP_200_OK)


@router.post(
    "/password/verify-otp",
    status_code=status.HTTP_200_OK,
)
async def verify_password_reset_otp(
    db: DBSession, payload: VerifyPasswordResetOtpRequest
):
    service = AuthService(db)
    await service.verify_password_reset_otp(payload)
    return Response(status_code=status.HTTP_200_OK)
