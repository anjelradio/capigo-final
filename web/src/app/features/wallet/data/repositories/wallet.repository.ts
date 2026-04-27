import { Injectable, inject } from '@angular/core';

import type { ApiResult } from '../../../shared/data/types/api-result';
import type {
  OwnerWalletBalance,
  OwnerWalletTopupConfirm,
  OwnerWalletTopupQr,
  OwnerWalletTransaction,
} from '../../domain/entities/wallet';
import { WalletApiService } from '../api/wallet-api.service';
import type {
  OwnerWalletBalanceData,
  OwnerWalletTopupConfirmData,
  OwnerWalletTopupQrData,
  OwnerWalletTransactionData,
} from '../schemas/wallet.schema';

@Injectable({ providedIn: 'root' })
export class WalletRepository {
  private readonly walletApi = inject(WalletApiService);

  async getMyWalletBalance(): Promise<ApiResult<OwnerWalletBalance>> {
    const response = await this.walletApi.getMyWalletBalance();
    if (!response.ok) {
      return response;
    }

    return {
      ok: true,
      data: this.mapBalance(response.data),
    };
  }

  async listMyWalletTransactions(): Promise<ApiResult<OwnerWalletTransaction[]>> {
    const response = await this.walletApi.listMyWalletTransactions();
    if (!response.ok) {
      return response;
    }

    return {
      ok: true,
      data: response.data.map((transaction) => this.mapTransaction(transaction)),
    };
  }

  async createMyTopupQr(amount: number): Promise<ApiResult<OwnerWalletTopupQr>> {
    const response = await this.walletApi.createMyTopupQr(amount);
    if (!response.ok) {
      return response;
    }

    return {
      ok: true,
      data: this.mapTopupQr(response.data),
    };
  }

  async confirmMyTopup(transactionId: string): Promise<ApiResult<OwnerWalletTopupConfirm>> {
    const response = await this.walletApi.confirmMyTopup(transactionId);
    if (!response.ok) {
      return response;
    }

    return {
      ok: true,
      data: this.mapTopupConfirm(response.data),
    };
  }

  private mapBalance(balance: OwnerWalletBalanceData): OwnerWalletBalance {
    return {
      walletId: balance.wallet_id,
      repairShopId: balance.repair_shop_id,
      balance: balance.balance,
      updatedAt: balance.updated_at,
    };
  }

  private mapTransaction(transaction: OwnerWalletTransactionData): OwnerWalletTransaction {
    return {
      id: transaction.id,
      type: transaction.type,
      status: transaction.status,
      amount: transaction.amount,
      balanceBefore: transaction.balance_before,
      balanceAfter: transaction.balance_after,
      description: transaction.description ?? null,
      createdAt: transaction.created_at,
    };
  }

  private mapTopupQr(topup: OwnerWalletTopupQrData): OwnerWalletTopupQr {
    return {
      transactionId: topup.transaction_id,
      internalReference: topup.internal_reference,
      amount: topup.amount,
      walletId: topup.wallet_id,
      repairShopId: topup.repair_shop_id,
      generatedAt: topup.generated_at,
      expiresAt: topup.expires_at,
      status: topup.status,
      qrPayload: topup.qr_payload,
      qrImageUrl: topup.qr_image_url,
    };
  }

  private mapTopupConfirm(confirm: OwnerWalletTopupConfirmData): OwnerWalletTopupConfirm {
    return {
      transactionId: confirm.transaction_id,
      status: confirm.status,
      previousBalance: confirm.previous_balance,
      newBalance: confirm.new_balance,
    };
  }
}
