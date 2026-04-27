import { z } from 'zod';

import type { ApiResult, ApiStatusResult } from '../../../shared/data/types/api-result';
import { AuthUserSchema } from '../../domain/entities/auth-user';

export { AuthUserSchema };

export const LoginFormSchema = z.object({
  email: z.string().min(1, 'El correo es obligatorio').email('Correo electronico invalido'),
  password: z.string().min(1, 'La contrasena es requerida'),
});

export const RegisterFormSchema = z.object({
  first_name: z.string().min(1, 'El nombre es obligatorio'),
  last_name: z.string().min(1, 'El apellido es obligatorio'),
  phone: z.string().min(1, 'El numero de telefono es obligatorio'),
  email: z.string().min(1, 'El correo es obligatorio').email('Correo electronico invalido'),
  password: z.string().min(1, 'La contrasena es requerida'),
});

export const LoginResponseSchema = z.object({
  user: AuthUserSchema,
  access_token: z.string(),
});

export const RequestPasswordResetOtpFormSchema = z.object({
  email: z.string().min(1, 'El correo es obligatorio').email('Correo electronico invalido'),
});

export const VerifyPasswordResetOtpFormSchema = z.object({
  email: z.string().min(1, 'El correo es obligatorio').email('Correo electronico invalido'),
  otp: z
    .string()
    .trim()
    .length(6, 'El codigo OTP debe tener 6 digitos')
    .regex(/^\d+$/, 'El codigo OTP solo debe contener numeros'),
});

export type LoginFormData = z.infer<typeof LoginFormSchema>;
export type RegisterFormData = z.infer<typeof RegisterFormSchema>;
export type LoginResponseData = z.infer<typeof LoginResponseSchema>;
export type RequestPasswordResetOtpFormData = z.infer<typeof RequestPasswordResetOtpFormSchema>;
export type VerifyPasswordResetOtpFormData = z.infer<typeof VerifyPasswordResetOtpFormSchema>;

export type AuthSession = {
  accessToken: string;
  user: LoginResponseData['user'];
};

export type AuthResult = ApiResult<AuthSession>;
export type AuthActionResult = ApiResult<LoginResponseData['user']>;
export type AuthLogoutResult = ApiStatusResult;
export type RequestPasswordResetOtpResult = ApiStatusResult;
export type VerifyPasswordResetOtpResult = ApiStatusResult;
