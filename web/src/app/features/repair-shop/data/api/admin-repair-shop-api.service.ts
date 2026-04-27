import { Injectable, inject } from '@angular/core';

import { environment } from '../../../../../environments/environment';
import { API_ENDPOINTS } from '../../../../core/config/api-endpoints';
import { AuthTokenService } from '../../../../core/services/auth-token.service';
import {
  errorResult,
  serverErrorResult,
} from '../../../shared/data/infrastructure/api-error-result';
import type { ApiResult, ApiStatusResult } from '../../../shared/data/types/api-result';
import {
  AdminRecentServicesResponseSchema,
  AdminRepairShopOverviewSchema,
  AdminRepairShopsResponseSchema,
  type AdminRecentServiceData,
  type AdminRepairShopData,
  type AdminRepairShopOverviewData,
  ShopMechanicsListResponseSchema,
  type ShopMechanicData,
} from '../schemas/repair-shop.schema';

@Injectable({ providedIn: 'root' })
export class AdminRepairShopApiService {
  private readonly authTokenService = inject(AuthTokenService);
  private readonly baseUrl = environment.apiUrl;

  async listAllShops(): Promise<ApiResult<AdminRepairShopData[]>> {
    try {
      const res = await fetch(`${this.baseUrl}${API_ENDPOINTS.REPAIR_SHOP.ADMIN_SHOPS}`, {
        headers: this.getHeaders(),
      });

      if (!res.ok) {
        return serverErrorResult(res, 'Error al obtener talleres.');
      }

      const responseData = await res.json();
      const parsedResult = AdminRepairShopsResponseSchema.safeParse(responseData);
      if (!parsedResult.success) {
        return errorResult('Error en la respuesta del servidor');
      }

      return {
        ok: true,
        data: parsedResult.data.shops,
      };
    } catch {
      return errorResult('Error de conexion. Intenta mas tarde.');
    }
  }

  async getShopOverview(shopId: string): Promise<ApiResult<AdminRepairShopOverviewData>> {
    try {
      const res = await fetch(
        `${this.baseUrl}${API_ENDPOINTS.REPAIR_SHOP.ADMIN_SHOP_OVERVIEW_BASE}/${shopId}/overview`,
        {
          headers: this.getHeaders(),
        },
      );

      if (!res.ok) {
        return serverErrorResult(res, 'Error al obtener el detalle del taller.');
      }

      const responseData = await res.json();
      const parsedResult = AdminRepairShopOverviewSchema.safeParse(responseData);
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

  async listShopMechanics(shopId: string): Promise<ApiResult<ShopMechanicData[]>> {
    try {
      const res = await fetch(
        `${this.baseUrl}${API_ENDPOINTS.REPAIR_SHOP.ADMIN_SHOP_MECHANICS_BASE}/${shopId}/mechanics`,
        {
          headers: this.getHeaders(),
        },
      );

      if (!res.ok) {
        return serverErrorResult(res, 'Error al obtener mecanicos del taller.');
      }

      const responseData = await res.json();
      const parsedResult = ShopMechanicsListResponseSchema.safeParse(responseData);
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

  async deleteShopMechanic(shopId: string, mechanicId: string): Promise<ApiStatusResult> {
    try {
      const res = await fetch(
        `${this.baseUrl}${API_ENDPOINTS.REPAIR_SHOP.ADMIN_SHOP_MECHANICS_BASE}/${shopId}/mechanics/${mechanicId}`,
        {
          method: 'DELETE',
          headers: this.getHeaders(),
        },
      );

      if (!res.ok) {
        return serverErrorResult(res, 'Error al desvincular mecanico del taller.');
      }

      return { ok: true };
    } catch {
      return errorResult('Error de conexion. Intenta mas tarde.');
    }
  }

  async listRecentServices(shopId: string): Promise<ApiResult<AdminRecentServiceData[]>> {
    try {
      const res = await fetch(
        `${this.baseUrl}${API_ENDPOINTS.REPAIR_SHOP.ADMIN_SHOP_RECENT_SERVICES_BASE}/${shopId}/recent-services`,
        {
          headers: this.getHeaders(),
        },
      );

      if (!res.ok) {
        return serverErrorResult(res, 'Error al obtener ultimos servicios del taller.');
      }

      const responseData = await res.json();
      const parsedResult = AdminRecentServicesResponseSchema.safeParse(responseData);
      if (!parsedResult.success) {
        return errorResult('Error en la respuesta del servidor');
      }

      return {
        ok: true,
        data: parsedResult.data.services,
      };
    } catch {
      return errorResult('Error de conexion. Intenta mas tarde.');
    }
  }

  private getHeaders(): HeadersInit {
    const token = this.authTokenService.getToken();

    return {
      ...(token && { Authorization: `Bearer ${token}` }),
    };
  }
}
