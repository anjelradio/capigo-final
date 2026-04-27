import string
from random import SystemRandom
from secrets import choice, compare_digest

from fastapi import HTTPException
from sqlmodel import Session

from app.core.config import settings
from app.core.email import send_email
from app.core.otp import generate_otp, hash_otp
from app.core.redis import redis_client
from app.core.security import create_access_token, hash_password, verify_password
from app.modules.auth.schema import (
    RequestPasswordResetOtpRequest,
    VerifyPasswordResetOtpRequest,
)
from app.modules.user.models import User, UserRole
from app.modules.user.repositories import UserRepository
from app.modules.user.schemas import UserCreate

secure_random = SystemRandom()


def validate_password_policy(password: str) -> None:
    digit_count = sum(char.isdigit() for char in password)
    uppercase_count = sum(char.isupper() for char in password)

    has_two_digits = digit_count >= 2
    has_two_uppercase = uppercase_count >= 2

    if not has_two_digits and not has_two_uppercase:
        raise HTTPException(
            status_code=400,
            detail="La contraseña debe tener al menos 2 números y al menos 2 letras mayúsculas",
        )

    if not has_two_digits:
        raise HTTPException(
            status_code=400,
            detail="La contraseña debe tener al menos 2 números",
        )

    if not has_two_uppercase:
        raise HTTPException(
            status_code=400,
            detail="La contraseña debe tener al menos 2 letras mayúsculas",
        )


class AuthService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def _validate_password_policy(self, password: str) -> None:
        validate_password_policy(password)

    def register(self, payload: UserCreate) -> User:
        if self.repo.get_by_email(payload.email):
            raise HTTPException(status_code=400, detail="Email ya registrado")

        self._validate_password_policy(payload.password)

        user = User(
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=payload.email,
            phone=payload.phone,
            hashed_password=hash_password(payload.password),
            role=UserRole.CLIENT,
        )

        return self.repo.create(user)

    def register_with_token(self, payload: UserCreate):
        user = self.register(payload)
        token = create_access_token({"sub": str(user.id)})
        return token, user

    def login(self, email: str, password: str):
        user = self.repo.get_by_email(email)
        if not user:
            raise HTTPException(status_code=401, detail="Credenciales Invalidas")

        if not verify_password(password[:72], user.hashed_password):
            raise HTTPException(status_code=401, detail="Contrasena Incorrecta")

        token = create_access_token({"sub": str(user.id)})
        return token, user

    def check_auth_status(self, user: User):
        token = create_access_token({"sub": str(user.id)})
        return token, user

    def _generate_temporary_password(self, length: int = 10) -> str:
        generated = [choice(string.ascii_uppercase) for _ in range(2)]
        generated.extend(choice(string.digits) for _ in range(2))

        pool = string.ascii_letters + string.digits
        for _ in range(max(length - 4, 4)):
            generated.append(choice(pool))

        secure_random.shuffle(generated)
        return "".join(generated)

    async def request_password_reset_otp(
        self, payload: RequestPasswordResetOtpRequest
    ) -> None:
        email = str(payload.email).strip().lower()
        user = self.repo.get_by_email(email)

        otp_key = f"password_reset_otp:{email}"
        attempts_key = f"password_reset_otp_attempts:{email}"
        cooldown_key = f"password_reset_otp_cooldown:{email}"

        ttl = redis_client.ttl(cooldown_key)
        if ttl and ttl > 0:
            raise HTTPException(
                status_code=429,
                detail=f"Debes esperar {ttl} segundos para solicitar otro codigo",
            )

        otp_ttl_seconds = settings.OTP_EXPIRES_MIN * 60

        if user:
            otp = generate_otp()
            otp_hashed = hash_otp(otp)

            html_content = (
                f"<h2>Recuperacion de contraseña</h2>"
                f"<p>Tu codigo OTP es: <strong>{otp}</strong></p>"
                f"<p>Este codigo expira en {settings.OTP_EXPIRES_MIN} minutos.</p>"
            )

            try:
                await send_email(
                    to_email=user.email,
                    subject="Codigo OTP para recuperar contraseña",
                    html_content=html_content,
                )
            except Exception:
                raise HTTPException(
                    status_code=500, detail="No se pudo enviar el codigo OTP"
                )

            redis_client.set(otp_key, otp_hashed, ex=otp_ttl_seconds)
            redis_client.set(attempts_key, "0", ex=otp_ttl_seconds)

        redis_client.set(cooldown_key, "1", ex=settings.OTP_RESEND_COOLDOWN_SEC)

    async def verify_password_reset_otp(
        self, payload: VerifyPasswordResetOtpRequest
    ) -> None:
        email = str(payload.email).strip().lower()
        user = self.repo.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=400, detail="Codigo OTP invalido o expirado"
            )

        otp_key = f"password_reset_otp:{email}"
        attempts_key = f"password_reset_otp_attempts:{email}"
        cooldown_key = f"password_reset_otp_cooldown:{email}"

        stored_otp_hash = redis_client.get(otp_key)
        if not stored_otp_hash:
            raise HTTPException(
                status_code=400, detail="Codigo OTP invalido o expirado"
            )

        attempts = int(redis_client.get(attempts_key) or "0")
        if attempts >= settings.OTP_MAX_ATTEMPTS:
            raise HTTPException(
                status_code=429,
                detail="Se alcanzo el limite de intentos para el codigo OTP",
            )

        provided_otp_hash = hash_otp(payload.otp.strip())
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

            raise HTTPException(
                status_code=400, detail="Codigo OTP invalido o expirado"
            )

        redis_client.delete(otp_key, attempts_key, cooldown_key)

        temporary_password = self._generate_temporary_password()
        validate_password_policy(temporary_password)

        html_content = (
            f"<h2>Nueva contraseña temporal</h2>"
            f"<p>Tu nueva contraseña es: <strong>{temporary_password}</strong></p>"
            f"<p>Por seguridad, cambiala desde tu perfil despues de iniciar sesion.</p>"
        )

        try:
            await send_email(
                to_email=user.email,
                subject="Nueva contraseña temporal",
                html_content=html_content,
            )
        except Exception:
            raise HTTPException(
                status_code=500,
                detail="No se pudo enviar la nueva contraseña al correo",
            )

        user.hashed_password = hash_password(temporary_password)
        self.repo.update(user)

        return None
