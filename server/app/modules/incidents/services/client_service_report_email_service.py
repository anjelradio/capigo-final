import logging
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import settings
from app.core.email import send_email_sync
from app.modules.user.repositories import UserRepository
from app.modules.wallet.models import Payment

from .client_service_report_pdf_service import ClientServiceReportPdfService

logger = logging.getLogger(__name__)


class ClientServiceReportEmailService:
    def __init__(self, db):
        self.user = UserRepository(db)
        self.report_pdf = ClientServiceReportPdfService(db)
        templates_dir = Path(__file__).resolve().parents[3] / "templates"
        self.template_env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def send_payment_completed_email(self, *, incident, assignment, payment: Payment) -> None:
        client = self.user.get_by_id(incident.user_id)
        if not client or not str(client.email).strip():
            logger.warning(
                "No se encontro correo del cliente para enviar comprobante incident_id=%s",
                incident.id,
            )
            return

        client_name = self._build_client_name(client.first_name, client.last_name)
        report_package = self.report_pdf.build_payment_completion_report(
            payment=payment,
            client_name=client_name,
        )
        context = {
            **report_package["context"],
            "support_email": settings.BREVO_SENDER_EMAIL,
        }

        html_content = self._render_template("emails/service_completed.html", context)
        subject = f"Informe y comprobante de servicio CapiGO - {context['incident_short_id']}"

        send_email_sync(
            to_email=str(client.email).strip().lower(),
            subject=subject,
            html_content=html_content,
            attachments=[
                {
                    "name": report_package["filename"],
                    "content": report_package["pdf_bytes"],
                }
            ],
        )

    def _render_template(self, template_name: str, context: dict) -> str:
        template = self.template_env.get_template(template_name)
        return template.render(**context)

    def _build_client_name(self, first_name: str | None, last_name: str | None) -> str:
        parts = [str(first_name or "").strip(), str(last_name or "").strip()]
        name = " ".join(part for part in parts if part)
        return name or "Cliente"
