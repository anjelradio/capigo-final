from datetime import UTC, datetime
import logging
from uuid import UUID

from fastapi import HTTPException

from app.modules.assignments.models import AssignmentStatus
from app.modules.incidents.models import IncidentStatus
from app.modules.realtime.services import PushNotificationService, ShopOfferNotificationService
from app.modules.user.models import UserRole

from .base_service import AssignmentBaseService

logger = logging.getLogger(__name__)


class OwnerOfferService(AssignmentBaseService):
    def list_my_pending_offers(self, *, user_id: UUID) -> dict:
        shop_id = self._resolve_owner_shop_id(user_id)
        now_utc = datetime.now(UTC)
        assignments = self.request_assignment.list_pending_active_by_shop(shop_id, now_utc)

        offers: list[dict] = []
        for assignment in assignments:
            payload = self.request_assignment.get_offer_notification_payload(assignment.id)
            if not payload:
                continue

            offers.append(
                {
                    "assignment_id": assignment.id,
                    "incident_id": assignment.incident_id,
                    "problem_id": payload.get("problem_id"),
                    "problem_name": payload.get("problem_name"),
                    "incident_description": payload.get("incident_description"),
                    "distance_km": payload.get("distance_km"),
                    "delivery_price": payload.get("delivery_price"),
                    "notified_at": assignment.notified_at,
                    "expires_at": assignment.expires_at,
                }
            )

        return {"offers": offers}

    def get_my_offer_detail(self, *, user_id: UUID, assignment_id: UUID) -> dict:
        shop_id = self._resolve_owner_shop_id(user_id)
        assignment = self.request_assignment.get_by_id(assignment_id)
        if not assignment or assignment.repair_shop_id != shop_id:
            raise HTTPException(status_code=404, detail="Oferta no encontrada")

        payload = self.request_assignment.get_offer_notification_payload(assignment.id)
        if not payload:
            raise HTTPException(status_code=404, detail="Oferta no encontrada")

        return {
            "assignment_id": assignment.id,
            "incident_id": assignment.incident_id,
            "problem_id": payload.get("problem_id"),
            "problem_name": payload.get("problem_name"),
            "incident_description": payload.get("incident_description"),
            "incident_latitude": payload["incident_latitude"],
            "incident_longitude": payload["incident_longitude"],
            "repair_shop_latitude": payload.get("shop_latitude"),
            "repair_shop_longitude": payload.get("shop_longitude"),
            "distance_km": payload.get("distance_km"),
            "delivery_price": payload.get("delivery_price"),
            "mechanic_name": self.request_assignment.get_mechanic_full_name(
                assignment.mechanic_id
            ),
            "notified_at": assignment.notified_at,
            "expires_at": assignment.expires_at,
            "evidence_urls": payload.get("evidence_urls", []),
        }

    def list_my_offer_history(self, *, user_id: UUID) -> dict:
        shop_id = self._resolve_owner_shop_id(user_id)
        now_utc = datetime.now(UTC)
        assignments = self.request_assignment.list_history_by_shop(shop_id, now_utc)

        offers: list[dict] = []
        for assignment in assignments:
            payload = self.request_assignment.get_offer_notification_payload(assignment.id)
            if not payload:
                continue

            offers.append(
                {
                    "assignment_id": assignment.id,
                    "incident_id": assignment.incident_id,
                    "problem_id": payload.get("problem_id"),
                    "problem_name": payload.get("problem_name"),
                    "incident_description": payload.get("incident_description"),
                    "distance_km": payload.get("distance_km"),
                    "delivery_price": payload.get("delivery_price"),
                    "status": self._resolve_history_status(assignment.status, assignment.expires_at),
                    "notified_at": assignment.notified_at,
                    "expires_at": assignment.expires_at,
                    "responded_at": assignment.responded_at,
                }
            )

        return {"offers": offers}

    def list_my_assignments(self, *, user_id: UUID) -> dict:
        shop_id = self._resolve_owner_shop_id(user_id)
        assignments = self.request_assignment.list_assignments_for_shop(shop_id)

        items: list[dict] = []
        for assignment in assignments:
            payload = self.request_assignment.get_offer_notification_payload(assignment.id)
            if not payload:
                continue

            items.append(
                {
                    "assignment_id": assignment.id,
                    "incident_id": assignment.incident_id,
                    "problem_id": payload.get("problem_id"),
                    "problem_name": payload.get("problem_name"),
                    "incident_description": payload.get("incident_description"),
                    "distance_km": payload.get("distance_km"),
                    "delivery_price": payload.get("delivery_price"),
                    "status": assignment.status.value,
                    "mechanic_name": self.request_assignment.get_mechanic_full_name(
                        assignment.mechanic_id
                    ),
                    "created_at": assignment.created_date,
                }
            )

        return {"assignments": items}

    def download_my_assignment_report_pdf(self, *, user_id: UUID, assignment_id: UUID) -> tuple[bytes, str]:
        shop_id = self._resolve_owner_shop_id(user_id)
        assignment = self.request_assignment.get_by_id(assignment_id)
        if not assignment or assignment.repair_shop_id != shop_id:
            raise HTTPException(status_code=404, detail="Asignacion no encontrada")

        payload = self.request_assignment.get_service_report_payload(assignment.id)
        if not payload:
            raise HTTPException(status_code=404, detail="No se encontro informacion de reporte")

        report_id = payload.get("report_id")
        if not report_id:
            raise HTTPException(
                status_code=409,
                detail="El incidente aun no tiene un reporte final del mecanico",
            )

        lines = self._build_report_lines(payload)
        title = f"Reporte de servicio #{str(payload['incident_id'])[:8]}"
        pdf_bytes = self._build_simple_pdf(title=title, lines=lines)
        filename = f"reporte-servicio-{payload['incident_id']}.pdf"
        return pdf_bytes, filename

    def reject_my_offer(self, *, user_id: UUID, assignment_id: UUID) -> dict:
        shop_id = self._resolve_owner_shop_id(user_id)
        assignment = self.request_assignment.get_by_id(assignment_id)
        if not assignment or assignment.repair_shop_id != shop_id:
            raise HTTPException(status_code=404, detail="Oferta no encontrada")

        self._ensure_offer_actionable(assignment.status, assignment.expires_at)

        assignment.status = AssignmentStatus.REJECTED
        assignment.responded_at = datetime.now(UTC)
        self.db.add(assignment)
        self.db.commit()

        notify_output = ShopOfferNotificationService(
            self.db
        ).notify_next_offer_in_incident_queue_sync(assignment.incident_id)
        next_assignment_id = notify_output.get("assignment_id")

        self._emit_incident_realtime_event(
            incident_id=assignment.incident_id,
            event_type="assignment.offer.rejected",
            payload={
                "assignment_id": assignment.id,
                "next_notified_assignment_id": next_assignment_id,
                "description": "El taller rechazo la oferta",
            },
            assignment_id=assignment.id,
            repair_shop_id=assignment.repair_shop_id,
        )

        return {
            "assignment_id": assignment.id,
            "incident_id": assignment.incident_id,
            "status": AssignmentStatus.REJECTED.value,
            "detail": "Oferta rechazada",
            "next_notified_assignment_id": next_assignment_id,
        }

    def accept_my_offer(self, *, user_id: UUID, assignment_id: UUID, mechanic_id: UUID) -> dict:
        shop_id = self._resolve_owner_shop_id(user_id)
        assignment = self.request_assignment.get_by_id(assignment_id)
        if not assignment or assignment.repair_shop_id != shop_id:
            raise HTTPException(status_code=404, detail="Oferta no encontrada")

        self._ensure_offer_actionable(assignment.status, assignment.expires_at)

        mechanic_link = self.shop_mechanic.get_active_by_id_and_shop(mechanic_id, shop_id)
        if not mechanic_link:
            raise HTTPException(status_code=404, detail="Mecanico no encontrado en el taller")
        if not mechanic_link.is_available:
            raise HTTPException(status_code=409, detail="El mecanico seleccionado no esta disponible")

        assignment.status = AssignmentStatus.ACCEPTED
        assignment.mechanic_id = mechanic_link.id
        assignment.responded_at = datetime.now(UTC)
        self.db.add(assignment)

        mechanic_link.is_available = False
        self.db.add(mechanic_link)

        incident = self.incident.get_by_id(assignment.incident_id)
        if incident:
            incident.status = IncidentStatus.ASSIGNED
            incident.delivery_price = assignment.delivery_price
            incident.distance_km = assignment.distance_km
            self.db.add(incident)

        remaining_pending = self.request_assignment.list_pending_by_incident_except_shop(
            incident_id=assignment.incident_id,
            exclude_shop_id=assignment.repair_shop_id,
        )
        for pending in remaining_pending:
            pending.status = AssignmentStatus.CANCELLED
            pending.responded_at = datetime.now(UTC)
            self.db.add(pending)

        self.db.commit()

        self._emit_incident_realtime_event(
            incident_id=assignment.incident_id,
            event_type="assignment.accepted",
            payload={
                "assignment_id": assignment.id,
                "mechanic_id": assignment.mechanic_id,
                "repair_shop_id": assignment.repair_shop_id,
                "status": IncidentStatus.ASSIGNED.value,
                "description": "Solicitud aceptada por el taller",
            },
            status=IncidentStatus.ASSIGNED,
            assignment_id=assignment.id,
            repair_shop_id=assignment.repair_shop_id,
            mechanic_id=assignment.mechanic_id,
        )

        self._emit_incident_realtime_event(
            incident_id=assignment.incident_id,
            event_type="incident.status.changed",
            payload={
                "status": IncidentStatus.ASSIGNED.value,
                "assignment_id": assignment.id,
                "mechanic_id": assignment.mechanic_id,
                "description": "Incidente asignado a taller y mecanico",
            },
            status=IncidentStatus.ASSIGNED,
            assignment_id=assignment.id,
            repair_shop_id=assignment.repair_shop_id,
            mechanic_id=assignment.mechanic_id,
        )

        self._emit_incident_realtime_event(
            incident_id=assignment.incident_id,
            event_type="assignment.mechanic.assigned",
            payload={
                "assignment_id": assignment.id,
                "mechanic_id": assignment.mechanic_id,
                "description": "Mecanico asignado al incidente",
            },
            status=IncidentStatus.ASSIGNED,
            assignment_id=assignment.id,
            repair_shop_id=assignment.repair_shop_id,
            mechanic_id=assignment.mechanic_id,
        )

        self._send_mechanic_assignment_push(
            mechanic_user_id=mechanic_link.user_id,
            incident_id=assignment.incident_id,
            assignment_id=assignment.id,
        )

        return {
            "assignment_id": assignment.id,
            "incident_id": assignment.incident_id,
            "status": AssignmentStatus.ACCEPTED.value,
            "detail": "Oferta aceptada",
            "next_notified_assignment_id": None,
        }

    def _send_mechanic_assignment_push(
        self,
        *,
        mechanic_user_id: UUID,
        incident_id: UUID,
        assignment_id: UUID,
    ) -> None:
        try:
            PushNotificationService(self.db).notify_mechanic_assignment_created(
                mechanic_user_id=mechanic_user_id,
                incident_id=incident_id,
                assignment_id=assignment_id,
            )
        except Exception as error:
            logger.warning(
                "No se pudo enviar push a mecanico user_id=%s incident_id=%s error=%s",
                mechanic_user_id,
                incident_id,
                error,
            )

    def _resolve_history_status(
        self, status: AssignmentStatus, expires_at: datetime | None
    ) -> str:
        now_utc_naive = datetime.utcnow()
        expires_at_naive = self._to_utc_naive(expires_at)

        if (
            status == AssignmentStatus.PENDING
            and expires_at_naive is not None
            and expires_at_naive <= now_utc_naive
        ):
            return AssignmentStatus.EXPIRED.value

        return status.value

    def _to_utc_naive(self, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value
        return value.astimezone(UTC).replace(tzinfo=None)

    def _ensure_offer_actionable(
        self, status: AssignmentStatus, expires_at: datetime | None
    ) -> None:
        if status != AssignmentStatus.PENDING:
            raise HTTPException(status_code=409, detail="La oferta ya no esta pendiente")

        expires_at_naive = self._to_utc_naive(expires_at)
        if expires_at_naive is None:
            raise HTTPException(status_code=409, detail="La oferta aun no fue notificada")

        if expires_at_naive <= datetime.utcnow():
            raise HTTPException(status_code=409, detail="La oferta ya expiro")

    def _resolve_owner_shop_id(self, user_id: UUID) -> UUID:
        owner = self._get_user_or_404(user_id)
        if owner.role != UserRole.OWNER:
            raise HTTPException(
                status_code=403,
                detail="Solo los propietarios de taller pueden revisar ofertas",
            )

        shop = self.repair_shop.get_by_owner_id(owner.id)
        if not shop:
            raise HTTPException(status_code=404, detail="Taller no encontrado")

        return shop.id

    def _emit_incident_realtime_event(
        self,
        *,
        incident_id: UUID,
        event_type: str,
        payload: dict,
        status: str | None = None,
        assignment_id: UUID | None = None,
        repair_shop_id: UUID | None = None,
        mechanic_id: UUID | None = None,
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
                assignment_id=assignment_id,
                repair_shop_id=repair_shop_id,
                mechanic_id=mechanic_id,
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

    def _build_report_lines(self, payload: dict) -> list[str]:
        vehicle_title = self._join_non_empty(
            [payload.get("vehicle_make"), payload.get("vehicle_model")]
        ) or "No registrado"

        lines: list[str] = []

        lines.extend(self._section_title("DATOS DEL INCIDENTE"))
        lines.append(f"Incidente ID: {payload.get('incident_id')}")
        lines.append(
            f"Estado incidente: {self._humanize_status(payload.get('incident_status'))}"
        )
        lines.append(
            f"Problema diagnosticado: {payload.get('problem_name') or 'Sin diagnostico'}"
        )
        lines.append(
            f"Fecha solicitud: {self._format_datetime(payload.get('incident_created_at'))}"
        )
        lines.append(
            f"Fecha cierre asignacion: {self._format_datetime(payload.get('assignment_responded_at'))}"
        )
        self._add_multiline_field(
            lines,
            "Descripcion inicial",
            payload.get("incident_description") or "Sin descripcion",
        )
        lines.append(
            f"Ubicacion incidente: {payload.get('incident_address') or 'Sin direccion textual'}"
        )
        lines.append(
            f"Distancia estimada: {self._format_decimal(payload.get('distance_km'), 'km')}"
        )
        lines.append(f"Costo traslado: {self._format_money(payload.get('delivery_price'))}")

        lines.extend(self._section_title("DATOS DEL TALLER"))
        lines.append(f"Taller: {payload.get('shop_name') or 'Sin dato'}")
        lines.append(f"Direccion taller: {payload.get('shop_address') or 'Sin dato'}")

        lines.extend(self._section_title("DATOS DEL MECANICO"))
        lines.append(f"Mecanico: {payload.get('mechanic_name') or 'Sin asignar'}")
        lines.append(f"Telefono mecanico: {payload.get('mechanic_phone') or 'Sin dato'}")
        lines.append(
            f"Estado asignacion: {self._humanize_status(payload.get('assignment_status'))}"
        )

        lines.extend(self._section_title("DATOS DEL VEHICULO"))
        lines.append(f"Vehiculo: {vehicle_title}")
        lines.append(f"Placa vehiculo: {payload.get('vehicle_plate') or 'Sin dato'}")
        lines.append(f"Color vehiculo: {payload.get('vehicle_color') or 'Sin dato'}")
        lines.append(f"Anio vehiculo: {payload.get('vehicle_year') or 'Sin dato'}")
        lines.append(f"Tipo vehiculo: {payload.get('vehicle_type') or 'Sin dato'}")

        lines.extend(self._section_title("REPORTE FINAL DEL SERVICIO"))
        lines.append(
            f"Fecha reporte mecanico: {self._format_datetime(payload.get('report_created_at'))}"
        )
        lines.append(f"Costo mano de obra: {self._format_money(payload.get('labor_price'))}")
        self._add_multiline_field(
            lines,
            "Detalle del trabajo",
            payload.get("report_description") or "Sin detalle",
        )

        lines.extend(self._section_title("CALIFICACION DEL CLIENTE"))
        lines.append(f"Calificacion: {payload.get('feedback_rating') or 'Sin calificacion'}")
        self._add_multiline_field(
            lines,
            "Comentario",
            payload.get("feedback_comment") or "Sin comentario",
        )
        return lines

    def _build_simple_pdf(self, *, title: str, lines: list[str]) -> bytes:
        page_width = 595
        page_height = 842
        margin_left = 46
        margin_right = 46
        page_number = 1

        def start_page_commands(current_page_number: int) -> tuple[list[str], float]:
            commands: list[str] = [
                "q 0.965 0.972 0.984 rg 0 0 595 842 re f Q",
                "q 0.102 0.361 0.604 rg 0 768 595 74 re f Q",
                "q 1 1 1 rg",
                "BT /F2 18 Tf 1 0 0 1 46 810 Tm "
                f"({self._pdf_escape(title)}) Tj ET",
                "BT /F1 10 Tf 1 0 0 1 46 792 Tm "
                f"(Generado: {self._pdf_escape(self._format_datetime(datetime.now(UTC)) )}) Tj ET",
                "Q",
                "q 0.90 0.92 0.95 RG 1 w 46 760 m 549 760 l S Q",
                "BT /F1 9 Tf 1 0 0 1 490 28 Tm "
                f"(Pagina {current_page_number}) Tj ET",
            ]
            return commands, 742.0

        page_commands: list[list[str]] = []
        commands, cursor_y = start_page_commands(page_number)

        for raw_line in lines:
            line = str(raw_line)

            if line.startswith("===") and line.endswith("==="):
                if cursor_y < 84:
                    page_commands.append(commands)
                    page_number += 1
                    commands, cursor_y = start_page_commands(page_number)

                section_title = line.strip("=").strip()
                section_width = page_width - margin_left - margin_right
                commands.append(
                    "q 0.870 0.914 0.965 rg "
                    f"{margin_left - 6} {cursor_y - 5} {section_width + 12} 18 re f Q"
                )
                commands.append(
                    "BT /F2 11 Tf 1 0 0 1 "
                    f"{margin_left} {cursor_y} Tm "
                    f"({self._pdf_escape(section_title)}) Tj ET"
                )
                cursor_y -= 23
                continue

            if not line.strip():
                cursor_y -= 8
                continue

            if cursor_y < 66:
                page_commands.append(commands)
                page_number += 1
                commands, cursor_y = start_page_commands(page_number)

            x = margin_left + (12 if line.startswith("  ") else 0)
            commands.append(
                "BT /F1 10 Tf 1 0 0 1 "
                f"{x} {cursor_y} Tm "
                f"({self._pdf_escape(line.strip())}) Tj ET"
            )
            cursor_y -= 14

        page_commands.append(commands)

        objects: dict[int, bytes] = {
            1: b"<< /Type /Catalog /Pages 2 0 R >>",
            2: b"",
            3: b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
            4: b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>",
        }

        kids_refs: list[str] = []
        next_obj_id = 5
        for commands_for_page in page_commands:
            page_obj_id = next_obj_id
            content_obj_id = next_obj_id + 1
            next_obj_id += 2

            stream_data = "\n".join(commands_for_page).encode("latin-1", errors="replace")
            objects[content_obj_id] = (
                b"<< /Length "
                + str(len(stream_data)).encode("latin-1")
                + b" >>\nstream\n"
                + stream_data
                + b"\nendstream"
            )

            objects[page_obj_id] = (
                "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
                "/Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> "
                f"/Contents {content_obj_id} 0 R >>"
            ).encode("latin-1")
            kids_refs.append(f"{page_obj_id} 0 R")

        objects[2] = (
            f"<< /Type /Pages /Kids [{' '.join(kids_refs)}] /Count {len(kids_refs)} >>"
        ).encode("latin-1")

        max_object_id = max(objects.keys())
        pdf = bytearray(b"%PDF-1.4\n")
        offsets = [0] * (max_object_id + 1)

        for object_id in range(1, max_object_id + 1):
            object_content = objects.get(object_id)
            if object_content is None:
                continue
            offsets[object_id] = len(pdf)
            pdf.extend(f"{object_id} 0 obj\n".encode("latin-1"))
            pdf.extend(object_content)
            pdf.extend(b"\nendobj\n")

        xref_start = len(pdf)
        pdf.extend(f"xref\n0 {max_object_id + 1}\n".encode("latin-1"))
        pdf.extend(b"0000000000 65535 f \n")
        for object_id in range(1, max_object_id + 1):
            offset = offsets[object_id]
            if offset == 0:
                pdf.extend(b"0000000000 00000 f \n")
                continue
            pdf.extend(f"{offset:010d} 00000 n \n".encode("latin-1"))

        pdf.extend(
            (
                "trailer\n"
                f"<< /Size {max_object_id + 1} /Root 1 0 R >>\n"
                "startxref\n"
                f"{xref_start}\n"
                "%%EOF"
            ).encode("latin-1")
        )
        return bytes(pdf)

    def _pdf_escape(self, value: str) -> str:
        ascii_value = str(value).encode("latin-1", errors="replace").decode("latin-1")
        return (
            ascii_value.replace("\\", "\\\\")
            .replace("(", "\\(")
            .replace(")", "\\)")
        )

    def _format_datetime(self, value: datetime | None) -> str:
        if value is None:
            return "Sin dato"
        if value.tzinfo is None:
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return value.astimezone(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")

    def _format_money(self, value: float | None) -> str:
        if value is None:
            return "No disponible"
        return f"Bs {value:.2f}"

    def _format_decimal(self, value: float | None, suffix: str) -> str:
        if value is None:
            return "No disponible"
        return f"{value:.2f} {suffix}"

    def _join_non_empty(self, parts: list[str | None]) -> str:
        clean_parts = [str(item).strip() for item in parts if str(item or "").strip()]
        return " ".join(clean_parts)

    def _section_title(self, title: str) -> list[str]:
        return ["", f"=== {title} ==="]

    def _add_multiline_field(self, lines: list[str], label: str, value: str) -> None:
        text = str(value or "").strip()
        wrapped = self._wrap_text(text, max_chars=88)
        if not wrapped:
            lines.append(f"{label}: Sin dato")
            return

        lines.append(f"{label}: {wrapped[0]}")
        for chunk in wrapped[1:]:
            lines.append(f"  {chunk}")

    def _wrap_text(self, text: str, max_chars: int) -> list[str]:
        if not text:
            return []

        words = text.split()
        if not words:
            return []

        chunks: list[str] = []
        current = words[0]
        for word in words[1:]:
            candidate = f"{current} {word}"
            if len(candidate) <= max_chars:
                current = candidate
                continue
            chunks.append(current)
            current = word

        chunks.append(current)
        return chunks

    def _humanize_status(self, value: str | None) -> str:
        normalized = str(value or "").strip().lower()
        if not normalized:
            return "Sin dato"

        words = normalized.split("_")
        return " ".join(word.capitalize() for word in words if word)
