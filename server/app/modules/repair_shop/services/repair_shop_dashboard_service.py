from datetime import UTC, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from sqlalchemy import text
from sqlmodel import Session

from app.modules.assignments.models import AssignmentStatus
from app.modules.repair_shop.schemas import (
    RepairShopDashboardBreakdownRead,
    RepairShopDashboardKpisRead,
    RepairShopDashboardRead,
    RepairShopDashboardZoneRead,
)
from .base_service import RepairShopBaseService


class RepairShopDashboardService(RepairShopBaseService):
    def __init__(self, db: Session):
        super().__init__(db)

    def get_my_dashboard(self, *, owner_id: UUID, period_days: int = 30) -> RepairShopDashboardRead:
        self._ensure_owner_role(owner_id, detail="Solo usuarios owner pueden consultar el dashboard")
        shop = self._get_shop_by_owner_or_404(owner_id)

        normalized_days = max(1, min(int(period_days), 365))
        now_utc = datetime.utcnow().replace(microsecond=0)
        start_utc = now_utc - timedelta(days=normalized_days)

        kpis = self._get_kpis(shop_id=shop.id, start_utc=start_utc, end_utc=now_utc)
        services_by_type = self._get_services_by_type(
            shop_id=shop.id,
            start_utc=start_utc,
            end_utc=now_utc,
            completed_total=kpis.completed_services,
        )
        zones_by_services = self._get_zones_by_services(
            shop_id=shop.id,
            start_utc=start_utc,
            end_utc=now_utc,
            completed_total=kpis.completed_services,
        )

        return RepairShopDashboardRead(
            period_days=normalized_days,
            generated_at=now_utc,
            kpis=kpis,
            services_by_type=services_by_type,
            zones_by_services=zones_by_services,
        )

    def _get_kpis(self, *, shop_id, start_utc: datetime, end_utc: datetime) -> RepairShopDashboardKpisRead:
        requests_received = self._count_requests_received(shop_id=shop_id, start_utc=start_utc, end_utc=end_utc)
        accepted_services = self._count_accepted_services(shop_id=shop_id, start_utc=start_utc, end_utc=end_utc)
        completed_services = self._count_completed_services(shop_id=shop_id, start_utc=start_utc, end_utc=end_utc)
        cancelled_cases = self._count_cancelled_cases(shop_id=shop_id, start_utc=start_utc, end_utc=end_utc)
        revenue_total = self._sum_revenue(shop_id=shop_id, start_utc=start_utc, end_utc=end_utc)
        average_resolution_minutes = self._get_average_resolution_minutes(
            shop_id=shop_id,
            start_utc=start_utc,
            end_utc=end_utc,
        )
        top_mechanic_name, top_mechanic_completed = self._get_top_mechanic(
            shop_id=shop_id,
            start_utc=start_utc,
            end_utc=end_utc,
        )

        acceptance_rate = (accepted_services / requests_received * 100.0) if requests_received > 0 else 0.0
        cancellation_rate = (cancelled_cases / requests_received * 100.0) if requests_received > 0 else 0.0
        average_ticket_value = (float(revenue_total) / completed_services) if completed_services > 0 else 0.0

        return RepairShopDashboardKpisRead(
            requests_received=requests_received,
            accepted_services=accepted_services,
            completed_services=completed_services,
            cancelled_cases=cancelled_cases,
            acceptance_rate=round(acceptance_rate, 2),
            cancellation_rate=round(cancellation_rate, 2),
            revenue_total=float(revenue_total),
            average_resolution_minutes=round(average_resolution_minutes, 2),
            average_ticket_value=round(average_ticket_value, 2),
            top_mechanic_name=top_mechanic_name,
            top_mechanic_completed=top_mechanic_completed,
        )

    def _count_requests_received(self, *, shop_id, start_utc: datetime, end_utc: datetime) -> int:
        query = text(
            """
            SELECT COUNT(*) AS total
            FROM request_assignment ra
            WHERE ra.state = true
              AND ra.repair_shop_id = :shop_id
              AND ra.created_date >= :start_utc
              AND ra.created_date < :end_utc
            """
        )
        total = self.db.exec(query, params={"shop_id": str(shop_id), "start_utc": start_utc, "end_utc": end_utc}).first()
        return int(total.total if total else 0)

    def _count_completed_services(self, *, shop_id, start_utc: datetime, end_utc: datetime) -> int:
        query = text(
            """
            SELECT COUNT(*) AS total
            FROM request_assignment ra
            WHERE ra.state = true
              AND ra.repair_shop_id = :shop_id
              AND ra.status = :completed_status
              AND ra.responded_at IS NOT NULL
              AND ra.responded_at >= :start_utc
              AND ra.responded_at < :end_utc
            """
        )
        total = self.db.exec(
            query,
            params={
                "shop_id": str(shop_id),
                "start_utc": start_utc,
                "end_utc": end_utc,
                "completed_status": AssignmentStatus.COMPLETED.name,
            },
        ).first()
        return int(total.total if total else 0)

    def _count_accepted_services(self, *, shop_id, start_utc: datetime, end_utc: datetime) -> int:
        query = text(
            """
            SELECT COUNT(*) AS total
            FROM request_assignment ra
            WHERE ra.state = true
              AND ra.repair_shop_id = :shop_id
              AND ra.status IN (:accepted_status, :payment_pending_status, :completed_status)
              AND ra.responded_at IS NOT NULL
              AND ra.responded_at >= :start_utc
              AND ra.responded_at < :end_utc
            """
        )
        total = self.db.exec(
            query,
            params={
                "shop_id": str(shop_id),
                "start_utc": start_utc,
                "end_utc": end_utc,
                "accepted_status": AssignmentStatus.ACCEPTED.name,
                "payment_pending_status": AssignmentStatus.PAYMENT_PENDING.name,
                "completed_status": AssignmentStatus.COMPLETED.name,
            },
        ).first()
        return int(total.total if total else 0)

    def _count_cancelled_cases(self, *, shop_id, start_utc: datetime, end_utc: datetime) -> int:
        query = text(
            """
            SELECT COUNT(*) AS total
            FROM request_assignment ra
            WHERE ra.state = true
              AND ra.repair_shop_id = :shop_id
              AND ra.status IN (:cancelled_status, :rejected_status, :expired_status, :failed_status)
              AND COALESCE(ra.responded_at, ra.created_date) >= :start_utc
              AND COALESCE(ra.responded_at, ra.created_date) < :end_utc
            """
        )
        total = self.db.exec(
            query,
            params={
                "shop_id": str(shop_id),
                "start_utc": start_utc,
                "end_utc": end_utc,
                "cancelled_status": AssignmentStatus.CANCELLED.name,
                "rejected_status": AssignmentStatus.REJECTED.name,
                "expired_status": AssignmentStatus.EXPIRED.name,
                "failed_status": AssignmentStatus.FAILED.name,
            },
        ).first()
        return int(total.total if total else 0)

    def _sum_revenue(self, *, shop_id, start_utc: datetime, end_utc: datetime) -> Decimal:
        query = text(
            """
            SELECT COALESCE(SUM(ra.final_price), 0) AS total
            FROM request_assignment ra
            WHERE ra.state = true
              AND ra.repair_shop_id = :shop_id
              AND ra.status = :completed_status
              AND ra.final_price IS NOT NULL
              AND ra.responded_at IS NOT NULL
              AND ra.responded_at >= :start_utc
              AND ra.responded_at < :end_utc
            """
        )
        row = self.db.exec(
            query,
            params={
                "shop_id": str(shop_id),
                "start_utc": start_utc,
                "end_utc": end_utc,
                "completed_status": AssignmentStatus.COMPLETED.name,
            },
        ).first()
        if not row or row.total is None:
            return Decimal("0.00")
        return Decimal(str(row.total)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _get_average_resolution_minutes(self, *, shop_id, start_utc: datetime, end_utc: datetime) -> float:
        query = text(
            """
            WITH arrived AS (
                SELECT incident_id, MIN(created_date) AS arrived_at
                FROM incident_realtime_event
                WHERE state = true
                  AND event_type = :status_changed_event
                  AND payload->>'status' = :arrived_status
                GROUP BY incident_id
            ),
            completed AS (
                SELECT incident_id, MIN(created_date) AS completed_at
                FROM incident_realtime_event
                WHERE state = true
                  AND event_type = :status_changed_event
                  AND payload->>'status' = :completed_status
                GROUP BY incident_id
            )
            SELECT COALESCE(AVG(EXTRACT(EPOCH FROM (c.completed_at - a.arrived_at)) / 60.0), 0) AS avg_minutes
            FROM request_assignment ra
            JOIN arrived a ON a.incident_id = ra.incident_id
            JOIN completed c ON c.incident_id = ra.incident_id
            WHERE ra.state = true
              AND ra.repair_shop_id = :shop_id
              AND a.arrived_at >= :start_utc
              AND a.arrived_at < :end_utc
              AND c.completed_at >= :start_utc
              AND c.completed_at < :end_utc
              AND c.completed_at >= a.arrived_at
            """
        )
        row = self.db.exec(
            query,
            params={
                "shop_id": str(shop_id),
                "start_utc": start_utc,
                "end_utc": end_utc,
                "status_changed_event": "incident.status.changed",
                "arrived_status": "arrived",
                "completed_status": "completed",
            },
        ).first()
        if not row or row.avg_minutes is None:
            return 0.0
        return float(row.avg_minutes)

    def _get_top_mechanic(
        self,
        *,
        shop_id,
        start_utc: datetime,
        end_utc: datetime,
    ) -> tuple[str | None, int]:
        query = text(
            """
            SELECT
                COALESCE(NULLIF(TRIM(u.first_name || ' ' || u.last_name), ''), 'Sin mecanico') AS label,
                COUNT(*) AS total
            FROM request_assignment ra
            LEFT JOIN shop_mechanics sm ON sm.id = ra.mechanic_id
            LEFT JOIN "user" u ON u.id = sm.user_id
            WHERE ra.state = true
              AND ra.repair_shop_id = :shop_id
              AND ra.status = :completed_status
              AND ra.responded_at IS NOT NULL
              AND ra.responded_at >= :start_utc
              AND ra.responded_at < :end_utc
            GROUP BY COALESCE(NULLIF(TRIM(u.first_name || ' ' || u.last_name), ''), 'Sin mecanico')
            ORDER BY total DESC, label ASC
            LIMIT 1
            """
        )
        row = self.db.exec(
            query,
            params={
                "shop_id": str(shop_id),
                "start_utc": start_utc,
                "end_utc": end_utc,
                "completed_status": AssignmentStatus.COMPLETED.name,
            },
        ).first()

        if not row:
            return None, 0

        return str(row.label), int(row.total or 0)

    def _get_services_by_type(
        self,
        *,
        shop_id,
        start_utc: datetime,
        end_utc: datetime,
        completed_total: int,
    ) -> list[RepairShopDashboardBreakdownRead]:
        query = text(
            """
            SELECT
                COALESCE(s.name, 'Sin clasificacion') AS label,
                COUNT(*) AS total
            FROM request_assignment ra
            JOIN incident i ON i.id = ra.incident_id
            LEFT JOIN problem_service_map psm ON psm.problem_id = i.problem_id AND psm.state = true
            LEFT JOIN services s ON s.id = psm.service_id AND s.state = true AND s.is_available = true
            JOIN shop_services ss ON ss.shop_id = ra.repair_shop_id AND ss.service_id = s.id
            WHERE ra.state = true
              AND ra.repair_shop_id = :shop_id
              AND ra.status = :completed_status
              AND ra.responded_at IS NOT NULL
              AND ra.responded_at >= :start_utc
              AND ra.responded_at < :end_utc
              AND ss.state = true
              AND ss.is_available = true
            GROUP BY COALESCE(s.name, 'Sin clasificacion')
            ORDER BY total DESC, label ASC
            LIMIT 6
            """
        )
        rows = self.db.exec(
            query,
            params={
                "shop_id": str(shop_id),
                "start_utc": start_utc,
                "end_utc": end_utc,
                "completed_status": AssignmentStatus.COMPLETED.name,
            },
        ).all()

        breakdowns: list[RepairShopDashboardBreakdownRead] = []
        for row in rows:
            count = int(row.total or 0)
            percentage = (count / completed_total * 100.0) if completed_total > 0 else 0.0
            breakdowns.append(
                RepairShopDashboardBreakdownRead(
                    label=str(row.label),
                    count=count,
                    percentage=round(percentage, 2),
                )
            )

        return breakdowns

    def _get_zones_by_services(
        self,
        *,
        shop_id,
        start_utc: datetime,
        end_utc: datetime,
        completed_total: int,
    ) -> list[RepairShopDashboardZoneRead]:
        query = text(
            """
            SELECT
                COALESCE(i.address, 'Zona sin nombre') AS label,
                ROUND(i.latitude::numeric, 2) AS latitude,
                ROUND(i.longitude::numeric, 2) AS longitude,
                COUNT(*) AS total
            FROM request_assignment ra
            JOIN incident i ON i.id = ra.incident_id
            WHERE ra.state = true
              AND ra.repair_shop_id = :shop_id
              AND ra.status = :completed_status
              AND ra.responded_at IS NOT NULL
              AND ra.responded_at >= :start_utc
              AND ra.responded_at < :end_utc
            GROUP BY COALESCE(i.address, 'Zona sin nombre'), ROUND(i.latitude::numeric, 2), ROUND(i.longitude::numeric, 2)
            ORDER BY total DESC, label ASC
            LIMIT 6
            """
        )
        rows = self.db.exec(
            query,
            params={
                "shop_id": str(shop_id),
                "start_utc": start_utc,
                "end_utc": end_utc,
                "completed_status": AssignmentStatus.COMPLETED.name,
            },
        ).all()

        zones: list[RepairShopDashboardZoneRead] = []
        for row in rows:
            count = int(row.total or 0)
            percentage = (count / completed_total * 100.0) if completed_total > 0 else 0.0
            zones.append(
                RepairShopDashboardZoneRead(
                    label=str(row.label),
                    count=count,
                    percentage=round(percentage, 2),
                    latitude=float(row.latitude) if row.latitude is not None else None,
                    longitude=float(row.longitude) if row.longitude is not None else None,
                )
            )

        return zones
