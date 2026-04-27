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
  type AuthLogoutResult,
  type AuthResult,
  LoginFormSchema,
  LoginResponseSchema,
  RegisterFormSchema,
  RequestPasswordResetOtpFormSchema,
  type RequestPasswordResetOtpResult,
  VerifyPasswordResetOtpFormSchema,
  type VerifyPasswordResetOtpResult,
} from '../schemas/auth.schema';

@Injectable({ providedIn: 'root' })
export class AuthApiService {
  private readonly authTokenService = inject(AuthTokenService);
  private readonly baseUrl = environment.apiUrl;

  async login(data: unknown): Promise<AuthResult> {
    const parsedData = LoginFormSchema.safeParse(data);
    if (!parsedData.success) {
      return zodValidationErrorResult(parsedData.error);
    }

    try {
      const res = await fetch(`${this.baseUrl}${API_ENDPOINTS.AUTH.LOGIN}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(parsedData.data),
      });

      if (!res.ok) {
        return serverErrorResult(res, 'Error al iniciar sesion.');
      }

      const responseData = await res.json();
      const parsedResult = LoginResponseSchema.safeParse(responseData);
      if (!parsedResult.success) {
        return errorResult('Error en la respuesta del servidor');
      }

      return {
        ok: true,
        data: {
          accessToken: parsedResult.data.access_token,
          user: parsedResult.data.user,
        },
      };
    } catch {
      return errorResult('Error de conexion. Intenta mas tarde.');
    }
  }

  async register(data: unknown): Promise<AuthResult> {
    const parsedData = RegisterFormSchema.safeParse(data);
    if (!parsedData.success) {
      return zodValidationErrorResult(parsedData.error);
    }

    try {
      const res = await fetch(`${this.baseUrl}${API_ENDPOINTS.AUTH.REGISTER}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(parsedData.data),
      });

      if (!res.ok) {
        return serverErrorResult(res, 'Error al registrarse.');
      }

      const responseData = await res.json();
      const parsedResult = LoginResponseSchema.safeParse(responseData);
      if (!parsedResult.success) {
        return errorResult('Error en la respuesta del servidor');
      }

      return {
        ok: true,
        data: {
          accessToken: parsedResult.data.access_token,
          user: parsedResult.data.user,
        },
      };
    } catch {
      return errorResult('Error de conexion. Intenta mas tarde.');
    }
  }

  async logout(): Promise<AuthLogoutResult> {
    const token = this.authTokenService.getToken();

    try {
      const res = await fetch(`${this.baseUrl}${API_ENDPOINTS.AUTH.LOGOUT}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { Authorization: `Bearer ${token}` }),
        },
        body: JSON.stringify({}),
      });

      if (!res.ok) {
        return serverErrorResult(res, 'Error al cerrar sesion.');
      }

      return { ok: true };
    } catch {
      return errorResult('Error de conexion. Intenta mas tarde.');
    }
  }

  async requestPasswordResetOtp(data: unknown): Promise<RequestPasswordResetOtpResult> {
    const parsedData = RequestPasswordResetOtpFormSchema.safeParse(data);
    if (!parsedData.success) {
      return zodValidationErrorResult(parsedData.error);
    }

    try {
      const res = await fetch(`${this.baseUrl}${API_ENDPOINTS.AUTH.PASSWORD.REQUEST_OTP}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(parsedData.data),
      });

      if (!res.ok) {
        return serverErrorResult(res, 'Error al solicitar codigo OTP.');
      }

      return { ok: true };
    } catch {
      return errorResult('Error de conexion. Intenta mas tarde.');
    }
  }

  async verifyPasswordResetOtp(data: unknown): Promise<VerifyPasswordResetOtpResult> {
    const parsedData = VerifyPasswordResetOtpFormSchema.safeParse(data);
    if (!parsedData.success) {
      return zodValidationErrorResult(parsedData.error);
    }

    try {
      const res = await fetch(`${this.baseUrl}${API_ENDPOINTS.AUTH.PASSWORD.VERIFY_OTP}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(parsedData.data),
      });

      if (!res.ok) {
        return serverErrorResult(res, 'Error al verificar codigo OTP.');
      }

      return { ok: true };
    } catch {
      return errorResult('Error de conexion. Intenta mas tarde.');
    }
  }
}
