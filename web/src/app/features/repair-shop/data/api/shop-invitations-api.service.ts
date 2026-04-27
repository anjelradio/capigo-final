import { Injectable, inject } from '@angular/core';

import { environment } from '../../../../../environments/environment';
import { API_ENDPOINTS } from '../../../../core/config/api-endpoints';
import { AuthTokenService } from '../../../../core/services/auth-token.service';
import {
  errorResult,
  serverErrorResult,
  zodValidationErrorResult,
} from '../../../shared/data/infrastructure/api-error-result';
import type { ApiMaybeResult, ApiStatusResult } from '../../../shared/data/types/api-result';
import {
  ShopInvitationCreateFormSchema,
  ShopInvitationSchema,
  type ShopInvitationData,
} from '../schemas/repair-shop.schema';

@Injectable({ providedIn: 'root' })
export class ShopInvitationsApiService {
  private readonly authTokenService = inject(AuthTokenService);
  private readonly baseUrl = environment.apiUrl;

  async createMyShopInvitation(data: unknown): Promise<ApiStatusResult> {
    const parsedData = ShopInvitationCreateFormSchema.safeParse(data);
    if (!parsedData.success) {
      return zodValidationErrorResult(parsedData.error);
    }

    try {
      const res = await fetch(`${this.baseUrl}${API_ENDPOINTS.REPAIR_SHOP.CREATE_MY_INVITATION}`, {
        method: 'POST',
        headers: this.getHeaders(true),
        body: JSON.stringify(parsedData.data),
      });

      if (!res.ok) {
        return serverErrorResult(res, 'Error al crear invitacion.');
      }

      return { ok: true };
    } catch {
      return errorResult('Error de conexion. Intenta mas tarde.');
    }
  }

  async getMyShopInvitation(): Promise<ApiMaybeResult<ShopInvitationData>> {
    try {
      const res = await fetch(`${this.baseUrl}${API_ENDPOINTS.REPAIR_SHOP.MY_INVITATION}`, {
        headers: this.getHeaders(),
      });

      if (res.status === 404 || res.status === 204) {
        return {
          ok: true,
          data: null,
        };
      }

      if (!res.ok) {
        return serverErrorResult(res, 'Error al obtener invitacion del taller.');
      }

      const responseData = await res.json();
      if (responseData === null) {
        return {
          ok: true,
          data: null,
        };
      }

      const parsedResult = ShopInvitationSchema.safeParse(responseData);
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

  async deleteMyShopInvitation(): Promise<ApiStatusResult> {
    try {
      const res = await fetch(`${this.baseUrl}${API_ENDPOINTS.REPAIR_SHOP.DELETE_MY_INVITATION}`, {
        method: 'DELETE',
        headers: this.getHeaders(),
      });

      if (!res.ok) {
        return serverErrorResult(res, 'Error al eliminar invitacion del taller.');
      }

      return { ok: true };
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
