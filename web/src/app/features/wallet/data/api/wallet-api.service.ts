import { Injectable, inject } from '@angular/core';

import { environment } from '../../../../../environments/environment';
import { API_ENDPOINTS } from '../../../../core/config/api-endpoints';
import { AuthTokenService } from '../../../../core/services/auth-token.service';
import {
  errorResult,
  serverErrorResult,
} from '../../../shared/data/infrastructure/api-error-result';
import type { ApiResult } from '../../../shared/data/types/api-result';
import {
  OwnerWalletBalanceSchema,
  OwnerWalletTopupConfirmSchema,
  OwnerWalletTopupQrRequestSchema,
  OwnerWalletTopupQrSchema,
  OwnerWalletTransactionsResponseSchema,
  type OwnerWalletBalanceData,
  type OwnerWalletTopupConfirmData,
  type OwnerWalletTopupQrData,
  type OwnerWalletTransactionData,
} from '../schemas/wallet.schema';

@Injectable({ providedIn: 'root' })
export class WalletApiService {
  private readonly authTokenService = inject(AuthTokenService);
  private readonly baseUrl = environment.apiUrl;

  async getMyWalletBalance(): Promise<ApiResult<OwnerWalletBalanceData>> {
    try {
      const res = await fetch(`${this.baseUrl}${API_ENDPOINTS.WALLET.MY_BALANCE}`, {
        headers: this.getHeaders(),
      });

      if (!res.ok) {
        return serverErrorResult(res, 'Error al obtener el saldo del taller.');
      }

      const responseData = await res.json();
      const parsedResult = OwnerWalletBalanceSchema.safeParse(responseData);
      if (!parsedResult.success) {
        return errorResult('Error en la respuesta del servidor');
      }

      return {
        ok: true,
        data: parsedResult.data,
      };
    } catch {
      return errorResult('Error de conexion. Intenta mas tarde.');
    }
  }

  async listMyWalletTransactions(): Promise<ApiResult<OwnerWalletTransactionData[]>> {
    try {
      const res = await fetch(`${this.baseUrl}${API_ENDPOINTS.WALLET.MY_TRANSACTIONS}`, {
        headers: this.getHeaders(),
      });

      if (!res.ok) {
        return serverErrorResult(res, 'Error al obtener las transacciones.');
      }

      const responseData = await res.json();
      const parsedResult = OwnerWalletTransactionsResponseSchema.safeParse(responseData);
      if (!parsedResult.success) {
        return errorResult('Error en la respuesta del servidor');
      }

      return {
        ok: true,
        data: parsedResult.data.transactions,
      };
    } catch {
      return errorResult('Error de conexion. Intenta mas tarde.');
    }
  }

  async createMyTopupQr(amount: number): Promise<ApiResult<OwnerWalletTopupQrData>> {
    const parsedData = OwnerWalletTopupQrRequestSchema.safeParse({ amount });
    if (!parsedData.success) {
      return errorResult('Monto invalido para generar el QR.');
    }

    try {
      const res = await fetch(`${this.baseUrl}${API_ENDPOINTS.WALLET.TOPUP_QR}`, {
        method: 'POST',
        headers: this.getHeaders(true),
        body: JSON.stringify(parsedData.data),
      });

      if (!res.ok) {
        return serverErrorResult(res, 'Error al generar el QR de recarga.');
      }

      const responseData = await res.json();
      const parsedResult = OwnerWalletTopupQrSchema.safeParse(responseData);
      if (!parsedResult.success) {
        return errorResult('Error en la respuesta del servidor');
      }

      return {
        ok: true,
        data: parsedResult.data,
      };
    } catch {
      return errorResult('Error de conexion. Intenta mas tarde.');
    }
  }

  async confirmMyTopup(transactionId: string): Promise<ApiResult<OwnerWalletTopupConfirmData>> {
    try {
      const res = await fetch(
        `${this.baseUrl}${API_ENDPOINTS.WALLET.TOPUP_CONFIRM_BASE}/${transactionId}/confirm`,
        {
          method: 'POST',
          headers: this.getHeaders(),
        },
      );

      if (!res.ok) {
        return serverErrorResult(res, 'Error al confirmar la recarga.');
      }

      const responseData = await res.json();
      const parsedResult = OwnerWalletTopupConfirmSchema.safeParse(responseData);
      if (!parsedResult.success) {
        return errorResult('Error en la respuesta del servidor');
      }

      return {
        ok: true,
        data: parsedResult.data,
      };
    } catch {
      return errorResult('Error de conexion. Intenta mas tarde.');
    }
  }

  private getHeaders(withJsonContentType = false): HeadersInit {
    const token = this.authTokenService.getToken();

    return {
      ...(withJsonContentType && { 'Content-Type': 'application/json' }),
      ...(token && { Authorization: `Bearer ${token}` }),
    };
  }
}
