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
  OwnerAssignmentsResponseSchema,
  OwnerOfferActionResponseSchema,
  OwnerOfferHistoryResponseSchema,
  OwnerOfferDetailSchema,
  OwnerPendingOffersResponseSchema,
  type OwnerAssignmentData,
  type OwnerOfferActionResponseData,
  type OwnerHistoryOfferData,
  type OwnerOfferDetailData,
  type OwnerPendingOfferData,
} from '../schemas/realtime-offer.schema';

@Injectable({ providedIn: 'root' })
export class RealtimeOffersApiService {
  private readonly authTokenService = inject(AuthTokenService);
  private readonly baseUrl = environment.apiUrl;

  async listMyPendingOffers(): Promise<ApiResult<OwnerPendingOfferData[]>> {
    try {
      const res = await fetch(`${this.baseUrl}${API_ENDPOINTS.ASSIGNMENTS.OWNER_PENDING_OFFERS}`, {
        headers: this.getHeaders(),
      });

      if (!res.ok) {
        return serverErrorResult(res, 'Error al obtener ofertas pendientes.');
      }

      const responseData = await res.json();
      const parsedResult = OwnerPendingOffersResponseSchema.safeParse(responseData);
      if (!parsedResult.success) {
        return errorResult('Error en la respuesta del servidor');
      }

      return {
        ok: true,
        data: parsedResult.data.offers,
      };
    } catch {
      return errorResult('Error de conexion. Intenta mas tarde.');
    }
  }

  async getOfferDetail(assignmentId: string): Promise<ApiResult<OwnerOfferDetailData>> {
    try {
      const res = await fetch(
        `${this.baseUrl}${API_ENDPOINTS.ASSIGNMENTS.OWNER_OFFER_DETAIL}/${assignmentId}/offer-detail`,
        {
          headers: this.getHeaders(),
        },
      );

      if (!res.ok) {
        return serverErrorResult(res, 'Error al obtener el detalle de la oferta.');
      }

      const responseData = await res.json();
      const parsedResult = OwnerOfferDetailSchema.safeParse(responseData);
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

  async listMyOfferHistory(): Promise<ApiResult<OwnerHistoryOfferData[]>> {
    try {
      const res = await fetch(`${this.baseUrl}${API_ENDPOINTS.ASSIGNMENTS.OWNER_OFFER_HISTORY}`, {
        headers: this.getHeaders(),
      });

      if (!res.ok) {
        return serverErrorResult(res, 'Error al obtener el historial de solicitudes.');
      }

      const responseData = await res.json();
      const parsedResult = OwnerOfferHistoryResponseSchema.safeParse(responseData);
      if (!parsedResult.success) {
        return errorResult('Error en la respuesta del servidor');
      }

      return {
        ok: true,
        data: parsedResult.data.offers,
      };
    } catch {
      return errorResult('Error de conexion. Intenta mas tarde.');
    }
  }

  async listMyAssignments(): Promise<ApiResult<OwnerAssignmentData[]>> {
    try {
      const res = await fetch(`${this.baseUrl}${API_ENDPOINTS.ASSIGNMENTS.OWNER_ASSIGNMENTS}`, {
        headers: this.getHeaders(),
      });

      if (!res.ok) {
        return serverErrorResult(res, 'Error al obtener las asignaciones del taller.');
      }

      const responseData = await res.json();
      const parsedResult = OwnerAssignmentsResponseSchema.safeParse(responseData);
      if (!parsedResult.success) {
        return errorResult('Error en la respuesta del servidor');
      }

      return {
        ok: true,
        data: parsedResult.data.assignments,
      };
    } catch {
      return errorResult('Error de conexion. Intenta mas tarde.');
    }
  }

  async downloadServiceReportPdf(assignmentId: string): Promise<ApiResult<Blob>> {
    try {
      const res = await fetch(
        `${this.baseUrl}${API_ENDPOINTS.ASSIGNMENTS.OWNER_OFFER_DETAIL}/${assignmentId}/${API_ENDPOINTS.ASSIGNMENTS.OWNER_SERVICE_REPORT_PDF_SUFFIX}`,
        {
          headers: this.getHeaders(),
        },
      );

      if (!res.ok) {
        return serverErrorResult(res, 'Error al descargar el reporte del servicio.');
      }

      const blob = await res.blob();
      return {
        ok: true,
        data: blob,
      };
    } catch {
      return errorResult('Error de conexion. Intenta mas tarde.');
    }
  }

  async submitOffer(
    assignmentId: string,
    mechanicId: string,
    quotedPrice: number,
  ): Promise<ApiResult<OwnerOfferActionResponseData>> {
    return this.postOfferAction(
      assignmentId,
      API_ENDPOINTS.ASSIGNMENTS.OWNER_SUBMIT_OFFER_SUFFIX,
      {
        mechanic_id: mechanicId,
        quoted_price: quotedPrice,
      },
    );
  }

  async rejectOffer(assignmentId: string): Promise<ApiResult<OwnerOfferActionResponseData>> {
    return this.postOfferAction(assignmentId, API_ENDPOINTS.ASSIGNMENTS.OWNER_REJECT_SUFFIX);
  }

  private async postOfferAction(
    assignmentId: string,
    actionSuffix: string,
    body?: unknown,
  ): Promise<ApiResult<OwnerOfferActionResponseData>> {
    try {
      const res = await fetch(
        `${this.baseUrl}${API_ENDPOINTS.ASSIGNMENTS.OWNER_OFFER_DETAIL}/${assignmentId}/${actionSuffix}`,
        {
          method: 'POST',
          headers: this.getHeaders(Boolean(body)),
          ...(body ? { body: JSON.stringify(body) } : {}),
        },
      );

      if (!res.ok) {
        return serverErrorResult(res, 'Error al procesar la solicitud.');
      }

      const responseData = await res.json();
      const parsedResult = OwnerOfferActionResponseSchema.safeParse(responseData);
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
