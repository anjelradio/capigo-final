import { Injectable, inject } from '@angular/core';

import { environment } from '../../../../../environments/environment';
import { API_ENDPOINTS } from '../../../../core/config/api-endpoints';
import { AuthTokenService } from '../../../../core/services/auth-token.service';
import { errorResult, serverErrorResult } from '../../../shared/data/infrastructure/api-error-result';
import type { ApiResult } from '../../../shared/data/types/api-result';
import {
  RepairShopDashboardSchema,
  type RepairShopDashboardData,
} from '../schemas/repair-shop-dashboard.schema';

@Injectable({ providedIn: 'root' })
export class RepairShopDashboardApiService {
  private readonly authTokenService = inject(AuthTokenService);
  private readonly baseUrl = environment.apiUrl;

  async getMyDashboard(periodDays = 30): Promise<ApiResult<RepairShopDashboardData>> {
    const url = new URL(`${this.baseUrl}${API_ENDPOINTS.REPAIR_SHOP.MY_DASHBOARD}`);
    url.searchParams.set('period_days', String(periodDays));

    try {
      const res = await fetch(url.toString(), {
        headers: this.getHeaders(),
      });

      if (!res.ok) {
        return serverErrorResult(res, 'Error al obtener el dashboard del taller.');
      }

      const responseData = await res.json();
      const parsedResult = RepairShopDashboardSchema.safeParse(responseData);
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

  private getHeaders(): HeadersInit {
    const token = this.authTokenService.getToken();

    return {
      ...(token && { Authorization: `Bearer ${token}` }),
    };
  }
}
