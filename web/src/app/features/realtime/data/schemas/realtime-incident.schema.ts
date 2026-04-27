import { z } from 'zod';

export const IncidentSnapshotStateSchema = z.object({
  status: z.string().nullable().optional(),
  assignment_id: z.string().uuid().nullable().optional(),
  repair_shop_id: z.string().uuid().nullable().optional(),
  mechanic_id: z.string().uuid().nullable().optional(),
  mechanic_latitude: z.number().nullable().optional(),
  mechanic_longitude: z.number().nullable().optional(),
  mechanic_location_updated_at: z.string().nullable().optional(),
  last_event_at: z.string().nullable().optional(),
});

export const IncidentRealtimeEventSchema = z.object({
  id: z.string().uuid(),
  type: z.string(),
  payload: z.record(z.string(), z.unknown()),
  created_at: z.string(),
});

export const IncidentSnapshotResponseSchema = z.object({
  incident_id: z.string().uuid(),
  snapshot: IncidentSnapshotStateSchema,
  events: z.array(IncidentRealtimeEventSchema),
});

export const IncidentSocketSnapshotEventSchema = z.object({
  type: z.literal('incident.snapshot'),
  payload: IncidentSnapshotResponseSchema,
});

export const IncidentSocketRealtimeEventSchema = z.object({
  type: z.string(),
  payload: z.record(z.string(), z.unknown()),
  meta: z
    .object({
      incident_id: z.string().uuid(),
      event_id: z.string().uuid(),
      created_at: z.string(),
    })
    .optional(),
});

export type IncidentSnapshotResponseData = z.infer<typeof IncidentSnapshotResponseSchema>;
export type IncidentSocketRealtimeEventData = z.infer<typeof IncidentSocketRealtimeEventSchema>;
