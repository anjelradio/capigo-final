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
  IncidentSnapshotResponseSchema,
  type IncidentSnapshotResponseData,
} from '../schemas/realtime-incident.schema';

@Injectable({ providedIn: 'root' })
export class RealtimeIncidentApiService {
  private readonly authTokenService = inject(AuthTokenService);
  private readonly baseUrl = environment.apiUrl;

  async getIncidentSnapshot(incidentId: string): Promise<ApiResult<IncidentSnapshotResponseData>> {
    try {
      const res = await fetch(
        `${this.baseUrl}${API_ENDPOINTS.REALTIME.INCIDENT_SNAPSHOT_BASE}/${incidentId}/snapshot`,
        {
          headers: this.getHeaders(),
        },
      );

      if (!res.ok) {
        return serverErrorResult(res, 'Error al obtener el estado en tiempo real del incidente.');
      }

      const responseData = await res.json();
      const parsed = IncidentSnapshotResponseSchema.safeParse(responseData);
      if (!parsed.success) {
        return errorResult('Error en la respuesta del servidor');
      }

      return {
        ok: true,
        data: parsed.data,
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
