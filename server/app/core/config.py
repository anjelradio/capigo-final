from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    JWT_SECRET: str = Field(..., env="JWT_SECRET")
    JWT_ALG: str = Field(default="HS256", env="JWT_ALG")
    JWT_EXPIRES_MIN: int = Field(default=60 * 24, env="JWT_EXPIRES_MIN")

    BREVO_API_KEY: str = Field(..., env="BREVO_API_KEY")
    BREVO_SENDER_EMAIL: str = Field(..., env="BREVO_SENDER_EMAIL")
    BREVO_SENDER_NAME: str = Field(default="LoomBo", env="BREVO_SENDER_NAME")

    OTP_LENGTH: int = Field(default=6, env="OTP_LENGTH")
    OTP_EXPIRES_MIN: int = Field(default=5, env="OTP_EXPIRES_MIN")
    OTP_MAX_ATTEMPTS: int = Field(default=5, env="OTP_MAX_ATTEMPTS")
    OTP_RESEND_COOLDOWN_SEC: int = Field(default=60, env="OTP_RESEND_COOLDOWN_SEC")

    REDIS_URL: str = Field(..., env="REDIS_URL")

    GEMINI_API_KEY: str = Field(default="", env="GEMINI_API_KEY")
    GEMINI_MODEL: str = Field(default="gemini-2.5-flash", env="GEMINI_MODEL")
    GEMINI_MODEL_FALLBACKS: list[str] = Field(
        default_factory=lambda: ["gemini-2.5-flash-lite", "gemini-3-flash"],
        env="GEMINI_MODEL_FALLBACKS",
    )
    OPENAI_API_KEY: str = Field(default="", env="OPENAI_API_KEY")
    CLOUDINARY_CLOUD_NAME: str = Field(default="", env="CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY: str = Field(default="", env="CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET: str = Field(default="", env="CLOUDINARY_API_SECRET")
    FIREBASE_SERVICE_ACCOUNT_JSON: str = Field(default="", env="FIREBASE_SERVICE_ACCOUNT_JSON")

    ASSIGNMENT_OFFER_TIMEOUT_SEC: int = Field(default=45, env="ASSIGNMENT_OFFER_TIMEOUT_SEC")
    ASSIGNMENT_QUEUE_SWEEP_SEC: int = Field(default=5, env="ASSIGNMENT_QUEUE_SWEEP_SEC")
    ASSIGNMENT_BASE_FEE_BOB: float = Field(default=5.0, env="ASSIGNMENT_BASE_FEE_BOB")
    ASSIGNMENT_PRICE_PER_KM_BOB: float = Field(
        default=2.5,
        env="ASSIGNMENT_PRICE_PER_KM_BOB",
    )
    ASSIGNMENT_ESTIMATED_SPEED_KMH: float = Field(
        default=28.0,
        env="ASSIGNMENT_ESTIMATED_SPEED_KMH",
    )
    ASSIGNMENT_ESTIMATED_MIN_FLOOR_MINUTES: int = Field(
        default=5,
        env="ASSIGNMENT_ESTIMATED_MIN_FLOOR_MINUTES",
    )
    STRIPE_SECRET_KEY: str = Field(default="", env="STRIPE_SECRET_KEY")
    STRIPE_CURRENCY: str = Field(default="usd", env="STRIPE_CURRENCY")
    STRIPE_SUCCESS_URL: str = Field(default="", env="STRIPE_SUCCESS_URL")
    STRIPE_CANCEL_URL: str = Field(default="", env="STRIPE_CANCEL_URL")
    SQL_ECHO: bool = Field(default=False, env="SQL_ECHO")
    CORS_ORIGINS: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:4200",
            "http://127.0.0.1:4200",
            "https://capigo-final.vercel.app",
        ],
        env="CORS_ORIGINS",
    )

    PROJECT_NAME: str = "App Project"
    ENVIRONMENT: str = Field(..., env="ENVIRONMENT")

    LANGUAGE_CODE: str = "es"
    TIME_ZONE: str = "America/La_Paz"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.startswith("["):
                return value
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("GEMINI_MODEL_FALLBACKS", mode="before")
    @classmethod
    def parse_gemini_model_fallbacks(cls, value):
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.startswith("["):
                return value
            return [model.strip() for model in value.split(",") if model.strip()]
        return value

    @property
    def database_url_normalized(self) -> str:
        url = self.DATABASE_URL.strip()
        if url.startswith("postgres://"):
            return "postgresql+psycopg://" + url[len("postgres://") :]
        if url.startswith("postgresql://") and "+psycopg" not in url:
            return "postgresql+psycopg://" + url[len("postgresql://") :]
        return url

    @field_validator("ASSIGNMENT_BASE_FEE_BOB", "ASSIGNMENT_PRICE_PER_KM_BOB")
    @classmethod
    def validate_assignment_price_params(cls, value: float) -> float:
        if value < 0:
            raise ValueError("Los parametros de cobro no pueden ser negativos")
        return value

    @field_validator("ASSIGNMENT_ESTIMATED_SPEED_KMH")
    @classmethod
    def validate_assignment_speed_kmh(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("ASSIGNMENT_ESTIMATED_SPEED_KMH debe ser mayor a 0")
        return value

    @field_validator("ASSIGNMENT_ESTIMATED_MIN_FLOOR_MINUTES")
    @classmethod
    def validate_assignment_min_floor_minutes(cls, value: int) -> int:
        if value < 0:
            raise ValueError("ASSIGNMENT_ESTIMATED_MIN_FLOOR_MINUTES no puede ser negativo")
        return value

    class Config:
        env_file = ".env"

settings = Settings()
