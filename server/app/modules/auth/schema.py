from pydantic import EmailStr
from sqlmodel import SQLModel

from app.modules.user.schemas import UserRead


class LoginResponse(SQLModel):
    user: UserRead
    access_token: str


class LoginRequest(SQLModel):
    email: EmailStr
    password: str


class RequestPasswordResetOtpRequest(SQLModel):
    email: EmailStr


class VerifyPasswordResetOtpRequest(SQLModel):
    email: EmailStr
    otp: str
