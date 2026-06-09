import hashlib
import time
from uuid import UUID

from fastapi import HTTPException, UploadFile
import httpx
from sqlmodel import Session

from app.core.config import settings


class CloudinaryUploadService:
    def __init__(self, db: Session):
        self.db = db

    def upload_photos(
        self,
        incident_id: UUID,
        photos: list[UploadFile],
    ) -> list[str]:
        uploaded_urls: list[str] = []
        for photo in photos:
            if not str(photo.content_type or "").startswith("image/"):
                raise HTTPException(
                    status_code=400,
                    detail="Solo se permiten imagenes en evidencias del incidente",
                )

            photo_bytes = photo.file.read()
            if not photo_bytes:
                raise HTTPException(status_code=400, detail="Una imagen enviada esta vacia")

            uploaded_urls.append(
                self._upload_to_cloudinary(
                    incident_id=incident_id,
                    file_name=photo.filename or "photo.jpg",
                    content_type=photo.content_type or "image/jpeg",
                    content=photo_bytes,
                )
            )

        return uploaded_urls

    def _upload_to_cloudinary(
        self,
        incident_id: UUID,
        file_name: str,
        content_type: str,
        content: bytes,
    ) -> str:
        missing_vars: list[str] = []
        if not settings.CLOUDINARY_CLOUD_NAME:
            missing_vars.append("CLOUDINARY_CLOUD_NAME")
        if not settings.CLOUDINARY_API_KEY:
            missing_vars.append("CLOUDINARY_API_KEY")
        if not settings.CLOUDINARY_API_SECRET:
            missing_vars.append("CLOUDINARY_API_SECRET")

        if missing_vars:
            raise HTTPException(
                status_code=500,
                detail=(
                    "Cloudinary no esta configurado correctamente. "
                    f"Faltan: {', '.join(missing_vars)}"
                ),
            )

        timestamp = int(time.time())
        folder = f"apico/evidences/{incident_id}"
        public_id = hashlib.sha1(content).hexdigest()
        params_to_sign = (
            f"folder={folder}"
            f"&public_id={public_id}"
            f"&timestamp={timestamp}{settings.CLOUDINARY_API_SECRET}"
        )
        signature = hashlib.sha1(params_to_sign.encode("utf-8")).hexdigest()

        endpoint = (
            f"https://api.cloudinary.com/v1_1/{settings.CLOUDINARY_CLOUD_NAME}/image/upload"
        )
        files = {
            "file": (file_name, content, content_type),
        }
        data = {
            "api_key": settings.CLOUDINARY_API_KEY,
            "timestamp": str(timestamp),
            "folder": folder,
            "public_id": public_id,
            "signature": signature,
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(endpoint, data=data, files=files)
                response.raise_for_status()
            payload = response.json()
        except httpx.HTTPStatusError as error:
            cloudinary_error = ""
            try:
                cloudinary_payload = error.response.json()
                cloudinary_error = str(cloudinary_payload.get("error", {}).get("message", ""))
            except Exception:
                cloudinary_error = error.response.text

            cloudinary_error = cloudinary_error.strip() or "Sin detalle"
            raise HTTPException(
                status_code=502,
                detail=(
                    "No fue posible subir una imagen a Cloudinary. "
                    f"status={error.response.status_code} detail={cloudinary_error}"
                ),
            )
        except Exception:
            raise HTTPException(
                status_code=502,
                detail="No fue posible subir una imagen a Cloudinary",
            )

        secure_url = str(payload.get("secure_url") or "").strip()
        if not secure_url:
            raise HTTPException(
                status_code=502,
                detail="Cloudinary no devolvio una URL valida",
            )

        return secure_url
