import logging
import stripe
from fastapi import HTTPException

from app.core.config import settings

logger = logging.getLogger(__name__)


class StripeService:
    def __init__(self):
        if not settings.STRIPE_SECRET_KEY:
            raise HTTPException(status_code=500, detail="STRIPE_SECRET_KEY no configurado")
        stripe.api_key = settings.STRIPE_SECRET_KEY

    def create_checkout_session(
        self,
        *,
        currency: str,
        amount_minor_units: int,
        incident_id: str,
        payment_id: str,
        assignment_id: str,
        user_id: str,
        product_name: str = "Servicio mecanico Capigo",
        product_description: str = "",
    ):
        try:
            session = stripe.checkout.Session.create(
                mode="payment",
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": currency,
                            "product_data": {
                                "name": product_name,
                                "description": product_description,
                            },
                            "unit_amount": amount_minor_units,
                        },
                        "quantity": 1,
                    }
                ],
                metadata={
                    "payment_id": payment_id,
                    "incident_id": incident_id,
                    "assignment_id": assignment_id,
                    "user_id": user_id,
                },
                success_url=settings.STRIPE_SUCCESS_URL,
                cancel_url=settings.STRIPE_CANCEL_URL,
            )
            return session
        except Exception as error:
            logger.exception("No se pudo crear checkout de Stripe")
            raise HTTPException(status_code=502, detail=f"Stripe no pudo crear el checkout: {error}")

    def retrieve_checkout_session(self, session_id: str):
        try:
            return stripe.checkout.Session.retrieve(session_id)
        except Exception as error:
            logger.exception("No se pudo verificar checkout de Stripe session_id=%s", session_id)
            raise HTTPException(status_code=502, detail=f"Stripe no pudo verificar el pago: {error}")
