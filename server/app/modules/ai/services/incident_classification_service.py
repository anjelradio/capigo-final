import base64
import json
import logging
from uuid import UUID

import httpx
from fastapi import HTTPException
from sqlmodel import Session, select

from app.core.config import settings
from app.core.db import engine
from app.modules.incidents.models import Incident, IncidentStatus, Problem
from app.modules.incidents.repositories import EvidenceRepository, IncidentRepository

logger = logging.getLogger(__name__)


class IncidentClassificationService:
    MIN_CONFIDENCE = 0.70
    GEMINI_MODEL = "gemini-2.5-flash"
    MAX_EVIDENCE_IMAGES = 3
    RETRYABLE_GEMINI_STATUS_CODES = {429, 500, 502, 503, 504}

    def __init__(self, db: Session):
        self.db = db
        self.incident = IncidentRepository(db)
        self.evidence = EvidenceRepository(db)

    @classmethod
    def classify_incident_background(
        cls,
        incident_id: UUID,
        audio_payload: dict | None = None,
    ) -> None:
        with Session(engine) as db:
            service = cls(db)
            try:
                service.classify_incident(incident_id, audio_payload=audio_payload)
            except Exception as error:
                logger.warning(
                    "No se pudo clasificar incidente en background id=%s error=%s",
                    incident_id,
                    error,
                )

    def classify_incident(self, incident_id: UUID, audio_payload: dict | None = None) -> dict:
        incident = self._get_incident_or_404(incident_id)
        self._mark_incident_classifying(incident)

        try:
            payload = self._classify_with_gemini(incident, audio_payload=audio_payload)
            resolved = self._persist_classification_result(incident, payload)

            if resolved["accepted_threshold"]:
                from app.modules.assignments.services import AssignmentOrchestratorService

                AssignmentOrchestratorService(self.db).run_after_classification(incident.id)

            return resolved
        except HTTPException:
            self._mark_incident_failed(incident)
            raise
        except Exception:
            self._mark_incident_failed(incident)
            raise HTTPException(
                status_code=502,
                detail="No fue posible clasificar el incidente con IA",
            )

    def _get_incident_or_404(self, incident_id: UUID) -> Incident:
        query = select(Incident).where(Incident.id == incident_id, Incident.state == True)
        incident = self.db.exec(query).first()
        if not incident:
            raise HTTPException(status_code=404, detail="Incidente no encontrado")
        return incident

    def _mark_incident_classifying(self, incident: Incident) -> None:
        incident.status = IncidentStatus.CLASSIFYING
        incident.ai_attempts += 1
        self.db.add(incident)
        self.db.commit()
        self.db.refresh(incident)
        self._emit_incident_realtime_event(
            incident_id=incident.id,
            event_type="incident.status.changed",
            payload={
                "status": incident.status,
                "description": "Clasificando incidente con IA",
            },
            status=incident.status,
        )

    def _mark_incident_failed(self, incident: Incident) -> None:
        incident.status = IncidentStatus.FAILED
        self.db.add(incident)
        self.db.commit()
        self._emit_incident_realtime_event(
            incident_id=incident.id,
            event_type="incident.status.changed",
            payload={
                "status": incident.status,
                "description": "No se pudo clasificar el incidente",
            },
            status=incident.status,
        )

    def _classify_with_gemini(self, incident: Incident, audio_payload: dict | None = None) -> dict:
        if not settings.GEMINI_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="GEMINI_API_KEY no esta configurada",
            )

        problems = self._get_active_problems_catalog()
        if not problems:
            raise HTTPException(
                status_code=400,
                detail="No hay problemas cargados para clasificar incidentes",
            )

        prompt = self._build_classification_prompt(incident.description or "", problems)
        parts = [{"text": prompt}] + self._build_evidence_image_parts(incident.id)

        audio_part = self._build_audio_part(audio_payload)
        if audio_part:
            parts.append(audio_part)

        payload = {
            "contents": [{"role": "user", "parts": parts}],
            "generationConfig": {"responseMimeType": "application/json"},
        }

        body = self._request_gemini_with_fallback(payload)

        text = self._extract_text_from_gemini_response(body)
        parsed = self._parse_gemini_json_result(text)
        return {
            "situation_summary": str(parsed.get("situation_summary") or "").strip(),
            "problem_id": str(parsed.get("problem_id", "")).strip(),
            "confidence": self._normalize_confidence(parsed.get("confidence")),
        }

    def _request_gemini_with_fallback(self, payload: dict) -> dict:
        models = self._resolve_gemini_models()
        attempts: list[str] = []

        for index, model in enumerate(models):
            endpoint = (
                "https://generativelanguage.googleapis.com/v1beta/models/"
                f"{model}:generateContent?key={settings.GEMINI_API_KEY}"
            )

            try:
                with httpx.Client(timeout=45.0) as client:
                    response = client.post(endpoint, json=payload)
                    response.raise_for_status()

                logger.info("Gemini clasificacion exitosa con modelo=%s", model)
                return response.json()
            except httpx.HTTPStatusError as error:
                status_code = error.response.status_code
                detail = error.response.text.strip() or "Sin detalle"
                attempts.append(f"model={model} status={status_code}")

                is_retryable = status_code in self.RETRYABLE_GEMINI_STATUS_CODES
                has_next_model = index < len(models) - 1
                logger.warning(
                    "Gemini rechazo clasificacion model=%s status=%s retryable=%s detail=%s",
                    model,
                    status_code,
                    is_retryable,
                    detail,
                )

                if is_retryable and has_next_model:
                    continue

                raise HTTPException(
                    status_code=502,
                    detail=(
                        "Gemini rechazo la solicitud de clasificacion. "
                        f"model={model} status={status_code} detail={detail}"
                    ),
                )
            except Exception as error:
                attempts.append(f"model={model} network_error={type(error).__name__}")
                has_next_model = index < len(models) - 1
                logger.warning(
                    "No se pudo conectar con Gemini model=%s error=%s",
                    model,
                    error,
                )

                if has_next_model:
                    continue

                raise HTTPException(
                    status_code=502,
                    detail="No fue posible obtener respuesta de Gemini",
                )

        attempts_text = " | ".join(attempts) if attempts else "sin_intentos"
        raise HTTPException(
            status_code=502,
            detail=(
                "No fue posible clasificar el incidente con ningun modelo Gemini. "
                f"attempts={attempts_text}"
            ),
        )

    def _resolve_gemini_models(self) -> list[str]:
        ordered_candidates = [
            settings.GEMINI_MODEL or self.GEMINI_MODEL,
            *settings.GEMINI_MODEL_FALLBACKS,
        ]
        models: list[str] = []
        for model in ordered_candidates:
            normalized = str(model or "").strip()
            if not normalized or normalized in models:
                continue
            models.append(normalized)

        return models or [self.GEMINI_MODEL]

    def _persist_classification_result(self, incident: Incident, payload: dict) -> dict:
        problem_id = payload["problem_id"]
        confidence = payload["confidence"]
        situation_summary = str(payload.get("situation_summary") or "").strip()

        incident.ai_confidence = confidence
        if situation_summary:
            incident.description = situation_summary

        selected_problem = self._find_problem_by_id(problem_id)
        if not selected_problem:
            incident.status = IncidentStatus.FAILED
            self.db.add(incident)
            self.db.commit()
            raise HTTPException(
                status_code=400,
                detail="Gemini devolvio un problem_id que no existe en el catalogo",
            )

        incident.problem_id = selected_problem.id
        incident.status = (
            IncidentStatus.CLASSIFIED
            if confidence >= self.MIN_CONFIDENCE
            else IncidentStatus.FAILED
        )

        self.db.add(incident)
        self.db.commit()
        self.db.refresh(incident)

        self._emit_incident_realtime_event(
            incident_id=incident.id,
            event_type="incident.status.changed",
            payload={
                "status": incident.status,
                "problem_id": incident.problem_id,
                "confidence": incident.ai_confidence,
                "description": "Clasificacion de incidente finalizada",
            },
            status=incident.status,
        )

        return {
            "incident_id": incident.id,
            "status": incident.status,
            "problem_id": incident.problem_id,
            "ai_confidence": incident.ai_confidence,
            "accepted_threshold": confidence >= self.MIN_CONFIDENCE,
        }

    def _emit_incident_realtime_event(
        self,
        *,
        incident_id: UUID,
        event_type: str,
        payload: dict,
        status: str | None = None,
    ) -> None:
        try:
            from app.modules.realtime.services.incident_realtime_service import (
                IncidentRealtimeService,
            )

            IncidentRealtimeService(self.db).publish_incident_event_sync(
                incident_id=incident_id,
                event_type=event_type,
                payload=payload,
                status=status,
            )
        except Exception as error:
            try:
                self.db.rollback()
            except Exception:
                pass
            logger.warning(
                "No se pudo emitir evento realtime incident_id=%s type=%s error=%s",
                incident_id,
                event_type,
                error,
            )

    def _get_active_problems_catalog(self) -> list[Problem]:
        query = (
            select(Problem)
            .where(Problem.state == True)
            .order_by(Problem.name.asc())
        )
        return list(self.db.exec(query).all())

    def _find_problem_by_id(self, problem_id: str) -> Problem | None:
        try:
            parsed_problem_id = UUID(problem_id)
        except Exception:
            return None

        query = select(Problem).where(
            Problem.id == parsed_problem_id,
            Problem.state == True,
        )
        return self.db.exec(query).first()

    def _build_classification_prompt(self, description: str, problems: list[Problem]) -> str:
        catalog_lines = []
        for problem in problems:
            detail = (problem.description or "").strip() or "Sin descripcion"
            catalog_lines.append(
                f"- id={problem.id} | name={problem.name} | description={detail}"
            )

        catalog_text = "\n".join(catalog_lines)

        return (
            "Eres un clasificador de incidentes mecanicos.\n"
            "Debes responder un JSON estricto con las llaves situation_summary, problem_id y confidence.\n"
            "No devuelvas texto extra.\n\n"
            f"Descripcion del incidente enviada por cliente (si existe):\n{description or 'Sin texto'}\n\n"
            "Tambien puedes recibir imagenes y/o audio del incidente.\n"
            "No transcribas literal el audio. Resume la situacion entendida de forma breve y clara.\n\n"
            "Catalogo de problemas disponibles:\n"
            f"{catalog_text}\n\n"
            "Reglas:\n"
            "1) situation_summary: una frase corta de la situacion en espanol.\n"
            "2) problem_id debe ser exactamente uno del catalogo.\n"
            "3) confidence debe estar en rango 0.0 a 1.0.\n"
            "4) Responde solo JSON."
        )

    def _build_audio_part(self, audio_payload: dict | None) -> dict | None:
        if not audio_payload:
            return None

        mime_type = str(audio_payload.get("mime_type") or "").strip()
        data_base64 = str(audio_payload.get("data_base64") or "").strip()
        if not mime_type.startswith("audio/"):
            mime_type = "audio/m4a"
        if not data_base64:
            return None

        return {
            "inline_data": {
                "mime_type": mime_type,
                "data": data_base64,
            }
        }

    def _build_evidence_image_parts(self, incident_id: UUID) -> list[dict]:
        evidences = self.evidence.list_by_incident_id(incident_id)
        parts: list[dict] = []

        for evidence in evidences[: self.MAX_EVIDENCE_IMAGES]:
            url = evidence.url.strip()
            if not url.startswith("http"):
                continue

            try:
                with httpx.Client(timeout=15.0) as client:
                    response = client.get(url)
                    response.raise_for_status()
                image_bytes = response.content
                mime_type = response.headers.get("content-type", "image/jpeg")
                if not mime_type.startswith("image/"):
                    mime_type = "image/jpeg"

                encoded = base64.b64encode(image_bytes).decode("utf-8")
                parts.append(
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": encoded,
                        }
                    }
                )
            except Exception:
                continue

        return parts

    def _extract_text_from_gemini_response(self, body: dict) -> str:
        candidates = body.get("candidates") or []
        if not candidates:
            raise HTTPException(status_code=502, detail="Gemini devolvio una respuesta vacia")

        content = candidates[0].get("content") or {}
        parts = content.get("parts") or []
        if not parts:
            raise HTTPException(status_code=502, detail="Gemini no devolvio contenido util")

        text = str(parts[0].get("text") or "").strip()
        if not text:
            raise HTTPException(status_code=502, detail="Gemini no devolvio texto util")

        return text

    def _parse_gemini_json_result(self, text: str) -> dict:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
            cleaned = cleaned.strip()

        try:
            result = json.loads(cleaned)
            if not isinstance(result, dict):
                raise ValueError
            return result
        except Exception:
            raise HTTPException(
                status_code=502,
                detail="Gemini devolvio una respuesta no parseable como JSON",
            )

    def _normalize_confidence(self, value: object) -> float:
        try:
            confidence = float(value)
        except Exception:
            return 0.0

        if confidence < 0:
            return 0.0
        if confidence > 1:
            return 1.0
        return confidence
