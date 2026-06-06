import { z } from 'zod';

export const RepairShopDashboardKpisSchema = z.object({
  requests_received: z.number(),
  accepted_services: z.number(),
  completed_services: z.number(),
  cancelled_cases: z.number(),
  acceptance_rate: z.number(),
  cancellation_rate: z.number(),
  revenue_total: z.number(),
  average_resolution_minutes: z.number(),
  average_ticket_value: z.number(),
  top_mechanic_name: z.string().nullable().optional(),
  top_mechanic_completed: z.number(),
});

export const RepairShopDashboardBreakdownSchema = z.object({
  label: z.string(),
  count: z.number(),
  percentage: z.number(),
});

export const RepairShopDashboardZoneSchema = z.object({
  label: z.string(),
  count: z.number(),
  percentage: z.number(),
  latitude: z.number().nullable().optional(),
  longitude: z.number().nullable().optional(),
});

export const RepairShopDashboardSchema = z.object({
  period_days: z.number(),
  generated_at: z.string(),
  kpis: RepairShopDashboardKpisSchema,
  services_by_type: z.array(RepairShopDashboardBreakdownSchema),
  zones_by_services: z.array(RepairShopDashboardZoneSchema),
});

export type RepairShopDashboardKpisData = z.infer<typeof RepairShopDashboardKpisSchema>;
export type RepairShopDashboardBreakdownData = z.infer<typeof RepairShopDashboardBreakdownSchema>;
export type RepairShopDashboardZoneData = z.infer<typeof RepairShopDashboardZoneSchema>;
export type RepairShopDashboardData = z.infer<typeof RepairShopDashboardSchema>;
