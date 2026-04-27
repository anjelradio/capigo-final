import { z } from 'zod';

import type { ApiResult, ApiStatusResult } from '../../../shared/data/types/api-result';
import { AuthUserSchema } from '../../../auth/domain/entities/auth-user';
import type { UserProfile } from '../../domain/entities/user-profile';

export const UserProfileUpdateFormSchema = z.object({
  first_name: z.string().trim().min(2, 'El nombre debe tener al menos 2 caracteres'),
  last_name: z.string().trim().min(2, 'El apellido debe tener al menos 2 caracteres'),
  phone: z
    .string()
    .trim()
    .min(7, 'El telefono debe tener al menos 7 digitos')
    .max(9, 'El telefono debe tener maximo 9 digitos')
    .regex(/^\d+$/, 'El telefono solo debe contener numeros'),
});

export const UserProfileUpdateResponseSchema = AuthUserSchema;

export const UpdatePasswordFormSchema = z
  .object({
    current_password: z.string().min(1, 'La contraseña actual es requerida'),
    new_password: z.string().min(1, 'La nueva contraseña es requerida'),
    confirm_new_password: z.string().min(1, 'La confirmación de contraseña es requerida'),
  })
  .refine((data) => data.new_password === data.confirm_new_password, {
    message: 'La confirmación de contraseña no coincide',
    path: ['confirm_new_password'],
  });

export const VerifyEmailChangeOtpFormSchema = z.object({
  otp: z
    .string()
    .trim()
    .length(6, 'El codigo OTP debe tener 6 digitos')
    .regex(/^\d+$/, 'El codigo OTP solo debe contener numeros'),
});

export const VerifyEmailChangeOtpResponseSchema = z.object({
  change_email_token: z.string(),
});

export const UpdateEmailFormSchema = z.object({
  new_email: z
    .string()
    .trim()
    .min(1, 'El correo es obligatorio')
    .email('Correo electronico invalido'),
  change_email_token: z.string().trim().min(1, 'El token de cambio de correo es requerido'),
});

export const UpdateEmailResponseSchema = AuthUserSchema;

export type UserProfileUpdateFormData = z.infer<typeof UserProfileUpdateFormSchema>;
export type UserProfileUpdateResponseData = z.infer<typeof UserProfileUpdateResponseSchema>;
export type UpdatePasswordFormData = z.infer<typeof UpdatePasswordFormSchema>;
export type VerifyEmailChangeOtpFormData = z.infer<typeof VerifyEmailChangeOtpFormSchema>;
export type VerifyEmailChangeOtpResponseData = z.infer<typeof VerifyEmailChangeOtpResponseSchema>;
export type UpdateEmailFormData = z.infer<typeof UpdateEmailFormSchema>;
export type UpdateEmailResponseData = z.infer<typeof UpdateEmailResponseSchema>;

export type UserProfileResult = ApiResult<UserProfile>;
export type UpdateUserProfileResult = ApiResult<UserProfileUpdateResponseData>;
export type UpdatePasswordResult = ApiStatusResult;
export type RequestEmailChangeOtpResult = ApiStatusResult;
export type VerifyEmailChangeOtpResult = ApiResult<VerifyEmailChangeOtpResponseData>;
export type UpdateEmailResult = ApiResult<UpdateEmailResponseData>;
