import asyncio
import logging
from contextlib import asynccontextmanager
from contextlib import suppress

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from app.core.config import settings
from app.core.db import engine, init_db
from app.modules.assignments.router import router as assignments_router
from app.modules.auth.router import router as auth_router
from app.modules.incidents.router import router as incidents_router
from app.modules.realtime.router import router as realtime_router
from app.modules.realtime.models import DevicePushToken, IncidentLiveState, IncidentRealtimeEvent
from app.modules.realtime.services import ShopOfferNotificationService
from app.modules.repair_shop.router import router as repair_shop_router
from app.modules.user.router import router as user_router
from app.modules.wallet.payment_router import router as payments_router
from app.modules.wallet.router import router as wallet_router

load_dotenv()
logger = logging.getLogger(__name__)


async def _assignment_queue_timeout_worker() -> None:
    sweep_sec = max(settings.ASSIGNMENT_QUEUE_SWEEP_SEC, 2)
    while True:
        try:
            with Session(engine) as db:
                await ShopOfferNotificationService(db).expire_overdue_offers_and_notify_next()
        except Exception:
            logger.exception("Error procesando expiraciones de ofertas en cola")

        await asyncio.sleep(sweep_sec)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.ENVIRONMENT == "DEV":
        init_db()

    queue_worker = asyncio.create_task(_assignment_queue_timeout_worker())

    try:
        yield
    finally:
        queue_worker.cancel()
        with suppress(asyncio.CancelledError):
            await queue_worker


app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
    swagger_ui_parameters={
        "persistAuthorization": True,
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(repair_shop_router, prefix="/api")
app.include_router(incidents_router, prefix="/api")
app.include_router(assignments_router, prefix="/api")
app.include_router(realtime_router, prefix="/api")
app.include_router(wallet_router, prefix="/api")
app.include_router(payments_router, prefix="/api")
