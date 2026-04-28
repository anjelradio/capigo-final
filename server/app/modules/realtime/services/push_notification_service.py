import json
import logging
from datetime import UTC, datetime, timedelta

import httpx
import jwt
from sqlmodel import Session

from app.core.config import settings
from app.modules.realtime.models import DevicePushToken
from app.modules.realtime.repositories import DevicePushTokenRepository

logger = logging.getLogger(__name__)


class PushNotificationService:
    def __init__(self, db: Session):
        self.db = db
        self.tokens = DevicePushTokenRepository(db)

    def register_device_token(
        self,
        *,
        user_id,
        platform: str,
        push_token: str,
        device_id: str | None,
    ) -> dict:
        normalized_token = push_token.strip()
        if not normalized_token:
            return {"registered": False, "detail": "push_token_required"}

        normalized_platform = platform.strip().lower() or "android"
        normalized_device_id = device_id.strip() if device_id else None

        existing = self.tokens.get_by_push_token(normalized_token)
        if existing:
            existing.user_id = user_id
            existing.platform = normalized_platform
            existing.device_id = normalized_device_id
            existing.state = True
            self.tokens.save(existing)
            self.db.commit()
            self.db.refresh(existing)
            return {"registered": True, "detail": "token_updated"}

        if normalized_device_id:
            by_device = self.tokens.get_active_by_user_and_device(
                user_id=user_id,
                device_id=normalized_device_id,
            )
            if by_device:
                by_device.push_token = normalized_token
                by_device.platform = normalized_platform
                by_device.state = True
                self.tokens.save(by_device)
                self.db.commit()
                self.db.refresh(by_device)
                return {"registered": True, "detail": "device_token_replaced"}

        token = DevicePushToken(
            user_id=user_id,
            platform=normalized_platform,
            device_id=normalized_device_id,
            push_token=normalized_token,
        )
        self.tokens.create(token)
        self.db.commit()
        self.db.refresh(token)
        return {"registered": True, "detail": "token_created"}

    def notify_user(
        self,
        *,
        user_id,
        title: str,
        body: str,
        data: dict[str, str],
    ) -> dict:
        target_tokens = self.tokens.list_active_by_user(user_id)
        if not target_tokens:
            return {"sent": 0, "failed": 0, "detail": "no_device_tokens"}

        access_token, project_id = self._get_firebase_access_token_and_project()
        if not access_token or not project_id:
            return {"sent": 0, "failed": 0, "detail": "firebase_not_configured"}

        endpoint = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        sent = 0
        failed = 0
        for token in target_tokens:
            payload = {
                "message": {
                    "token": token.push_token,
                    "notification": {
                        "title": title,
                        "body": body,
                    },
                    "data": data,
                }
            }
            try:
                with httpx.Client(timeout=8.0) as client:
                    response = client.post(endpoint, headers=headers, json=payload)
                if 200 <= response.status_code < 300:
                    sent += 1
                    continue

                failed += 1
                logger.warning(
                    "Push send failed status=%s user_id=%s token_id=%s body=%s",
                    response.status_code,
                    user_id,
                    token.id,
                    response.text,
                )
            except Exception as error:
                failed += 1
                logger.warning(
                    "Push send exception user_id=%s token_id=%s error=%s",
                    user_id,
                    token.id,
                    error,
                )

        return {
            "sent": sent,
            "failed": failed,
            "detail": "ok" if sent > 0 else "push_delivery_failed",
        }

    def notify_mechanic_assignment_created(
        self,
        *,
        mechanic_user_id,
        incident_id,
        assignment_id,
    ) -> dict:
        return self.notify_user(
            user_id=mechanic_user_id,
            title="Nuevo servicio asignado",
            body="Tienes un incidente asignado. Toca para ver el monitoreo.",
            data={
                "type": "mechanic.assignment.created",
                "incident_id": str(incident_id),
                "assignment_id": str(assignment_id),
                "route": "/incidents/mechanic/active-service",
            },
        )

    def notify_client_incident_status_changed(
        self,
        *,
        client_user_id,
        incident_id,
        assignment_id,
        status: str,
    ) -> dict:
        title = "Actualizacion de servicio"
        body = "El estado de tu incidente fue actualizado."
        push_type = "client.incident.status.changed"
        route = "/incidents/active-service"

        if status == "on_the_way":
            title = "Tu mecanico va en camino"
            body = "El mecanico ya salio y va rumbo a tu ubicacion."
        elif status == "arrived":
            title = "Tu mecanico ya llego"
            body = "El mecanico ya esta en el punto del incidente."
        elif status == "completed":
            title = "Servicio finalizado"
            body = "Tu servicio finalizo. Cuentanos como fue tu experiencia."
            push_type = "client.incident.review.request"
            route = f"/home/client?reviewIncidentId={incident_id}"
        elif status == "cancelled":
            title = "Servicio cancelado"
            body = "El servicio fue cancelado por el mecanico."

        return self.notify_user(
            user_id=client_user_id,
            title=title,
            body=body,
            data={
                "type": push_type,
                "incident_id": str(incident_id),
                "assignment_id": str(assignment_id),
                "status": status,
                "route": route,
            },
        )

    def _get_firebase_access_token_and_project(self) -> tuple[str | None, str | None]:
        raw_json = settings.FIREBASE_SERVICE_ACCOUNT_JSON.strip()
        if not raw_json:
            return None, None

        try:
            service_account = json.loads(raw_json)
        except Exception as error:
            logger.warning("Invalid FIREBASE_SERVICE_ACCOUNT_JSON error=%s", error)
            return None, None

        client_email = service_account.get("client_email")
        private_key = service_account.get("private_key")
        token_uri = service_account.get("token_uri", "https://oauth2.googleapis.com/token")
        project_id = service_account.get("project_id")

        if not client_email or not private_key or not project_id:
            logger.warning("Firebase service account missing required fields")
            return None, None

        now = datetime.now(UTC)
        claims = {
            "iss": client_email,
            "scope": "https://www.googleapis.com/auth/firebase.messaging",
            "aud": token_uri,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=55)).timestamp()),
        }

        try:
            assertion = jwt.encode(claims, private_key, algorithm="RS256")
        except Exception as error:
            logger.warning("Unable to sign Firebase JWT error=%s", error)
            return None, None

        form_data = {
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": assertion,
        }

        try:
            with httpx.Client(timeout=8.0) as client:
                response = client.post(token_uri, data=form_data)
        except Exception as error:
            logger.warning("Unable to request Firebase access token error=%s", error)
            return None, None

        if response.status_code < 200 or response.status_code >= 300:
            logger.warning(
                "Firebase OAuth failed status=%s body=%s",
                response.status_code,
                response.text,
            )
            return None, None

        payload = response.json()
        access_token = payload.get("access_token")
        if not access_token:
            return None, None

        return access_token, project_id
