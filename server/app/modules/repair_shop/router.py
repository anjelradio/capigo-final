from fastapi import APIRouter, Query, status
from uuid import UUID

from app.dependencies.auth import CurrentUser, DBSession
from app.modules.repair_shop.schemas import (
    AdminRecentServicesResponse,
    AdminRepairShopOverviewRead,
    AdminRepairShopsResponse,
    JoinShopByCodeRequest,
    RepairShopAddressPreviewRead,
    RepairShopCreate,
    RepairShopCreateResponse,
    RepairShopLocationUpdateRequest,
    RepairShopProfileUpdateRequest,
    RepairShopRead,
    ServiceRead,
    ShopInvitationCreateRequest,
    ShopInvitationRead,
    ShopMechanicRead,
    ShopServicesAssignRequest,
)
from app.modules.repair_shop.services import (
    AdminService,
    ShopCatalogService,
    ShopInvitationService,
    ShopMechanicService,
    ShopMembershipService,
    ShopProfileService,
)
from app.modules.user.schemas import UserRead

router = APIRouter(prefix="/repair-shop", tags=["Talleres"])


@router.get(
    "/admin/shops",
    response_model=AdminRepairShopsResponse,
    status_code=status.HTTP_200_OK,
)
def list_all_repair_shops_for_admin(db: DBSession, user: CurrentUser):
    return AdminService(db).list_all_repair_shops(admin_id=user.id)


@router.get(
    "/admin/shops/{shop_id}/overview",
    response_model=AdminRepairShopOverviewRead,
    status_code=status.HTTP_200_OK,
)
def get_repair_shop_overview_for_admin(db: DBSession, user: CurrentUser, shop_id: UUID):
    return AdminService(db).get_repair_shop_overview(
        admin_id=user.id,
        shop_id=shop_id,
    )


@router.get(
    "/admin/shops/{shop_id}/mechanics",
    response_model=list[ShopMechanicRead],
    status_code=status.HTTP_200_OK,
)
def list_shop_mechanics_for_admin(
    db: DBSession,
    user: CurrentUser,
    shop_id: UUID,
    is_available: bool = Query(default=False),
):
    return AdminService(db).list_shop_mechanics_for_admin(
        admin_id=user.id,
        shop_id=shop_id,
        only_available=is_available,
    )


@router.delete(
    "/admin/shops/{shop_id}/mechanics/{mechanic_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_shop_mechanic_for_admin(
    db: DBSession,
    user: CurrentUser,
    shop_id: UUID,
    mechanic_id: UUID,
):
    AdminService(db).delete_shop_mechanic_for_admin(
        admin_id=user.id,
        shop_id=shop_id,
        mechanic_id=mechanic_id,
    )


@router.get(
    "/admin/shops/{shop_id}/recent-services",
    response_model=AdminRecentServicesResponse,
    status_code=status.HTTP_200_OK,
)
def list_recent_services_for_shop(
    db: DBSession,
    user: CurrentUser,
    shop_id: UUID,
    limit: int = Query(default=5, ge=1, le=20),
):
    return AdminService(db).list_recent_services_for_shop(
        admin_id=user.id,
        shop_id=shop_id,
        limit=limit,
    )


@router.post(
    "/create/preview-address",
    response_model=RepairShopAddressPreviewRead,
    status_code=status.HTTP_200_OK,
)
def preview_address(db: DBSession, payload: RepairShopCreate, user: CurrentUser):
    _ = user
    text_address = ShopProfileService(db).preview_text_address(payload)

    return {
        "name": payload.name,
        "latitude": payload.latitude,
        "longitude": payload.longitude,
        "text_address": text_address,
    }


@router.post(
    "/create",
    response_model=RepairShopCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_repair_shop(db: DBSession, payload: RepairShopCreate, user: CurrentUser):
    shop, owner = ShopProfileService(db).create(payload, owner_id=user.id)

    return {
        "user": owner,
        "shop": shop,
    }


@router.get(
    "/me",
    response_model=RepairShopRead,
    status_code=status.HTTP_200_OK,
)
def get_current_user_shop(db: DBSession, user: CurrentUser):
    return ShopProfileService(db).get_shop_by_owner(user.id)


@router.get(
    "/services",
    response_model=list[ServiceRead],
    status_code=status.HTTP_200_OK,
)
def list_services(db: DBSession, user: CurrentUser):
    _ = user
    return ShopCatalogService(db).list_services()


@router.put(
    "/me/services",
    response_model=RepairShopRead,
    status_code=status.HTTP_200_OK,
)
def assign_services_to_my_shop(
    db: DBSession, payload: ShopServicesAssignRequest, user: CurrentUser
):
    return ShopCatalogService(db).assign_shop_services(payload, owner_id=user.id)


@router.get(
    "/me/services",
    response_model=list[ServiceRead],
    status_code=status.HTTP_200_OK,
)
def list_my_shop_services(db: DBSession, user: CurrentUser):
    return ShopCatalogService(db).list_my_shop_services(owner_id=user.id)


@router.get(
    "/me/mechanics",
    response_model=list[ShopMechanicRead],
    status_code=status.HTTP_200_OK,
)
def list_my_shop_mechanics(
    db: DBSession,
    user: CurrentUser,
    is_available: bool = Query(default=False),
):
    return ShopMechanicService(db).list_my_shop_mechanics(
        owner_id=user.id,
        only_available=is_available,
    )


@router.delete(
    "/me/mechanics/{mechanic_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_my_shop_mechanic(
    db: DBSession,
    user: CurrentUser,
    mechanic_id: UUID,
):
    ShopMechanicService(db).delete_my_shop_mechanic(
        owner_id=user.id,
        mechanic_id=mechanic_id,
    )


@router.patch(
    "/me/profile",
    response_model=RepairShopRead,
    status_code=status.HTTP_200_OK,
)
def update_my_shop_profile(
    db: DBSession, payload: RepairShopProfileUpdateRequest, user: CurrentUser
):
    return ShopProfileService(db).update_my_shop_profile(payload, owner_id=user.id)


@router.patch(
    "/me/location",
    response_model=RepairShopRead,
    status_code=status.HTTP_200_OK,
)
def update_my_shop_location(
    db: DBSession, payload: RepairShopLocationUpdateRequest, user: CurrentUser
):
    return ShopProfileService(db).update_my_shop_location(payload, owner_id=user.id)


@router.post(
    "/me/invitation",
    status_code=status.HTTP_204_NO_CONTENT,
)
def create_my_shop_invitation(
    db: DBSession, payload: ShopInvitationCreateRequest, user: CurrentUser
):
    ShopInvitationService(db).create_or_replace_my_shop_invitation(
        payload, owner_id=user.id
    )


@router.get(
    "/me/invitation",
    response_model=ShopInvitationRead | None,
    status_code=status.HTTP_200_OK,
)
def get_my_shop_invitation(db: DBSession, user: CurrentUser):
    return ShopInvitationService(db).get_my_shop_invitation(owner_id=user.id)


@router.delete(
    "/me/invitation",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_my_shop_invitation(db: DBSession, user: CurrentUser):
    ShopInvitationService(db).delete_my_shop_invitation(owner_id=user.id)


@router.post(
    "/me/join",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
)
def join_shop_by_code(db: DBSession, payload: JoinShopByCodeRequest, user: CurrentUser):
    return ShopMembershipService(db).join_shop_by_code(payload, user.id)


@router.post(
    "/me/unlink",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
)
def unlink_mechanic_from_shop(db: DBSession, user: CurrentUser):
    return ShopMembershipService(db).unlink_mechanic_from_shop(user.id)
