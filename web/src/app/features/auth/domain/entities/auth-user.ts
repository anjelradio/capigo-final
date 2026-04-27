import { z } from 'zod';

export const AuthUserRoleSchema = z.enum(['admin', 'owner', 'mechanic', 'client']);

export const AuthUserSchema = z.object({
  id: z.string().uuid(),
  first_name: z.string(),
  last_name: z.string(),
  email: z.string(),
  phone: z.string(),
  role: AuthUserRoleSchema,
});

export type AuthUser = z.infer<typeof AuthUserSchema>;
export type AuthUserRole = z.infer<typeof AuthUserRoleSchema>;
