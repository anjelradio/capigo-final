import logging
from datetime import UTC, datetime
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

import stripe
from fastapi import HTTPException

from app.core.config import settings
from app.modules.assignments.models import AssignmentStatus
from app.modules.assignments.repositories import RequestAssignmentRepository
from app.modules.incidents.services.client_service_report_email_service import (
    ClientServiceReportEmailService,
)
from app.modules.incidents.models import IncidentStatus
from app.modules.incidents.repositories import IncidentRepository, IncidentServiceReportRepository
from app.modules.incidents.services import IncidentWorkflowService
from app.modules.realtime.services import PushNotificationService
from app.modules.user.models import UserRole
from app.modules.user.repositories import UserRepository
from app.modules.wallet.models import (
    Payment,
    PaymentProvider,
    PaymentStatus,
    TransactionStatus,
    TransactionType,
    Transactions,
)
from app.modules.wallet.repositories import PaymentRepository, WalletRepository

logger = logging.getLogger(__name__)


class PaymentService:
    ZERO_DECIMAL_CURRENCIES = {
        "bif",
        "clp",
        "djf",
        "gnf",
        "jpy",
        "kmf",
        "krw",
        "mga",
        "pyg",
        "rwf",
        "ugx",
        "vnd",
        "vuv",
        "xaf",
        "xof",
        "xpf",
    }

    def __init__(self, db):
        self.db = db
        self.payment = PaymentRepository(db)
        self.incident = IncidentRepository(db)
        self.request_assignment = RequestAssignmentRepository(db)
        self.report = IncidentServiceReportRepository(db)
        self.user = UserRepository(db)
        self.wallet = WalletRepository(db)

    def create_incident_checkout_session(self, *, user_id: UUID, incident_id: UUID) -> dict:
        self._ensure_stripe_configured()
        user = self.user.get_by_id(user_id)
        if not user or user.role != UserRole.CLIENT:
            raise HTTPException(status_code=403, detail="Solo clientes pueden pagar incidentes")

        incident = self.incident.get_by_id_and_user(incident_id, user_id)
        if not incident:
            raise HTTPException(status_code=404, detail="Incidente no encontrado")
        if incident.status != IncidentStatus.PAYMENT_PENDING:
            raise HTTPException(status_code=409, detail="El incidente no esta pendiente de pago")

        assignment = self.request_assignment.get_latest_active_by_incident(incident.id)
        if not assignment or assignment.status != AssignmentStatus.PAYMENT_PENDING:
            raise HTTPException(status_code=404, detail="Asignacion pendiente de pago no encontrada")
        if assignment.final_price is None:
            raise HTTPException(status_code=409, detail="El servicio no tiene precio final registrado")

        amount = self._resolve_payment_total_amount(incident=incident, assignment=assignment)
        if amount <= Decimal("0.00"):
            raise HTTPException(status_code=400, detail="El monto final debe ser mayor a cero")

        open_payment = self.payment.get_latest_open_by_incident(incident.id)
        if open_payment and open_payment.checkout_url and open_payment.stripe_checkout_session_id:
            open_amount = Decimal(str(open_payment.amount)).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            if open_amount == amount and open_payment.currency == settings.STRIPE_CURRENCY.lower():
                return self._checkout_response(open_payment)

            open_payment.status = PaymentStatus.EXPIRED
            self.db.add(open_payment)
            self.db.commit()

        payment = Payment(
            incident_id=incident.id,
            assignment_id=assignment.id,
            user_id=user.id,
            amount=amount,
            currency=settings.STRIPE_CURRENCY.lower(),
            status=PaymentStatus.PENDING,
            provider=PaymentProvider.STRIPE,
        )
        self.payment.create(payment)
        self.db.commit()
        self.db.refresh(payment)

        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            session = stripe.checkout.Session.create(
                mode="payment",
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": payment.currency,
                            "product_data": {
                                "name": "Servicio mecanico Capigo",
                                "description": f"Incidente {incident.id} - mano de obra y traslado",
                            },
                            "unit_amount": self._to_stripe_minor_units(amount, payment.currency),
                        },
                        "quantity": 1,
                    }
                ],
                metadata={
                    "payment_id": str(payment.id),
                    "incident_id": str(incident.id),
                    "assignment_id": str(assignment.id),
                    "user_id": str(user.id),
                },
                success_url=settings.STRIPE_SUCCESS_URL,
                cancel_url=settings.STRIPE_CANCEL_URL,
            )
        except Exception as error:
            payment.status = PaymentStatus.FAILED
            self.db.add(payment)
            self.db.commit()
            logger.exception("No se pudo crear checkout de Stripe payment_id=%s", payment.id)
            raise HTTPException(status_code=502, detail=f"Stripe no pudo crear el checkout: {error}")

        payment.status = PaymentStatus.CHECKOUT_CREATED
        payment.stripe_checkout_session_id = session.id
        payment.checkout_url = session.url
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)

        IncidentWorkflowService(self.db).payment_checkout_created(
            incident=incident,
            assignment=assignment,
            payment=payment,
        )
        return self._checkout_response(payment)

    def get_incident_payment_status(self, *, user_id: UUID, incident_id: UUID) -> dict:
        incident = self.incident.get_by_id_and_user(incident_id, user_id)
        if not incident:
            raise HTTPException(status_code=404, detail="Incidente no encontrado")

        assignment = self.request_assignment.get_latest_by_incident(incident.id)
        payment = self.payment.get_latest_by_incident(incident.id)

        return {
            "payment_id": payment.id if payment else None,
            "incident_id": incident.id,
            "assignment_id": assignment.id if assignment else None,
            "amount": float(payment.amount) if payment else None,
            "currency": payment.currency if payment else None,
            "status": payment.status.value if payment else None,
            "checkout_session_id": payment.stripe_checkout_session_id if payment else None,
            "checkout_url": payment.checkout_url if payment else None,
            "paid_at": payment.paid_at if payment else None,
            "incident_status": incident.status.value,
            "assignment_status": assignment.status.value if assignment else None,
        }

    def verify_checkout_session(self, *, session_id: str, user_id: UUID | None = None) -> dict:
        self._ensure_stripe_configured()
        normalized_session_id = session_id.strip()
        if not normalized_session_id:
            raise HTTPException(status_code=400, detail="session_id requerido")

        payment = self.payment.get_by_stripe_checkout_session_id(normalized_session_id)
        if not payment:
            raise HTTPException(status_code=404, detail="Pago no encontrado")
        if user_id is not None and payment.user_id != user_id:
            raise HTTPException(status_code=403, detail="No autorizado para verificar este pago")

        if payment.status == PaymentStatus.PAID:
            return self._verify_response(payment=payment, paid=True, detail="Pago ya confirmado")

        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            session = stripe.checkout.Session.retrieve(normalized_session_id)
        except Exception as error:
            logger.exception("No se pudo verificar checkout de Stripe session_id=%s", normalized_session_id)
            raise HTTPException(status_code=502, detail=f"Stripe no pudo verificar el pago: {error}")

        payment_intent_id = getattr(session, "payment_intent", None)
        if payment_intent_id:
            payment.stripe_payment_intent_id = str(payment_intent_id)

        if getattr(session, "payment_status", None) != "paid":
            self.db.add(payment)
            self.db.commit()
            return self._verify_response(
                payment=payment,
                paid=False,
                detail="El pago aun no fue confirmado por Stripe",
            )

        return self._mark_payment_paid(payment)

    def cancel_checkout_session(self, *, session_id: str) -> dict:
        payment = self.payment.get_by_stripe_checkout_session_id(session_id.strip())
        if not payment:
            raise HTTPException(status_code=404, detail="Pago no encontrado")
        if payment.status != PaymentStatus.PAID:
            payment.status = PaymentStatus.CANCELLED
            self.db.add(payment)
            self.db.commit()
        return self._verify_response(payment=payment, paid=False, detail="Pago cancelado")

    def _mark_payment_paid(self, payment: Payment) -> dict:
        incident = self.incident.get_by_id(payment.incident_id)
        assignment = self.request_assignment.get_by_id(payment.assignment_id)
        if not incident or not assignment:
            raise HTTPException(status_code=404, detail="Incidente o asignacion no encontrados")

        payment.status = PaymentStatus.PAID
        payment.paid_at = datetime.now(UTC).replace(tzinfo=None)
        self.db.add(payment)

        incident.status = IncidentStatus.COMPLETED
        self.db.add(incident)

        assignment.status = AssignmentStatus.COMPLETED
        assignment.responded_at = datetime.now(UTC)
        self.db.add(assignment)

        wallet_snapshot = self._debit_shop_wallet_if_possible(assignment=assignment)
        self.db.commit()
        self.db.refresh(payment)

        IncidentWorkflowService(self.db).payment_completed(
            incident=incident,
            assignment=assignment,
            payment=payment,
            wallet_snapshot=wallet_snapshot,
        )
        self._send_client_completed_push(incident=incident, assignment=assignment)
        self._send_client_service_report_email(
            incident=incident,
            assignment=assignment,
            payment=payment,
        )
        return self._verify_response(payment=payment, paid=True, detail="Pago confirmado")

    def _debit_shop_wallet_if_possible(self, *, assignment) -> dict | None:
        debit_amount = self._resolve_delivery_charge(assignment)
        if debit_amount <= Decimal("0.00"):
            return None

        wallet = self.wallet.get_active_by_repair_shop_id(assignment.repair_shop_id)
        if not wallet:
            logger.warning(
                "No se encontro billetera activa para debito de servicio shop_id=%s assignment_id=%s",
                assignment.repair_shop_id,
                assignment.id,
            )
            return None

        balance_before = Decimal(str(wallet.balance)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        balance_after = (balance_before - debit_amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        wallet.balance = balance_after
        wallet.modified_date = datetime.utcnow()
        self.db.add(wallet)

        transaction = Transactions(
            type=TransactionType.DEBIT_SERVICE,
            status=TransactionStatus.POSTED,
            amount=debit_amount,
            balance_before=balance_before,
            balance_after=balance_after,
            description=f"Debito por servicio pagado assignment_id={assignment.id}",
            wallet_id=wallet.id,
        )
        self.db.add(transaction)
        return {
            "balance_before": balance_before,
            "balance_after": balance_after,
            "debit_amount": debit_amount,
        }

    def _resolve_delivery_charge(self, assignment) -> Decimal:
        source_value = assignment.delivery_price
        if source_value is None:
            return Decimal("0.00")
        return Decimal(str(source_value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _resolve_payment_total_amount(self, *, incident, assignment) -> Decimal:
        final_price = Decimal(str(assignment.final_price)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        delivery_charge = self._resolve_payment_delivery_charge(
            incident=incident,
            assignment=assignment,
        )
        return (final_price + delivery_charge).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    def _resolve_payment_delivery_charge(self, *, incident, assignment) -> Decimal:
        source_value = incident.delivery_price
        if source_value is None:
            source_value = assignment.delivery_price
        if source_value is None:
            return Decimal("0.00")
        return Decimal(str(source_value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _send_client_completed_push(self, *, incident, assignment) -> None:
        try:
            PushNotificationService(self.db).notify_client_incident_status_changed(
                client_user_id=incident.user_id,
                incident_id=incident.id,
                assignment_id=assignment.id,
                status=IncidentStatus.COMPLETED.value,
            )
        except Exception as error:
            logger.warning(
                "No se pudo enviar push de pago completado user_id=%s incident_id=%s error=%s",
                incident.user_id,
                incident.id,
                error,
            )

    def _send_client_service_report_email(self, *, incident, assignment, payment) -> None:
        try:
            ClientServiceReportEmailService(self.db).send_payment_completed_email(
                incident=incident,
                assignment=assignment,
                payment=payment,
            )
        except Exception as error:
            logger.warning(
                "No se pudo enviar el comprobante por correo incident_id=%s payment_id=%s error=%s",
                incident.id,
                payment.id,
                error,
            )

    def _ensure_stripe_configured(self) -> None:
        if not settings.STRIPE_SECRET_KEY:
            raise HTTPException(status_code=500, detail="STRIPE_SECRET_KEY no esta configurado")
        if not settings.STRIPE_SUCCESS_URL or not settings.STRIPE_CANCEL_URL:
            raise HTTPException(status_code=500, detail="URLs de Stripe no configuradas")

    def _to_stripe_minor_units(self, amount: Decimal, currency: str) -> int:
        if currency.lower() in self.ZERO_DECIMAL_CURRENCIES:
            return int(amount.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        return int((amount * Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP))

    def _checkout_response(self, payment: Payment) -> dict:
        return {
            "payment_id": payment.id,
            "checkout_session_id": payment.stripe_checkout_session_id,
            "checkout_url": payment.checkout_url,
            "amount": float(payment.amount),
            "currency": payment.currency,
            "status": payment.status.value,
        }

    def _verify_response(self, *, payment: Payment, paid: bool, detail: str) -> dict:
        incident = self.incident.get_by_id(payment.incident_id)
        assignment = self.request_assignment.get_by_id(payment.assignment_id)
        return {
            "payment_id": payment.id,
            "incident_id": payment.incident_id,
            "assignment_id": payment.assignment_id,
            "payment_status": payment.status.value,
            "incident_status": incident.status.value if incident else "unknown",
            "assignment_status": assignment.status.value if assignment else "unknown",
            "paid": paid,
            "detail": detail,
        }
