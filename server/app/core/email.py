import httpx

from app.core.config import settings


async def send_email(to_email: str, subject: str, html_content: str) -> None:
    payload = {
        "sender": {
            "name": settings.BREVO_SENDER_NAME,
            "email": settings.BREVO_SENDER_EMAIL,
        },
        "to": [{"email": to_email}],
        "subject": subject,
        "htmlContent": html_content,
    }

    headers = {
        "api-key": settings.BREVO_API_KEY,
        "accept": "application/json",
        "content-type": "application/json",
    }

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(
            "https://api.brevo.com/v3/smtp/email", json=payload, headers=headers
        )

    if response.status_code >= 400:
        raise RuntimeError("No se pudo enviar el correo OTP")
