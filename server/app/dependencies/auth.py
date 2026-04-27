from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from app.core.db import get_session
from app.core.security import decode_token
from app.modules.user.models import User
from app.modules.user.repositories import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")


def get_db():
    yield from get_session()


DBSession = Annotated[Session, Depends(get_db)]


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: DBSession
) -> User:
    credentials_exc = HTTPException(
        status_code=401, detail="No Autorizado", headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = decode_token(token)
        user_id = UUID(payload.get("sub"))
    except Exception:
        raise credentials_exc

    repo = UserRepository(db)
    user = repo.get_by_id(user_id)

    if not user:
        raise credentials_exc

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
