import logging
from datetime import UTC, datetime
from decimal import Decimal, ROUND_HALF_UP
from math import ceil
from uuid import UUID

from app.core.config import settings
from app.modules.assignments.models import AssignmentStatus, RequestAssignment
from app.modules.incidents.models import IncidentStatus
from app.modules.realtime.services import ShopOfferNotificationService

from .base_service import AssignmentBaseService
from .candidate_shop_search_service import CandidateShopSearchService

logger = logging.getLogger(__name__)


class OfferEvaluationService(AssignmentBaseService):
    def evaluate_and_create_offers(
        self,
        *,
        incident_id: UUID,
        user_id: UUID,
        radius_steps_km: list[float],
        min_candidates: int,
        limit_per_radius: int,
        base_fee_bob: float,
        price_per_km_bob: float,
    ) -> dict:
        search_output = CandidateShopSearchService(self.db).search_candidate_shops(
            incident_id=incident_id,
            user_id=user_id,
            radius_steps_km=radius_steps_km,
            min_candidates=min_candidates,
            limit_per_radius=limit_per_radius,
        )

        incident = self._get_client_incident_or_404(user_id=user_id, incident_id=incident_id)
        candidates = search_output["candidates"]
        shop_ids = [candidate["shop_id"] for candidate in candidates]
        wallets_by_shop = self.wallet_lookup.map_active_wallets_by_shop_ids(shop_ids)

        created_offers: list[dict] = []
        discarded: list[dict] = []
        rank_counter = 1
        now_utc = datetime.now(UTC)

        for candidate in candidates:
            shop_id = UUID(str(candidate["shop_id"]))
            shop_name = candidate["shop_name"]
            distance_km = self._to_km_decimal(candidate["distance_km"])
            delivery_price = self._calculate_delivery_price(
                distance_km=distance_km,
                base_fee_bob=base_fee_bob,
                price_per_km_bob=price_per_km_bob,
            )
            estimated_minutes = self._calculate_estimated_minutes(distance_km=distance_km)

            open_assignment = self.request_assignment.get_open_by_incident_and_shop(
                incident_id=incident.id,
                repair_shop_id=shop_id,
            )
            if open_assignment:
                discarded.append(
                    {
                        "shop_id": shop_id,
                        "shop_name": shop_name,
                        "reason": "already_offered",
                    }
                )
                continue

            wallet = wallets_by_shop.get(str(shop_id))
            if not wallet:
                discarded.append(
                    {
                        "shop_id": shop_id,
                        "shop_name": shop_name,
                        "reason": "wallet_not_found",
                    }
                )
                continue

            if Decimal(wallet.balance) < delivery_price:
                discarded.append(
                    {
                        "shop_id": shop_id,
                        "shop_name": shop_name,
                        "reason": "insufficient_balance",
                    }
                )
                continue

            assignment = RequestAssignment(
                incident_id=incident.id,
                repair_shop_id=shop_id,
                status=AssignmentStatus.PENDING,
                queue_rank=rank_counter,
                offered_at=now_utc,
                distance_km=distance_km,
                delivery_price=delivery_price,
                estimated_minutes=estimated_minutes,
            )
            self.request_assignment.create(assignment)
            self.db.flush()
            rank_counter += 1

            created_offers.append(
                {
                    "request_assignment_id": assignment.id,
                    "shop_id": shop_id,
                    "shop_name": shop_name,
                    "distance_km": float(distance_km),
                    "delivery_price": float(delivery_price),
                    "estimated_minutes": estimated_minutes,
                }
            )

        self.db.commit()

        if created_offers:
            incident.status = IncidentStatus.SEARCHING_SHOP
            self.db.add(incident)
            self.db.commit()
            self._emit_incident_realtime_event(
                incident_id=incident.id,
                event_type="incident.status.changed",
                payload={
                    "status": incident.status,
                    "offers_created": len(created_offers),
                    "description": "Buscando taller para el incidente",
                },
                status=incident.status,
            )
            ShopOfferNotificationService(self.db).notify_next_offer_in_incident_queue_sync(
                incident.id
            )

        return {
            "incident_id": incident.id,
            "problem_id": incident.problem_id,
            "searched_candidates": len(candidates),
            "offers_created": len(created_offers),
            "offers": created_offers,
            "discarded": discarded,
        }

    def _calculate_delivery_price(
        self,
        *,
        distance_km: Decimal,
        base_fee_bob: float,
        price_per_km_bob: float,
    ) -> Decimal:
        base_fee = Decimal(str(base_fee_bob))
        rate_per_km = Decimal(str(price_per_km_bob))
        price = base_fee + (distance_km * rate_per_km)
        return price.quantize(Decimal("1"), rounding=ROUND_HALF_UP)

    def _to_km_decimal(self, value: float) -> Decimal:
        return Decimal(str(value)).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)

    def _calculate_estimated_minutes(self, *, distance_km: Decimal) -> int:
        speed_kmh = max(float(settings.ASSIGNMENT_ESTIMATED_SPEED_KMH), 0.1)
        floor_minutes = max(int(settings.ASSIGNMENT_ESTIMATED_MIN_FLOOR_MINUTES), 0)

        minutes = ceil((float(distance_km) / speed_kmh) * 60.0)
        return max(minutes, floor_minutes)

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
