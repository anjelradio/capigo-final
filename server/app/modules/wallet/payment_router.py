from uuid import UUID

from fastapi import APIRouter, status
from fastapi.responses import HTMLResponse

from app.dependencies.auth import CurrentUser, DBSession
from app.modules.wallet.schemas import (
    PaymentCheckoutSessionRead,
    PaymentStatusRead,
    PaymentVerifyResponse,
)
from app.modules.wallet.services import PaymentService

router = APIRouter(prefix="/payments", tags=["Pagos"])


@router.post(
    "/incidents/{incident_id}/checkout-session",
    response_model=PaymentCheckoutSessionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_incident_checkout_session(db: DBSession, user: CurrentUser, incident_id: UUID):
    return PaymentService(db).create_incident_checkout_session(
        user_id=user.id,
        incident_id=incident_id,
    )


@router.get(
    "/incidents/{incident_id}/status",
    response_model=PaymentStatusRead,
    status_code=status.HTTP_200_OK,
)
def get_incident_payment_status(db: DBSession, user: CurrentUser, incident_id: UUID):
    return PaymentService(db).get_incident_payment_status(
        user_id=user.id,
        incident_id=incident_id,
    )


@router.post(
    "/stripe/checkout-sessions/{session_id}/verify",
    response_model=PaymentVerifyResponse,
    status_code=status.HTTP_200_OK,
)
def verify_checkout_session(db: DBSession, user: CurrentUser, session_id: str):
    return PaymentService(db).verify_checkout_session(session_id=session_id, user_id=user.id)


@router.get("/stripe/success", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
def stripe_success(db: DBSession, session_id: str):
    try:
        result = PaymentService(db).verify_checkout_session(session_id=session_id)
        title = "Pago confirmado" if result["paid"] else "Pago pendiente"
        message = result["detail"]
    except Exception as error:
        title = "No se pudo confirmar el pago"
        message = str(error)
    return _result_page(title=title, message=message)


@router.get("/stripe/cancel", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
def stripe_cancel(db: DBSession, session_id: str):
    try:
        PaymentService(db).cancel_checkout_session(session_id=session_id)
        message = "El pago fue cancelado. Puedes volver a la aplicacion."
    except Exception as error:
        message = str(error)
    return _result_page(title="Pago cancelado", message=message)


def _result_page(*, title: str, message: str) -> str:
    return f"""
    <!doctype html>
    <html lang="es">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>{title}</title>
        <style>
          body {{ font-family: system-ui, sans-serif; padding: 32px; background: #111827; color: #f9fafb; }}
          main {{ max-width: 520px; margin: 0 auto; padding: 28px; border-radius: 20px; background: #1f2937; }}
          h1 {{ margin-top: 0; }}
          p {{ color: #d1d5db; line-height: 1.5; }}
        </style>
      </head>
      <body>
        <main>
          <h1>{title}</h1>
          <p>{message}</p>
          <p>Ya puedes volver a Capigo.</p>
        </main>
      </body>
    </html>
    """
