import { z } from 'zod';

import { AuthUserSchema } from '../../../auth/domain/entities/auth-user';

export const RepairShopFormSchema = z.object({
  name: z
    .string()
    .trim()
    .min(5, 'El nombre del taller debe tener al menos 5 caracteres')
    .max(70, 'El nombre del taller debe tener maximo 70 caracteres'),
  latitude: z.number().min(-90, 'Latitud invalida').max(90, 'Latitud invalida'),
  longitude: z.number().min(-180, 'Longitud invalida').max(180, 'Longitud invalida'),
});

export const RepairShopSchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
  text_address: z.string(),
  latitude: z.number(),
  longitude: z.number(),
});

export const ServiceSchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
});

export const ServicesListResponseSchema = z.array(ServiceSchema);

export const AssignShopServicesFormSchema = z.object({
  service_ids: z
    .array(z.string().uuid('Servicio invalido'))
    .min(1, 'Selecciona al menos un servicio'),
});

export const UpdateShopProfileFormSchema = z.object({
  name: z
    .string()
    .trim()
    .min(5, 'El nombre del taller debe tener al menos 5 caracteres')
    .max(70, 'El nombre del taller debe tener maximo 70 caracteres'),
  text_address: z
    .string()
    .trim()
    .min(5, 'La direccion debe tener al menos 5 caracteres')
    .max(240, 'La direccion debe tener maximo 240 caracteres'),
});

export const UpdateShopLocationFormSchema = z.object({
  latitude: z.number().min(-90, 'Latitud invalida').max(90, 'Latitud invalida'),
  longitude: z.number().min(-180, 'Longitud invalida').max(180, 'Longitud invalida'),
});

export const ShopInvitationCreateFormSchema = z.object({
  expires_at: z.string().min(1, 'Fecha de expiracion invalida'),
});

export const ShopInvitationSchema = z.object({
  code: z.string(),
  expires_at: z.string(),
  expires_at_label: z.string(),
  status: z.enum(['active', 'expired']),
});

export const RepairShopResponseSchema = z.object({
  user: AuthUserSchema,
  shop: RepairShopSchema,
});

export const ShopMechanicSchema = z.object({
  id: z.string().uuid(),
  shop_id: z.string().uuid(),
  user_id: z.string().uuid(),
  is_available: z.boolean(),
  created_date: z.string(),
  user: AuthUserSchema,
});

export const ShopMechanicsListResponseSchema = z.array(ShopMechanicSchema);

export const AdminRepairShopSchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
  text_address: z.string(),
  latitude: z.number(),
  longitude: z.number(),
  is_available: z.boolean(),
  state: z.boolean(),
  owner_id: z.string().uuid(),
  owner_name: z.string(),
  owner_email: z.string().email(),
  created_date: z.string(),
  deleted_date: z.string().nullable().optional(),
});

export const AdminRepairShopsResponseSchema = z.object({
  shops: z.array(AdminRepairShopSchema),
});

export const AdminShopMechanicStatsSchema = z.object({
  total: z.number(),
  available: z.number(),
  unavailable: z.number(),
  active_records: z.number(),
  inactive_records: z.number(),
});

export const AdminRepairShopOverviewSchema = z.object({
  shop: AdminRepairShopSchema,
  mechanic_stats: AdminShopMechanicStatsSchema,
  recent_activity: z.array(z.string()),
});

export const AdminRecentServiceSchema = z.object({
  assignment_id: z.string().uuid(),
  incident_id: z.string().uuid(),
  incident_description: z.string().nullable().optional(),
  incident_address: z.string().nullable().optional(),
  incident_status: z.string(),
  problem_name: z.string().nullable().optional(),
  mechanic_name: z.string().nullable().optional(),
  accepted_at: z.string().nullable().optional(),
  created_date: z.string(),
});

export const AdminRecentServicesResponseSchema = z.object({
  services: z.array(AdminRecentServiceSchema),
});

export type RepairShopFormData = z.infer<typeof RepairShopFormSchema>;
export type RepairShopData = z.infer<typeof RepairShopSchema>;
export type ServiceData = z.infer<typeof ServiceSchema>;
export type ShopInvitationData = z.infer<typeof ShopInvitationSchema>;
export type RepairShopResponseData = z.infer<typeof RepairShopResponseSchema>;
export type ShopMechanicData = z.infer<typeof ShopMechanicSchema>;
export type AdminRepairShopData = z.infer<typeof AdminRepairShopSchema>;
export type AdminShopMechanicStatsData = z.infer<typeof AdminShopMechanicStatsSchema>;
export type AdminRepairShopOverviewData = z.infer<typeof AdminRepairShopOverviewSchema>;
export type AdminRecentServiceData = z.infer<typeof AdminRecentServiceSchema>;
