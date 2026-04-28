import logging
import unicodedata
from typing import Any
from uuid import UUID

import httpx
from fastapi import HTTPException

from app.modules.repair_shop.models import RepairShop
from app.modules.repair_shop.schemas import (
    RepairShopCreate,
    RepairShopLocationUpdateRequest,
    RepairShopProfileUpdateRequest,
)
from app.modules.user.models import User, UserRole
from app.modules.wallet.models import Wallet
from app.modules.wallet.repositories import WalletRepository

from .base_service import RepairShopBaseService

logger = logging.getLogger(__name__)

NOMINATIM_REVERSE_URL = "https://nominatim.openstreetmap.org/reverse"
FALLBACK_TEXT_ADDRESS = "Ubicacion de taller"


class ShopProfileService(RepairShopBaseService):
    def resolve_text_address(self, latitude: float, longitude: float) -> str:
        params = {
            "lat": latitude,
            "lon": longitude,
            "format": "jsonv2",
            "accept-language": "es",
        }
        headers = {
            "User-Agent": "revo-repairshop-api/1.0",
        }

        try:
            with httpx.Client(timeout=5.0, headers=headers) as client:
                response = client.get(NOMINATIM_REVERSE_URL, params=params)
                response.raise_for_status()

            payload = response.json()
            address = self._build_short_address(payload)
            if address:
                return address
        except Exception as error:
            logger.warning(
                "No se pudo resolver text_address con reverse geocoding: %s", error
            )

        return FALLBACK_TEXT_ADDRESS

    def _build_short_address(self, payload: dict[str, Any]) -> str:
        address = payload.get("address")
        display_name = str(payload.get("display_name") or "").strip()
        if not display_name:
            return ""

        parts = [part.strip() for part in display_name.split(",") if part.strip()]
        if not parts:
            return ""

        excluded_values = self._get_excluded_macro_location_values(address)
        filtered_parts = [
            part for part in parts if self._normalize_text(part) not in excluded_values
        ]

        return ", ".join(filtered_parts).strip()

    def _get_excluded_macro_location_values(self, address: Any) -> set[str]:
        if not isinstance(address, dict):
            return set()

        excluded_keys = {
            "city",
            "town",
            "village",
            "municipality",
            "city_district",
            "county",
            "state_district",
            "state",
            "region",
            "country",
            "country_code",
            "continent",
        }

        excluded_values: set[str] = set()
        for key in excluded_keys:
            value = str(address.get(key) or "").strip()
            if not value:
                continue

            normalized = self._normalize_text(value)
            if normalized:
                excluded_values.add(normalized)

            for prefix in ("provincia ", "departamento ", "department "):
                if normalized.startswith(prefix):
                    excluded_values.add(normalized[len(prefix) :].strip())

        return excluded_values

    def _normalize_text(self, value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value)
        ascii_text = "".join(
            char for char in normalized if not unicodedata.combining(char)
        )
        return " ".join(ascii_text.lower().split())

    def preview_text_address(self, payload: RepairShopCreate) -> str:
        text_address = self.resolve_text_address(payload.latitude, payload.longitude)
        logger.info(
            "Preview reverse geocoding | name=%s lat=%s lng=%s text_address=%s",
            payload.name,
            payload.latitude,
            payload.longitude,
            text_address,
        )
        return text_address

    def create(self, payload: RepairShopCreate, owner_id: UUID) -> tuple[RepairShop, User]:
        owner = self._get_user_or_404(owner_id)
        wallet_repository = WalletRepository(self.db)

        if owner.role != UserRole.CLIENT:
            raise HTTPException(
                status_code=409,
                detail="Solo usuarios client pueden crear su primer taller",
            )

        if self.repair_shop.get_by_name(payload.name):
            raise HTTPException(
                status_code=409, detail="El nombre del taller ya esta en uso"
            )

        if self.repair_shop.get_by_owner_id(owner_id):
            raise HTTPException(
                status_code=409,
                detail="El usuario ya tiene un taller registrado",
            )

        text_address = self.resolve_text_address(payload.latitude, payload.longitude)

        try:
            shop = RepairShop(
                name=payload.name,
                latitude=payload.latitude,
                longitude=payload.longitude,
                text_address=text_address,
                owner_id=owner_id,
            )

            self.repair_shop.create(shop)
            wallet_repository.create(Wallet(repair_shop_id=shop.id))
            owner.role = UserRole.OWNER
            self.db.add(owner)
            self.db.flush()
            self.db.commit()
            self.db.refresh(shop)
            self.db.refresh(owner)

            return shop, owner
        except Exception:
            self.db.rollback()
            raise

    def get_shop_by_owner(self, owner_id: UUID) -> RepairShop:
        return self._get_shop_by_owner_or_404(owner_id)

    def update_my_shop_profile(
        self, payload: RepairShopProfileUpdateRequest, owner_id: UUID
    ) -> RepairShop:
        self._ensure_owner_role(
            owner_id,
            detail="Solo usuarios owner pueden editar el perfil del taller",
        )
        shop = self._get_shop_by_owner_or_404(owner_id)

        existing_shop = self.repair_shop.get_by_name(payload.name)
        if existing_shop and existing_shop.id != shop.id:
            raise HTTPException(
                status_code=409,
                detail="El nombre del taller ya esta en uso",
            )

        try:
            shop.name = payload.name
            shop.text_address = payload.text_address
            self.db.add(shop)
            self.db.commit()
            self.db.refresh(shop)
            return shop
        except Exception:
            self.db.rollback()
            raise

    def update_my_shop_location(
        self, payload: RepairShopLocationUpdateRequest, owner_id: UUID
    ) -> RepairShop:
        self._ensure_owner_role(
            owner_id,
            detail="Solo usuarios owner pueden editar la ubicacion del taller",
        )
        shop = self._get_shop_by_owner_or_404(owner_id)

        text_address = self.resolve_text_address(payload.latitude, payload.longitude)

        try:
            shop.latitude = payload.latitude
            shop.longitude = payload.longitude
            shop.text_address = text_address
            self.db.add(shop)
            self.db.commit()
            self.db.refresh(shop)
            return shop
        except Exception:
            self.db.rollback()
            raise
