import { Injectable, inject } from '@angular/core';

import { environment } from '../../../../../environments/environment';
import { API_ENDPOINTS } from '../../../../core/config/api-endpoints';
import { AuthTokenService } from '../../../../core/services/auth-token.service';
import {
  errorResult,
  serverErrorResult,
  zodValidationErrorResult,
} from '../../../shared/data/infrastructure/api-error-result';
import {
  type RequestEmailChangeOtpResult,
  type UpdateEmailResult,
  UpdateEmailFormSchema,
  UpdateEmailResponseSchema,
  type UpdatePasswordResult,
  UpdatePasswordFormSchema,
  type UpdateUserProfileResult,
  type VerifyEmailChangeOtpResult,
  VerifyEmailChangeOtpFormSchema,
  VerifyEmailChangeOtpResponseSchema,
  UserProfileUpdateFormSchema,
  UserProfileUpdateResponseSchema,
} from '../schemas/user.schema';

@Injectable({ providedIn: 'root' })
export class UserApiService {
  private readonly authTokenService = inject(AuthTokenService);
  private readonly baseUrl = environment.apiUrl;

  async updateProfile(data: unknown): Promise<UpdateUserProfileResult> {
    const parsedData = UserProfileUpdateFormSchema.safeParse(data);
    if (!parsedData.success) {
      return zodValidationErrorResult(parsedData.error);
    }

    try {
      const res = await fetch(`${this.baseUrl}${API_ENDPOINTS.USER.UPDATE_PROFILE}`, {
        method: 'PATCH',
        headers: this.getHeaders(true),
        body: JSON.stringify(parsedData.data),
      });

      if (!res.ok) {
        return serverErrorResult(res, 'Error al actualizar el perfil.');
      }

      const responseData = await res.json();
      const parsedResult = UserProfileUpdateResponseSchema.safeParse(responseData);
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

  async updatePassword(data: unknown): Promise<UpdatePasswordResult> {
    const parsedData = UpdatePasswordFormSchema.safeParse(data);
    if (!parsedData.success) {
      return zodValidationErrorResult(parsedData.error);
    }

    try {
      const res = await fetch(`${this.baseUrl}${API_ENDPOINTS.USER.UPDATE_PASSWORD}`, {
        method: 'PATCH',
        headers: this.getHeaders(true),
        body: JSON.stringify(parsedData.data),
      });

      if (!res.ok) {
        return serverErrorResult(res, 'Error al actualizar la contrasena.');
      }

      return { ok: true };
    } catch {
      return errorResult('Error de conexion. Intenta mas tarde.');
    }
  }

  async requestEmailChangeOtp(): Promise<RequestEmailChangeOtpResult> {
    try {
      const res = await fetch(`${this.baseUrl}${API_ENDPOINTS.USER.EMAIL_CHANGE_REQUEST_OTP}`, {
        method: 'POST',
        headers: this.getHeaders(true),
        body: JSON.stringify({}),
      });

      if (!res.ok) {
        return serverErrorResult(res, 'Error al solicitar el codigo OTP.');
      }

      return { ok: true };
    } catch {
      return errorResult('Error de conexion. Intenta mas tarde.');
    }
  }

  async verifyEmailChangeOtp(data: unknown): Promise<VerifyEmailChangeOtpResult> {
    const parsedData = VerifyEmailChangeOtpFormSchema.safeParse(data);
    if (!parsedData.success) {
      return zodValidationErrorResult(parsedData.error);
    }

    try {
      const res = await fetch(`${this.baseUrl}${API_ENDPOINTS.USER.EMAIL_CHANGE_VERIFY_OTP}`, {
        method: 'POST',
        headers: this.getHeaders(true),
        body: JSON.stringify(parsedData.data),
      });

      if (!res.ok) {
        return serverErrorResult(res, 'Error al verificar codigo OTP.');
      }

      const responseData = await res.json();
      const parsedResult = VerifyEmailChangeOtpResponseSchema.safeParse(responseData);
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

  async updateEmail(data: unknown): Promise<UpdateEmailResult> {
    const parsedData = UpdateEmailFormSchema.safeParse(data);
    if (!parsedData.success) {
      return zodValidationErrorResult(parsedData.error);
    }

    try {
      const res = await fetch(`${this.baseUrl}${API_ENDPOINTS.USER.UPDATE_EMAIL}`, {
        method: 'PATCH',
        headers: this.getHeaders(true),
        body: JSON.stringify(parsedData.data),
      });

      if (!res.ok) {
        return serverErrorResult(res, 'Error al actualizar el correo.');
      }

      const responseData = await res.json();
      const parsedResult = UpdateEmailResponseSchema.safeParse(responseData);
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
