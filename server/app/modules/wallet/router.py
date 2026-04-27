from uuid import UUID

from fastapi import APIRouter, status

from app.dependencies.auth import CurrentUser, DBSession
from app.modules.wallet.schemas import (
    OwnerWalletBalanceRead,
    OwnerWalletTopupConfirmResponse,
    OwnerWalletTopupQrCreateRequest,
    OwnerWalletTopupQrRead,
    OwnerWalletTransactionsResponse,
)
from app.modules.wallet.services import OwnerWalletService

router = APIRouter(prefix="/wallet", tags=["Billetera"])


@router.get(
    "/me/balance",
    response_model=OwnerWalletBalanceRead,
    status_code=status.HTTP_200_OK,
)
def get_my_wallet_balance(db: DBSession, user: CurrentUser):
    return OwnerWalletService(db).get_my_wallet_balance(owner_id=user.id)


@router.get(
    "/me/transactions",
    response_model=OwnerWalletTransactionsResponse,
    status_code=status.HTTP_200_OK,
)
def list_my_wallet_transactions(db: DBSession, user: CurrentUser):
    return OwnerWalletService(db).list_my_wallet_transactions(owner_id=user.id)


@router.post(
    "/me/topups/qr",
    response_model=OwnerWalletTopupQrRead,
    status_code=status.HTTP_201_CREATED,
)
def create_my_topup_qr(
    db: DBSession,
    user: CurrentUser,
    payload: OwnerWalletTopupQrCreateRequest,
):
    return OwnerWalletService(db).create_my_topup_qr(
        owner_id=user.id,
        amount=payload.amount,
    )


@router.post(
    "/me/topups/{transaction_id}/confirm",
    response_model=OwnerWalletTopupConfirmResponse,
    status_code=status.HTTP_200_OK,
)
def confirm_my_topup(db: DBSession, user: CurrentUser, transaction_id: UUID):
    return OwnerWalletService(db).confirm_my_topup(
        owner_id=user.id,
        transaction_id=transaction_id,
    )
