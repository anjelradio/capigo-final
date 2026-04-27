import secrets
import string
from datetime import datetime, timezone
from uuid import UUID
from zoneinfo import ZoneInfo

from fastapi import HTTPException

from app.modules.repair_shop.models import ShopInvitation
from app.modules.repair_shop.schemas import ShopInvitationCreateRequest, ShopInvitationRead

from .base_service import RepairShopBaseService


class ShopInvitationService(RepairShopBaseService):
    def create_or_replace_my_shop_invitation(
        self, payload: ShopInvitationCreateRequest, owner_id: UUID
    ) -> None:
        self._ensure_owner_role(
            owner_id,
            detail="Solo usuarios owner pueden generar invitaciones",
        )
        shop = self._get_shop_by_owner_or_404(owner_id)

        invitation = self.shop_invitation.get_by_shop_id(shop.id)
        code = self._generate_unique_invitation_code()

        try:
            if invitation:
                invitation.code = code
                invitation.expires_at = payload.expires_at
                invitation.shop_id = shop.id
                invitation.state = True
                self.db.add(invitation)
            else:
                self.shop_invitation.create(
                    ShopInvitation(
                        code=code,
                        expires_at=payload.expires_at,
                        shop_id=shop.id,
                    )
                )

            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    def get_my_shop_invitation(self, owner_id: UUID) -> ShopInvitationRead | None:
        shop = self._get_shop_by_owner_or_404(owner_id)
        invitation = self.shop_invitation.get_by_shop_id(shop.id)
        if not invitation:
            return None

        expires_at = invitation.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        now_utc = datetime.now(timezone.utc)
        status = "active" if expires_at > now_utc else "expired"
        expires_at_bo = expires_at.astimezone(ZoneInfo("America/La_Paz"))

        return ShopInvitationRead(
            code=invitation.code,
            expires_at=invitation.expires_at,
            expires_at_label=expires_at_bo.strftime("%d/%m/%Y - %H:%M"),
            status=status,
        )

    def delete_my_shop_invitation(self, owner_id: UUID) -> None:
        self._ensure_owner_role(
            owner_id,
            detail="Solo usuarios owner pueden eliminar invitaciones",
        )
        shop = self._get_shop_by_owner_or_404(owner_id)

        invitation = self.shop_invitation.get_by_shop_id(shop.id)
        if not invitation:
            raise HTTPException(status_code=404, detail="No hay invitacion activa")

        try:
            self.shop_invitation.soft_delete(invitation)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    def _generate_unique_invitation_code(self) -> str:
        alphabet = string.ascii_uppercase + string.digits

        for _ in range(40):
            code = "".join(secrets.choice(alphabet) for _ in range(6))
            if not self.shop_invitation.exists_code(code):
                return code

        raise HTTPException(
            status_code=500,
            detail="No se pudo generar un codigo de invitacion unico",
        )
