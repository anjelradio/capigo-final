from uuid import UUID
from secrets import compare_digest

from fastapi import HTTPException
from sqlmodel import Session

from app.core.config import settings
from app.core.email import send_email
from app.core.otp import generate_otp, hash_otp
from app.core.redis import redis_client
from app.core.security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.modules.auth.service import validate_password_policy
from app.modules.user.repositories import UserRepository
from app.modules.user.schemas import (
    UpdateEmailRequest,
    UpdatePasswordRequest,
    UserProfileUpdate,
    VerifyEmailChangeOtpRequest,
)

EMAIL_CHANGE_SCOPE = "email_change"


class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def update_profile(self, user_id: UUID, payload: UserProfileUpdate):
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        user.first_name = payload.first_name
        user.last_name = payload.last_name
        user.phone = payload.phone

        return self.repo.update(user)

    def update_password(self, user_id: UUID, payload: UpdatePasswordRequest) -> None:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        if payload.new_password != payload.confirm_new_password:
            raise HTTPException(
                status_code=400,
                detail="La confirmacion de contraseña no coincide",
            )

        if not verify_password(payload.current_password[:72], user.hashed_password):
            raise HTTPException(status_code=401, detail="Contrasena actual incorrecta")

        if payload.current_password == payload.new_password:
            raise HTTPException(
                status_code=400,
                detail="La nueva contraseña debe ser diferente a la actual",
            )

        validate_password_policy(payload.new_password)

        user.hashed_password = hash_password(payload.new_password)
        self.repo.update(user)

    async def request_email_change_otp(self, user_id: UUID) -> None:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        otp_key = f"email_change_otp:{user.id}"
        attempts_key = f"email_change_otp_attempts:{user.id}"
        cooldown_key = f"email_change_otp_cooldown:{user.id}"

        ttl = redis_client.ttl(cooldown_key)
        if ttl and ttl > 0:
            raise HTTPException(
                status_code=429,
                detail=f"Debes esperar {ttl} segundos para solicitar otro codigo",
            )

        otp = generate_otp()
        otp_hashed = hash_otp(otp)
        otp_ttl_seconds = settings.OTP_EXPIRES_MIN * 60

        html_content = (
            f"<h2>Verificacion para cambio de correo</h2>"
            f"<p>Tu codigo OTP es: <strong>{otp}</strong></p>"
            f"<p>Este codigo expira en {settings.OTP_EXPIRES_MIN} minutos.</p>"
        )

        try:
            await send_email(
                to_email=user.email,
                subject="Codigo OTP para cambio de correo",
                html_content=html_content,
            )
        except Exception:
            raise HTTPException(status_code=500, detail="No se pudo enviar el codigo OTP")

        redis_client.set(otp_key, otp_hashed, ex=otp_ttl_seconds)
        redis_client.set(attempts_key, "0", ex=otp_ttl_seconds)
        redis_client.set(cooldown_key, "1", ex=settings.OTP_RESEND_COOLDOWN_SEC)

    def verify_email_change_otp(
        self, user_id: UUID, payload: VerifyEmailChangeOtpRequest
    ) -> str:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        otp_key = f"email_change_otp:{user.id}"
        attempts_key = f"email_change_otp_attempts:{user.id}"
        cooldown_key = f"email_change_otp_cooldown:{user.id}"

        stored_otp_hash = redis_client.get(otp_key)
        if not stored_otp_hash:
            raise HTTPException(status_code=400, detail="Codigo OTP invalido o expirado")

        attempts = int(redis_client.get(attempts_key) or "0")
        if attempts >= settings.OTP_MAX_ATTEMPTS:
            raise HTTPException(
                status_code=429,
                detail="Se alcanzo el limite de intentos para el codigo OTP",
            )

        provided_otp_hash = hash_otp(payload.otp)
        if not compare_digest(stored_otp_hash, provided_otp_hash):
            attempts += 1
            remaining_ttl = redis_client.ttl(otp_key)

            if remaining_ttl and remaining_ttl > 0:
                redis_client.set(attempts_key, str(attempts), ex=remaining_ttl)
            else:
                redis_client.set(attempts_key, str(attempts))

            if attempts >= settings.OTP_MAX_ATTEMPTS:
                raise HTTPException(
                    status_code=429,
                    detail="Se alcanzo el limite de intentos para el codigo OTP",
                )

            raise HTTPException(status_code=400, detail="Codigo OTP invalido o expirado")

        redis_client.delete(otp_key, attempts_key, cooldown_key)

        return create_access_token(
            {
                "sub": str(user.id),
                "scope": EMAIL_CHANGE_SCOPE,
            },
            minutes=10,
        )

    def update_email(self, user_id: UUID, payload: UpdateEmailRequest):
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        try:
            token_payload = decode_token(payload.change_email_token)
            token_user_id = UUID(token_payload.get("sub", ""))
            token_scope = token_payload.get("scope")
        except Exception:
            raise HTTPException(status_code=401, detail="Token de cambio de correo invalido")

        if token_user_id != user.id or token_scope != EMAIL_CHANGE_SCOPE:
            raise HTTPException(status_code=401, detail="Token de cambio de correo invalido")

        new_email = str(payload.new_email).strip().lower()

        if new_email == user.email:
            raise HTTPException(status_code=400, detail="El nuevo correo debe ser diferente")

        existing_user = self.repo.get_by_email(new_email)
        if existing_user and existing_user.id != user.id:
            raise HTTPException(status_code=400, detail="El correo ya esta registrado")

        user.email = new_email
        return self.repo.update(user)
