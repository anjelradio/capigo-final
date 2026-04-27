from uuid import UUID

from app.modules.incidents.models import IncidentStatus

from .base_service import AssignmentBaseService


class CandidateShopSearchService(AssignmentBaseService):
    def search_candidate_shops(
        self,
        *,
        incident_id: UUID,
        user_id: UUID,
        radius_steps_km: list[float],
        min_candidates: int,
        limit_per_radius: int,
    ) -> dict:
        self._ensure_client_role(
            user_id,
            detail="Solo usuarios client pueden buscar talleres candidatos",
        )
        incident = self._get_client_incident_or_404(user_id=user_id, incident_id=incident_id)
        self._ensure_classified_incident(incident)

        if incident.status != IncidentStatus.SEARCHING_SHOP:
            incident.status = IncidentStatus.SEARCHING_SHOP
            self.db.add(incident)
            self.db.commit()
            self.db.refresh(incident)

        candidates: list[dict] = []
        seen_shop_ids: set[str] = set()

        for radius_km in radius_steps_km:
            scoped = self.candidate_shop.search_by_problem_and_radius(
                problem_id=incident.problem_id,
                incident_latitude=incident.latitude,
                incident_longitude=incident.longitude,
                radius_km=radius_km,
                limit=limit_per_radius,
            )

            for row in scoped:
                shop_id = str(row["shop_id"])
                if shop_id in seen_shop_ids:
                    continue
                seen_shop_ids.add(shop_id)
                candidates.append(row)

            if len(candidates) >= min_candidates:
                break

        candidates = sorted(candidates, key=lambda item: float(item["distance_km"]))

        return {
            "incident_id": incident.id,
            "problem_id": incident.problem_id,
            "searched_radius_steps_km": radius_steps_km,
            "candidates_found": len(candidates),
            "candidates": candidates,
        }
