from datetime import UTC, datetime
from decimal import Decimal, ROUND_HALF_UP

from fastapi import HTTPException

from app.modules.assignments.repositories import RequestAssignmentRepository
from app.modules.wallet.models import Payment


class ClientServiceReportPdfService:
    def __init__(self, db):
        self.request_assignment = RequestAssignmentRepository(db)

    def build_payment_completion_report(
        self,
        *,
        payment: Payment,
        client_name: str,
    ) -> dict:
        payload = self.request_assignment.get_service_report_payload(payment.assignment_id)
        if not payload:
            raise HTTPException(
                status_code=404,
                detail="No se encontro informacion del servicio para generar el comprobante",
            )

        if not payload.get("report_id"):
            raise HTTPException(
                status_code=409,
                detail="El incidente aun no tiene un reporte final del mecanico",
            )

        delivery_price = self._to_decimal(payload.get("delivery_price"))
        final_price = self._to_decimal(payload.get("final_price"))
        payment_total = self._to_decimal(payment.amount)
        currency_label = self._currency_label(payment.currency)

        report_context = self._build_report_context(
            payload=payload,
            payment=payment,
            client_name=client_name,
            delivery_price=delivery_price,
            final_price=final_price,
            payment_total=payment_total,
            currency_label=currency_label,
        )

        title = f"Informe de servicio y pago #{str(payload['incident_id'])[:8]}"
        lines = self._build_report_lines(report_context)
        pdf_bytes = self._build_simple_pdf(title=title, lines=lines)

        return {
            "pdf_bytes": pdf_bytes,
            "filename": f"informe-servicio-{payload['incident_id']}.pdf",
            "context": report_context,
        }

    def _build_report_context(
        self,
        *,
        payload: dict,
        payment: Payment,
        client_name: str,
        delivery_price: Decimal,
        final_price: Decimal,
        payment_total: Decimal,
        currency_label: str,
    ) -> dict:
        vehicle_label = self._join_non_empty(
            [payload.get("vehicle_make"), payload.get("vehicle_model")]
        ) or "No registrado"

        return {
            "client_name": client_name,
            "incident_id": str(payload.get("incident_id")),
            "incident_short_id": str(payload.get("incident_id"))[:8],
            "incident_status": self._humanize_status(payload.get("incident_status")),
            "problem_name": payload.get("problem_name") or "Sin diagnostico",
            "incident_description": payload.get("incident_description") or "Sin descripcion",
            "incident_address": payload.get("incident_address") or "Sin direccion textual",
            "incident_created_at": self._format_datetime(payload.get("incident_created_at")),
            "incident_responded_at": self._format_datetime(payload.get("assignment_responded_at")),
            "shop_name": payload.get("shop_name") or "Sin dato",
            "shop_address": payload.get("shop_address") or "Sin dato",
            "mechanic_name": payload.get("mechanic_name") or "Sin asignar",
            "mechanic_phone": payload.get("mechanic_phone") or "Sin dato",
            "assignment_status": self._humanize_status(payload.get("assignment_status")),
            "vehicle_label": vehicle_label,
            "vehicle_plate": payload.get("vehicle_plate") or "Sin dato",
            "vehicle_color": payload.get("vehicle_color") or "Sin dato",
            "vehicle_year": payload.get("vehicle_year") or "Sin dato",
            "vehicle_type": payload.get("vehicle_type") or "Sin dato",
            "report_created_at": self._format_datetime(payload.get("report_created_at")),
            "report_description": payload.get("report_description") or "Sin detalle",
            "delivery_price": self._format_money(delivery_price, currency_label),
            "final_price": self._format_money(final_price, currency_label),
            "payment_total": self._format_money(payment_total, currency_label),
            "payment_id": str(payment.id),
            "payment_status": self._humanize_status(payment.status.value),
            "payment_provider": str(payment.provider.value).capitalize(),
            "payment_currency": currency_label,
            "payment_paid_at": self._format_datetime(payment.paid_at),
        }

    def _build_report_lines(self, context: dict) -> list[str]:
        lines: list[str] = []

        lines.extend(self._section_title("DATOS DEL CLIENTE"))
        lines.append(f"Cliente: {context['client_name']}")
        lines.append(f"Incidente ID: {context['incident_id']}")
        lines.append(f"Estado incidente: {context['incident_status']}")

        lines.extend(self._section_title("DATOS DEL INCIDENTE"))
        lines.append(f"Problema diagnosticado: {context['problem_name']}")
        lines.append(f"Fecha solicitud: {context['incident_created_at']}")
        lines.append(f"Fecha cierre asignacion: {context['incident_responded_at']}")
        self._add_multiline_field(
            lines,
            "Descripcion inicial",
            context["incident_description"],
        )
        lines.append(f"Ubicacion incidente: {context['incident_address']}")

        lines.extend(self._section_title("DATOS DEL TALLER"))
        lines.append(f"Taller: {context['shop_name']}")
        lines.append(f"Direccion taller: {context['shop_address']}")

        lines.extend(self._section_title("DATOS DEL MECANICO"))
        lines.append(f"Mecanico: {context['mechanic_name']}")
        lines.append(f"Telefono mecanico: {context['mechanic_phone']}")
        lines.append(f"Estado asignacion: {context['assignment_status']}")

        lines.extend(self._section_title("DATOS DEL VEHICULO"))
        lines.append(f"Vehiculo: {context['vehicle_label']}")
        lines.append(f"Placa vehiculo: {context['vehicle_plate']}")
        lines.append(f"Color vehiculo: {context['vehicle_color']}")
        lines.append(f"Anio vehiculo: {context['vehicle_year']}")
        lines.append(f"Tipo vehiculo: {context['vehicle_type']}")

        lines.extend(self._section_title("REPORTE FINAL DEL SERVICIO"))
        lines.append(f"Fecha reporte mecanico: {context['report_created_at']}")
        self._add_multiline_field(
            lines,
            "Detalle del trabajo",
            context["report_description"],
        )

        lines.extend(self._section_title("RESUMEN DEL PAGO"))
        lines.append(f"Costo de traslado: {context['delivery_price']}")
        lines.append(f"Costo mano de obra: {context['final_price']}")
        lines.append(f"Total pagado: {context['payment_total']}")
        lines.append(f"ID de pago: {context['payment_id']}")
        lines.append(f"Estado de pago: {context['payment_status']}")
        lines.append(f"Proveedor: {context['payment_provider']}")
        lines.append(f"Moneda: {context['payment_currency']}")
        lines.append(f"Fecha de pago: {context['payment_paid_at']}")

        return lines

    def _build_simple_pdf(self, *, title: str, lines: list[str]) -> bytes:
        page_width = 595
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
                f"(Generado: {self._pdf_escape(self._format_datetime(datetime.now(UTC)))}) Tj ET",
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

    def _format_datetime(self, value) -> str:
        if value is None:
            return "Sin dato"
        if value.tzinfo is None:
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return value.astimezone(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")

    def _format_money(
        self,
        value: Decimal | float | int | None,
        currency_label: str,
    ) -> str:
        if value is None:
            return "No disponible"
        amount = Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return f"{currency_label} {amount:.2f}"

    def _currency_label(self, currency: str | None) -> str:
        normalized = str(currency or "").strip().lower()
        if normalized == "bob":
            return "Bs"
        if not normalized:
            return "Monto"
        return normalized.upper()

    def _to_decimal(self, value: float | Decimal | int | None) -> Decimal:
        if value is None:
            return Decimal("0.00")
        return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _pdf_escape(self, value: str) -> str:
        ascii_value = str(value).encode("latin-1", errors="replace").decode("latin-1")
        return (
            ascii_value.replace("\\", "\\\\")
            .replace("(", "\\(")
            .replace(")", "\\)")
        )

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

        translations = {
            "pending": "Pendiente",
            "classified": "Clasificado",
            "searching_shop": "Buscando taller",
            "assigned": "Asignado",
            "on_the_way": "En camino",
            "arrived": "Llegado",
            "payment_pending": "Pendiente de pago",
            "completed": "Completado",
            "accepted": "Aceptado",
            "offered": "Ofrecido",
            "rejected": "Rechazado",
            "paid": "Pagado",
            "checkout_created": "Checkout creado",
            "failed": "Fallido",
            "cancelled": "Cancelado",
            "expired": "Expirado",
        }

        if normalized in translations:
            return translations[normalized]

        words = normalized.split("_")
        return " ".join(word.capitalize() for word in words if word)
