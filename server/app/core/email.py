import base64
from collections.abc import Sequence

import httpx

from app.core.config import settings


def _encode_attachments(
    attachments: Sequence[dict[str, object]] | None,
) -> list[dict[str, str]] | None:
    if not attachments:
        return None

    encoded_attachments: list[dict[str, str]] = []
    for attachment in attachments:
        raw_content = attachment.get("content")
        if raw_content is None:
            continue

        if isinstance(raw_content, str):
            content_bytes = raw_content.encode("utf-8")
        else:
            content_bytes = bytes(raw_content)

        encoded_attachments.append(
            {
                "name": str(attachment.get("name") or "adjunto.pdf"),
                "content": base64.b64encode(content_bytes).decode("ascii"),
            }
        )

    return encoded_attachments or None


def _build_payload(
    *,
    to_email: str,
    subject: str,
    html_content: str,
    attachments: Sequence[dict[str, object]] | None = None,
) -> dict:
    payload: dict = {
        "sender": {
            "name": settings.BREVO_SENDER_NAME,
            "email": settings.BREVO_SENDER_EMAIL,
        },
        "to": [{"email": to_email}],
        "subject": subject,
        "htmlContent": html_content,
    }

    encoded_attachments = _encode_attachments(attachments)
    if encoded_attachments:
        payload["attachment"] = encoded_attachments

    return payload


def _raise_for_response(response: httpx.Response) -> None:
    if response.status_code < 400:
        return

    body = response.text.strip()
    if len(body) > 1000:
        body = f"{body[:1000]}..."

    raise RuntimeError(
        f"No se pudo enviar el correo (status={response.status_code}): {body}"
    )


async def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    attachments: Sequence[dict[str, object]] | None = None,
) -> None:
    payload = _build_payload(
        to_email=to_email,
        subject=subject,
        html_content=html_content,
        attachments=attachments,
    )

    headers = {
        "api-key": settings.BREVO_API_KEY,
        "accept": "application/json",
        "content-type": "application/json",
    }

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(
            "https://api.brevo.com/v3/smtp/email", json=payload, headers=headers
        )

    _raise_for_response(response)


def send_email_sync(
    to_email: str,
    subject: str,
    html_content: str,
    attachments: Sequence[dict[str, object]] | None = None,
) -> None:
    payload = _build_payload(
        to_email=to_email,
        subject=subject,
        html_content=html_content,
        attachments=attachments,
    )

    headers = {
        "api-key": settings.BREVO_API_KEY,
        "accept": "application/json",
        "content-type": "application/json",
    }

    with httpx.Client(timeout=10) as client:
        response = client.post(
            "https://api.brevo.com/v3/smtp/email", json=payload, headers=headers
        )

    _raise_for_response(response)
