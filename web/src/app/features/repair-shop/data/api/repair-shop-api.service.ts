import { Injectable, inject } from '@angular/core';

import { environment } from '../../../../../environments/environment';
import { API_ENDPOINTS } from '../../../../core/config/api-endpoints';
import { AuthTokenService } from '../../../../core/services/auth-token.service';
import {
  errorResult,
  serverErrorResult,
  zodValidationErrorResult,
} from '../../../shared/data/infrastructure/api-error-result';
import type { ApiResult, ApiStatusResult } from '../../../shared/data/types/api-result';
import {
  AssignShopServicesFormSchema,
  RepairShopFormSchema,
  RepairShopResponseSchema,
  RepairShopSchema,
  type RepairShopData,
  type RepairShopResponseData,
  ShopMechanicsListResponseSchema,
  type ServiceData,
  type ShopMechanicData,
  ServicesListResponseSchema,
  UpdateShopLocationFormSchema,
  UpdateShopProfileFormSchema,
} from '../schemas/repair-shop.schema';

@Injectable({ providedIn: 'root' })
export class RepairShopApiService {
  private readonly authTokenService = inject(AuthTokenService);
  private readonly baseUrl = environment.apiUrl;

  async createRepairShop(data: unknown): Promise<ApiResult<RepairShopResponseData>> {
    const parsedData = RepairShopFormSchema.safeParse(data);
    if (!parsedData.success) {
      return zodValidationErrorResult(parsedData.error);
    }

    try {
      const res = await fetch(`${this.baseUrl}${API_ENDPOINTS.REPAIR_SHOP.CREATE}`, {
        method: 'POST',
        headers: this.getHeaders(true),
        body: JSON.stringify(parsedData.data),
      });

      if (!res.ok) {
        return serverErrorResult(res, 'Error al registrar el taller.');
      }

      const responseData = await res.json();
      const parsedResult = RepairShopResponseSchema.safeParse(responseData);
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

  async getMyShop(): Promise<ApiResult<RepairShopData>> {
    try {
      const res = await fetch(`${this.baseUrl}${API_ENDPOINTS.REPAIR_SHOP.ME}`, {
        headers: this.getHeaders(),
      });

      if (!res.ok) {
        return serverErrorResult(res, 'Error al obtener el taller.');
      }

      const responseData = await res.json();
      const parsedResult = RepairShopSchema.safeParse(responseData);
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

  async listServices(): Promise<ApiResult<ServiceData[]>> {
    try {
      const res = await fetch(`${this.baseUrl}${API_ENDPOINTS.REPAIR_SHOP.SERVICES}`, {
        headers: this.getHeaders(),
      });

      if (!res.ok) {
        return serverErrorResult(res, 'Error al listar servicios.');
      }

      const responseData = await res.json();
      const parsedResult = ServicesListResponseSchema.safeParse(responseData);
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

  async getMyShopServices(): Promise<ApiResult<ServiceData[]>> {
    try {
      const res = await fetch(`${this.baseUrl}${API_ENDPOINTS.REPAIR_SHOP.MY_SERVICES}`, {
        headers: this.getHeaders(),
      });

      if (!res.ok) {
        return serverErrorResult(res, 'Error al obtener los servicios del taller.');
      }

      const responseData = await res.json();
      const parsedResult = ServicesListResponseSchema.safeParse(responseData);
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

  async listMyShopMechanics(isAvailable = false): Promise<ApiResult<ShopMechanicData[]>> {
    const url = new URL(`${this.baseUrl}${API_ENDPOINTS.REPAIR_SHOP.MY_MECHANICS}`);
    if (isAvailable) {
      url.searchParams.set('is_available', 'true');
    }

    try {
      const res = await fetch(url.toString(), {
        headers: this.getHeaders(),
      });

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

  async deleteMyShopMechanic(mechanicId: string): Promise<ApiStatusResult> {
    try {
      const res = await fetch(
        `${this.baseUrl}${API_ENDPOINTS.REPAIR_SHOP.DELETE_MY_MECHANIC}/${mechanicId}`,
        {
          method: 'DELETE',
          headers: this.getHeaders(),
        },
      );

      if (!res.ok) {
        return serverErrorResult(res, 'Error al eliminar el mecanico.');
      }

      return { ok: true };
    } catch {
      return errorResult('Error de conexion. Intenta mas tarde.');
    }
  }

  async assignMyShopServices(data: unknown): Promise<ApiResult<RepairShopData>> {
    const parsedData = AssignShopServicesFormSchema.safeParse(data);
    if (!parsedData.success) {
      return zodValidationErrorResult(parsedData.error);
    }

    try {
      const res = await fetch(`${this.baseUrl}${API_ENDPOINTS.REPAIR_SHOP.ASSIGN_MY_SERVICES}`, {
        method: 'PUT',
        headers: this.getHeaders(true),
        body: JSON.stringify(parsedData.data),
      });

      if (!res.ok) {
        return serverErrorResult(res, 'Error al guardar los servicios del taller.');
      }

      const responseData = await res.json();
      const parsedResult = RepairShopSchema.safeParse(responseData);
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

  async updateMyShopProfile(data: unknown): Promise<ApiResult<RepairShopData>> {
    const parsedData = UpdateShopProfileFormSchema.safeParse(data);
    if (!parsedData.success) {
      return zodValidationErrorResult(parsedData.error);
    }

    try {
      const res = await fetch(`${this.baseUrl}${API_ENDPOINTS.REPAIR_SHOP.UPDATE_MY_PROFILE}`, {
        method: 'PATCH',
        headers: this.getHeaders(true),
        body: JSON.stringify(parsedData.data),
      });

      if (!res.ok) {
        return serverErrorResult(res, 'Error al actualizar el taller.');
      }

      const responseData = await res.json();
      const parsedResult = RepairShopSchema.safeParse(responseData);
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

  async updateMyShopLocation(data: unknown): Promise<ApiResult<RepairShopData>> {
    const parsedData = UpdateShopLocationFormSchema.safeParse(data);
    if (!parsedData.success) {
      return zodValidationErrorResult(parsedData.error);
    }

    try {
      const res = await fetch(`${this.baseUrl}${API_ENDPOINTS.REPAIR_SHOP.UPDATE_MY_LOCATION}`, {
        method: 'PATCH',
        headers: this.getHeaders(true),
        body: JSON.stringify(parsedData.data),
      });

      if (!res.ok) {
        return serverErrorResult(res, 'Error al actualizar la ubicacion del taller.');
      }

      const responseData = await res.json();
      const parsedResult = RepairShopSchema.safeParse(responseData);
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
