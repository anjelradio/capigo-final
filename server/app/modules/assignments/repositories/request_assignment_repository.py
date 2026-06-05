from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, case, or_, text
from sqlalchemy import func
from sqlmodel import Session, select

from app.modules.assignments.models import AssignmentStatus, RequestAssignment
from app.modules.incidents.models import Evidence, Incident, Problem
from app.modules.repair_shop.models import ShopMechanic
from app.modules.user.models import User, Vehicle


class RequestAssignmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_open_by_incident_and_shop(
        self,
        *,
        incident_id: UUID,
        repair_shop_id: UUID,
    ) -> RequestAssignment | None:
        query = select(RequestAssignment).where(
            RequestAssignment.incident_id == incident_id,
            RequestAssignment.repair_shop_id == repair_shop_id,
            RequestAssignment.state == True,
            RequestAssignment.status.in_(
                (
                    AssignmentStatus.PENDING,
                    AssignmentStatus.OFFERED,
                    AssignmentStatus.ACCEPTED,
                )
            ),
        )
        return self.db.exec(query).first()

    def create(self, assignment: RequestAssignment) -> RequestAssignment:
        self.db.add(assignment)
        return assignment

    def list_pending_not_notified_by_incident(self, incident_id: UUID) -> list[RequestAssignment]:
        query = (
            select(RequestAssignment)
            .where(
                RequestAssignment.incident_id == incident_id,
                RequestAssignment.state == True,
                RequestAssignment.status == AssignmentStatus.PENDING,
                RequestAssignment.notified_at.is_(None),
            )
            .order_by(RequestAssignment.queue_rank.asc(), RequestAssignment.created_date.asc())
        )
        return list(self.db.exec(query).all())

    def list_by_incident(self, incident_id: UUID) -> list[RequestAssignment]:
        query = (
            select(RequestAssignment)
            .where(
                RequestAssignment.incident_id == incident_id,
                RequestAssignment.state == True,
            )
            .order_by(RequestAssignment.created_date.asc())
        )
        return list(self.db.exec(query).all())

    def list_pending_active_by_shop(self, shop_id: UUID, now_utc: datetime) -> list[RequestAssignment]:
        query = (
            select(RequestAssignment)
            .where(
                RequestAssignment.repair_shop_id == shop_id,
                RequestAssignment.state == True,
                RequestAssignment.status == AssignmentStatus.PENDING,
                RequestAssignment.expires_at.is_not(None),
                RequestAssignment.expires_at > now_utc,
            )
            .order_by(RequestAssignment.notified_at.desc(), RequestAssignment.queue_rank.asc())
        )
        return list(self.db.exec(query).all())

    def list_history_by_shop(self, shop_id: UUID, now_utc: datetime) -> list[RequestAssignment]:
        query = (
            select(RequestAssignment)
            .where(
                RequestAssignment.repair_shop_id == shop_id,
                RequestAssignment.state == True,
                or_(
                    RequestAssignment.status != AssignmentStatus.PENDING,
                    and_(
                        RequestAssignment.status == AssignmentStatus.PENDING,
                        RequestAssignment.expires_at.is_not(None),
                        RequestAssignment.expires_at <= now_utc,
                    ),
                ),
            )
            .order_by(RequestAssignment.modified_date.desc(), RequestAssignment.queue_rank.asc())
        )
        return list(self.db.exec(query).all())

    def get_by_id(self, assignment_id: UUID) -> RequestAssignment | None:
        query = select(RequestAssignment).where(
            RequestAssignment.id == assignment_id,
            RequestAssignment.state == True,
        )
        return self.db.exec(query).first()

    def list_offered_by_incident(self, incident_id: UUID) -> list[RequestAssignment]:
        query = (
            select(RequestAssignment)
            .where(
                RequestAssignment.incident_id == incident_id,
                RequestAssignment.state == True,
                RequestAssignment.status == AssignmentStatus.OFFERED,
            )
            .order_by(RequestAssignment.responded_at.desc(), RequestAssignment.created_date.desc())
        )
        return list(self.db.exec(query).all())

    def list_offer_candidates_except(
        self,
        *,
        incident_id: UUID,
        exclude_assignment_id: UUID,
    ) -> list[RequestAssignment]:
        query = (
            select(RequestAssignment)
            .where(
                RequestAssignment.incident_id == incident_id,
                RequestAssignment.id != exclude_assignment_id,
                RequestAssignment.state == True,
                RequestAssignment.status.in_(
                    (
                        AssignmentStatus.PENDING,
                        AssignmentStatus.OFFERED,
                    )
                ),
            )
            .order_by(RequestAssignment.queue_rank.asc(), RequestAssignment.created_date.asc())
        )
        return list(self.db.exec(query).all())

    def get_by_id_and_mechanic(self, *, assignment_id: UUID, mechanic_id: UUID) -> RequestAssignment | None:
        query = select(RequestAssignment).where(
            RequestAssignment.id == assignment_id,
            RequestAssignment.mechanic_id == mechanic_id,
            RequestAssignment.state == True,
        )
        return self.db.exec(query).first()

    def get_latest_active_by_mechanic(self, mechanic_id: UUID) -> RequestAssignment | None:
        query = (
            select(RequestAssignment)
            .where(
                RequestAssignment.mechanic_id == mechanic_id,
                RequestAssignment.state == True,
                RequestAssignment.status == AssignmentStatus.ACCEPTED,
            )
            .order_by(RequestAssignment.created_date.desc())
        )
        return self.db.exec(query).first()

    def get_latest_active_by_incident(self, incident_id: UUID) -> RequestAssignment | None:
        query = (
            select(RequestAssignment)
            .where(
                RequestAssignment.incident_id == incident_id,
                RequestAssignment.state == True,
                RequestAssignment.status == AssignmentStatus.ACCEPTED,
            )
            .order_by(RequestAssignment.created_date.desc())
        )
        return self.db.exec(query).first()

    def get_latest_by_incident(self, incident_id: UUID) -> RequestAssignment | None:
        query = (
            select(RequestAssignment)
            .where(
                RequestAssignment.incident_id == incident_id,
                RequestAssignment.state == True,
            )
            .order_by(RequestAssignment.created_date.desc())
        )
        return self.db.exec(query).first()

    def get_latest_by_incident_and_mechanic(
        self,
        *,
        incident_id: UUID,
        mechanic_id: UUID,
    ) -> RequestAssignment | None:
        query = (
            select(RequestAssignment)
            .where(
                RequestAssignment.incident_id == incident_id,
                RequestAssignment.mechanic_id == mechanic_id,
                RequestAssignment.state == True,
            )
            .order_by(RequestAssignment.created_date.desc())
        )
        return self.db.exec(query).first()

    def list_services_by_mechanic(
        self,
        *,
        mechanic_id: UUID,
        only_completed: bool,
    ) -> list[dict]:
        query = (
            select(
                RequestAssignment,
                Incident,
                Problem,
                Vehicle.plate,
            )
            .join(Incident, Incident.id == RequestAssignment.incident_id)
            .join(Problem, Problem.id == Incident.problem_id, isouter=True)
            .join(Vehicle, Vehicle.id == Incident.vehicle_id, isouter=True)
            .where(
                RequestAssignment.mechanic_id == mechanic_id,
                RequestAssignment.state == True,
                RequestAssignment.status.notin_(
                    (
                        AssignmentStatus.PENDING,
                        AssignmentStatus.REJECTED,
                        AssignmentStatus.EXPIRED,
                    )
                ),
            )
            .order_by(RequestAssignment.modified_date.desc(), RequestAssignment.created_date.desc())
        )

        if only_completed:
            query = query.where(RequestAssignment.status == AssignmentStatus.COMPLETED)

        rows = self.db.exec(query).all()
        return [
            {
                "assignment_id": assignment.id,
                "incident_id": incident.id,
                "assignment_status": assignment.status.value,
                "incident_status": incident.status.value,
                "incident_description": incident.description,
                "problem_name": problem.name if problem else None,
                "vehicle_plate": vehicle_plate,
                "created_date": assignment.created_date,
                "updated_date": assignment.modified_date,
            }
            for assignment, incident, problem, vehicle_plate in rows
        ]

    def exists_by_incident_and_shop(self, *, incident_id: UUID, shop_id: UUID) -> bool:
        query = select(RequestAssignment.id).where(
            RequestAssignment.incident_id == incident_id,
            RequestAssignment.repair_shop_id == shop_id,
            RequestAssignment.state == True,
        )
        return self.db.exec(query).first() is not None

    def exists_by_incident_and_mechanic(self, *, incident_id: UUID, mechanic_id: UUID) -> bool:
        query = select(RequestAssignment.id).where(
            RequestAssignment.incident_id == incident_id,
            RequestAssignment.mechanic_id == mechanic_id,
            RequestAssignment.state == True,
        )
        return self.db.exec(query).first() is not None

    def list_pending_by_incident_except_shop(
        self, *, incident_id: UUID, exclude_shop_id: UUID
    ) -> list[RequestAssignment]:
        query = (
            select(RequestAssignment)
            .where(
                RequestAssignment.incident_id == incident_id,
                RequestAssignment.state == True,
                RequestAssignment.status == AssignmentStatus.PENDING,
                RequestAssignment.repair_shop_id != exclude_shop_id,
            )
            .order_by(RequestAssignment.queue_rank.asc(), RequestAssignment.created_date.asc())
        )
        return list(self.db.exec(query).all())

    def list_pending_expired(self, *, now_utc: datetime, limit: int = 100) -> list[RequestAssignment]:
        query = (
            select(RequestAssignment)
            .where(
                RequestAssignment.state == True,
                RequestAssignment.status == AssignmentStatus.PENDING,
                RequestAssignment.expires_at.is_not(None),
                RequestAssignment.expires_at <= now_utc,
            )
            .order_by(RequestAssignment.expires_at.asc(), RequestAssignment.queue_rank.asc())
            .limit(limit)
        )
        return list(self.db.exec(query).all())

    def list_assignments_for_shop(self, shop_id: UUID) -> list[RequestAssignment]:
        status_order = case(
            (RequestAssignment.status == AssignmentStatus.ACCEPTED, 0),
            (RequestAssignment.status == AssignmentStatus.COMPLETED, 1),
            (RequestAssignment.status == AssignmentStatus.CANCELLED, 2),
            else_=3,
        )
        query = (
            select(RequestAssignment)
            .where(
                RequestAssignment.repair_shop_id == shop_id,
                RequestAssignment.state == True,
                RequestAssignment.status.in_(
                    (
                        AssignmentStatus.ACCEPTED,
                        AssignmentStatus.COMPLETED,
                        AssignmentStatus.CANCELLED,
                    )
                ),
            )
            .order_by(status_order.asc(), RequestAssignment.created_date.desc())
        )
        return list(self.db.exec(query).all())

    def list_recent_accepted_services_by_shop(
        self,
        *,
        shop_id: UUID,
        limit: int = 5,
    ) -> list[dict]:
        query = (
            select(
                RequestAssignment,
                Incident,
                Problem,
                User.first_name,
                User.last_name,
            )
            .join(Incident, Incident.id == RequestAssignment.incident_id)
            .join(Problem, Problem.id == Incident.problem_id, isouter=True)
            .join(ShopMechanic, ShopMechanic.id == RequestAssignment.mechanic_id, isouter=True)
            .join(User, User.id == ShopMechanic.user_id, isouter=True)
            .where(
                RequestAssignment.repair_shop_id == shop_id,
                RequestAssignment.state == True,
                RequestAssignment.status.notin_(
                    (
                        AssignmentStatus.EXPIRED,
                        AssignmentStatus.FAILED,
                        AssignmentStatus.PENDING,
                    )
                ),
            )
            .order_by(
                RequestAssignment.responded_at.desc(),
                RequestAssignment.modified_date.desc(),
            )
            .limit(limit)
        )

        rows = self.db.exec(query).all()
        services: list[dict] = []
        for assignment, incident, problem, first_name, last_name in rows:
            mechanic_name = None
            if first_name and last_name:
                mechanic_name = f"{first_name} {last_name}".strip()

            services.append(
                {
                    "assignment_id": assignment.id,
                    "incident_id": incident.id,
                    "incident_description": incident.description,
                    "incident_address": incident.address,
                    "incident_status": incident.status.value,
                    "problem_name": problem.name if problem else None,
                    "mechanic_name": mechanic_name,
                    "accepted_at": assignment.responded_at,
                    "created_date": assignment.created_date,
                }
            )

        return services

    def get_mechanic_full_name(self, mechanic_id: UUID | None) -> str | None:
        contact = self.get_mechanic_contact(mechanic_id)
        if not contact:
            return None
        return contact["full_name"]

    def get_mechanic_contact(self, mechanic_id: UUID | None) -> dict | None:
        if mechanic_id is None:
            return None

        query = (
            select(User.first_name, User.last_name, User.phone)
            .join(ShopMechanic, ShopMechanic.user_id == User.id)
            .where(
                ShopMechanic.id == mechanic_id,
                ShopMechanic.state == True,
                User.state == True,
            )
        )
        row = self.db.exec(query).first()
        if not row:
            return None

        full_name = f"{row.first_name} {row.last_name}".strip()
        return {
            "full_name": full_name if full_name else None,
            "phone": row.phone,
        }

    def get_offer_notification_payload(self, assignment_id: UUID) -> dict | None:
        query = text(
            """
            SELECT
                ra.id AS assignment_id,
                ra.incident_id AS incident_id,
                ra.repair_shop_id AS shop_id,
                ra.status AS assignment_status,
                rs.latitude AS shop_latitude,
                rs.longitude AS shop_longitude,
                ra.distance_km AS distance_km,
                ra.delivery_price AS delivery_price,
                ra.quoted_price AS quoted_price,
                ra.estimated_minutes AS estimated_minutes,
                ra.expires_at AS expires_at,
                i.description AS incident_description,
                i.status AS incident_status,
                i.latitude AS incident_latitude,
                i.longitude AS incident_longitude,
                p.id AS problem_id,
                p.name AS problem_name
            FROM request_assignment ra
            JOIN incident i ON i.id = ra.incident_id
            JOIN repair_shop rs ON rs.id = ra.repair_shop_id
            LEFT JOIN problem p ON p.id = i.problem_id
            WHERE ra.id = :assignment_id
            """
        )

        row = self.db.exec(query, params={"assignment_id": str(assignment_id)}).first()
        if not row:
            return None

        evidence_query = (
            select(Evidence.url)
            .where(
                Evidence.incident_id == row.incident_id,
                Evidence.state == True,
            )
            .order_by(Evidence.created_date.asc())
        )
        evidence_urls = [url for url in self.db.exec(evidence_query).all()]

        return {
            "assignment_id": row.assignment_id,
            "incident_id": row.incident_id,
            "shop_id": row.shop_id,
            "assignment_status": str(row.assignment_status).split(".")[-1].lower()
            if row.assignment_status is not None
            else None,
            "shop_latitude": float(row.shop_latitude) if row.shop_latitude is not None else None,
            "shop_longitude": float(row.shop_longitude) if row.shop_longitude is not None else None,
            "distance_km": float(row.distance_km) if row.distance_km is not None else None,
            "delivery_price": float(row.delivery_price) if row.delivery_price is not None else None,
            "quoted_price": float(row.quoted_price) if row.quoted_price is not None else None,
            "estimated_minutes": int(row.estimated_minutes) if row.estimated_minutes is not None else None,
            "expires_at": row.expires_at,
            "incident_description": row.incident_description,
            "incident_status": str(row.incident_status).split(".")[-1].lower()
            if row.incident_status is not None
            else None,
            "incident_latitude": float(row.incident_latitude),
            "incident_longitude": float(row.incident_longitude),
            "problem_id": row.problem_id,
            "problem_name": row.problem_name,
            "evidence_urls": evidence_urls,
        }

    def get_service_report_payload(self, assignment_id: UUID) -> dict | None:
        query = text(
            """
            SELECT
                ra.id AS assignment_id,
                ra.status AS assignment_status,
                ra.distance_km AS distance_km,
                ra.delivery_price AS delivery_price,
                ra.estimated_minutes AS estimated_minutes,
                ra.created_date AS assignment_created_at,
                ra.responded_at AS assignment_responded_at,
                i.id AS incident_id,
                i.status AS incident_status,
                i.description AS incident_description,
                i.address AS incident_address,
                i.latitude AS incident_latitude,
                i.longitude AS incident_longitude,
                i.created_date AS incident_created_at,
                p.id AS problem_id,
                p.name AS problem_name,
                rs.id AS shop_id,
                rs.name AS shop_name,
                rs.text_address AS shop_address,
                u_mech.first_name AS mechanic_first_name,
                u_mech.last_name AS mechanic_last_name,
                u_mech.phone AS mechanic_phone,
                v.make AS vehicle_make,
                v.model AS vehicle_model,
                v.plate AS vehicle_plate,
                v.color AS vehicle_color,
                v.year AS vehicle_year,
                vt.name AS vehicle_type,
                rep.id AS report_id,
                rep.description AS report_description,
                rep.labor_price AS labor_price,
                rep.created_date AS report_created_at,
                fb.rating AS feedback_rating,
                fb.comment AS feedback_comment,
                fb.created_date AS feedback_created_at
            FROM request_assignment ra
            JOIN incident i ON i.id = ra.incident_id
            JOIN repair_shop rs ON rs.id = ra.repair_shop_id
            LEFT JOIN problem p ON p.id = i.problem_id
            LEFT JOIN shop_mechanics sm ON sm.id = ra.mechanic_id
            LEFT JOIN "user" u_mech ON u_mech.id = sm.user_id
            LEFT JOIN vehicle v ON v.id = i.vehicle_id
            LEFT JOIN vehicle_type vt ON vt.id = v.type_id
            LEFT JOIN incident_service_report rep ON rep.incident_id = i.id AND rep.state = true
            LEFT JOIN incident_feedback fb ON fb.incident_id = i.id AND fb.state = true
            WHERE ra.id = :assignment_id AND ra.state = true
            """
        )

        row = self.db.exec(query, params={"assignment_id": str(assignment_id)}).first()
        if not row:
            return None

        return {
            "assignment_id": row.assignment_id,
            "assignment_status": row.assignment_status,
            "distance_km": float(row.distance_km) if row.distance_km is not None else None,
            "delivery_price": float(row.delivery_price) if row.delivery_price is not None else None,
            "estimated_minutes": int(row.estimated_minutes) if row.estimated_minutes is not None else None,
            "assignment_created_at": row.assignment_created_at,
            "assignment_responded_at": row.assignment_responded_at,
            "incident_id": row.incident_id,
            "incident_status": row.incident_status,
            "incident_description": row.incident_description,
            "incident_address": row.incident_address,
            "incident_latitude": float(row.incident_latitude)
            if row.incident_latitude is not None
            else None,
            "incident_longitude": float(row.incident_longitude)
            if row.incident_longitude is not None
            else None,
            "incident_created_at": row.incident_created_at,
            "problem_id": row.problem_id,
            "problem_name": row.problem_name,
            "shop_id": row.shop_id,
            "shop_name": row.shop_name,
            "shop_address": row.shop_address,
            "mechanic_name": (
                f"{row.mechanic_first_name} {row.mechanic_last_name}".strip()
                if row.mechanic_first_name and row.mechanic_last_name
                else None
            ),
            "mechanic_phone": row.mechanic_phone,
            "vehicle_make": row.vehicle_make,
            "vehicle_model": row.vehicle_model,
            "vehicle_plate": row.vehicle_plate,
            "vehicle_color": row.vehicle_color,
            "vehicle_year": row.vehicle_year,
            "vehicle_type": row.vehicle_type,
            "report_id": row.report_id,
            "report_description": row.report_description,
            "labor_price": float(row.labor_price) if row.labor_price is not None else None,
            "report_created_at": row.report_created_at,
            "feedback_rating": row.feedback_rating,
            "feedback_comment": row.feedback_comment,
            "feedback_created_at": row.feedback_created_at,
        }

    def get_today_status_totals_for_mechanic(
        self,
        *,
        mechanic_id: UUID,
        start_utc: datetime,
        end_utc: datetime,
    ) -> dict[str, int]:
        query = (
            select(
                RequestAssignment.status,
                func.count(RequestAssignment.id),
            )
            .where(
                RequestAssignment.mechanic_id == mechanic_id,
                RequestAssignment.state == True,
                RequestAssignment.responded_at.is_not(None),
                RequestAssignment.responded_at >= start_utc,
                RequestAssignment.responded_at < end_utc,
                RequestAssignment.status.in_(
                    (
                        AssignmentStatus.COMPLETED,
                        AssignmentStatus.CANCELLED,
                    )
                ),
            )
            .group_by(RequestAssignment.status)
        )

        completed = 0
        cancelled = 0
        for status, total in self.db.exec(query).all():
            if status == AssignmentStatus.COMPLETED:
                completed = int(total)
            elif status == AssignmentStatus.CANCELLED:
                cancelled = int(total)

        return {
            "completed_today": completed,
            "cancelled_today": cancelled,
        }
