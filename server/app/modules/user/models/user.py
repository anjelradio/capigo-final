from enum import Enum

from sqlmodel import Field

from app.core.base_model import UUIDBaseModel


class UserRole(str, Enum):
    ADMIN = "admin"
    OWNER = "owner"
    MECHANIC = "mechanic"
    CLIENT = "client"


class User(UUIDBaseModel, table=True):
    first_name: str
    last_name: str
    email: str = Field(index=True, unique=True)
    phone: str
    hashed_password: str
    role: UserRole = Field(default=UserRole.CLIENT)
