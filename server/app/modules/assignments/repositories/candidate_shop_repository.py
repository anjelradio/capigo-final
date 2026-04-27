from uuid import UUID

from sqlalchemy import text
from sqlmodel import Session


class CandidateShopRepository:
    def __init__(self, db: Session):
        self.db = db

    def search_by_problem_and_radius(
        self,
        *,
        problem_id: UUID,
        incident_latitude: float,
        incident_longitude: float,
        radius_km: float,
        limit: int,
    ) -> list[dict]:
        query = text(
            """
            SELECT
                rs.id AS shop_id,
                rs.name AS shop_name,
                rs.latitude AS shop_latitude,
                rs.longitude AS shop_longitude,
                ST_DistanceSphere(
                    ST_MakePoint(rs.longitude, rs.latitude),
                    ST_MakePoint(:incident_longitude, :incident_latitude)
                ) / 1000.0 AS distance_km
            FROM repair_shop rs
            WHERE
                rs.state = true
                AND rs.is_available = true
                AND ST_DWithin(
                    ST_SetSRID(ST_MakePoint(rs.longitude, rs.latitude), 4326)::geography,
                    ST_SetSRID(ST_MakePoint(:incident_longitude, :incident_latitude), 4326)::geography,
                    :radius_meters
                )
                AND EXISTS (
                    SELECT 1
                    FROM shop_services ss
                    JOIN services s ON s.id = ss.service_id
                    JOIN problem_service_map psm ON psm.service_id = ss.service_id
                    WHERE
                        ss.shop_id = rs.id
                        AND ss.state = true
                        AND ss.is_available = true
                        AND s.state = true
                        AND s.is_available = true
                        AND psm.state = true
                        AND psm.problem_id = :problem_id
                )
            ORDER BY distance_km ASC
            LIMIT :limit_value
            """
        )

        rows = self.db.exec(
            query,
            params={
                "problem_id": str(problem_id),
                "incident_latitude": incident_latitude,
                "incident_longitude": incident_longitude,
                "radius_meters": radius_km * 1000.0,
                "limit_value": max(limit, 1),
            },
        ).all()

        result: list[dict] = []
        for row in rows:
            result.append(
                {
                    "shop_id": row.shop_id,
                    "shop_name": row.shop_name,
                    "shop_latitude": float(row.shop_latitude),
                    "shop_longitude": float(row.shop_longitude),
                    "distance_km": float(row.distance_km),
                }
            )

        return result
