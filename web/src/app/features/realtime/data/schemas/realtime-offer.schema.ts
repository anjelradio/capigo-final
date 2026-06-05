import { z } from 'zod';

export const OwnerPendingOfferSchema = z.object({
  assignment_id: z.string().uuid(),
  incident_id: z.string().uuid(),
  problem_id: z.string().uuid().nullable().optional(),
  problem_name: z.string().nullable().optional(),
  incident_description: z.string().nullable().optional(),
  distance_km: z.number().nullable().optional(),
  delivery_price: z.number().nullable().optional(),
  quoted_price: z.number().nullable().optional(),
  notified_at: z.string().nullable().optional(),
  expires_at: z.string().nullable().optional(),
});

export const OwnerPendingOffersResponseSchema = z.object({
  offers: z.array(OwnerPendingOfferSchema),
});

export const OwnerHistoryOfferSchema = OwnerPendingOfferSchema.extend({
  status: z.string(),
  responded_at: z.string().nullable().optional(),
});

export const OwnerOfferHistoryResponseSchema = z.object({
  offers: z.array(OwnerHistoryOfferSchema),
});

export const OwnerOfferActionResponseSchema = z.object({
  assignment_id: z.string().uuid(),
  incident_id: z.string().uuid(),
  status: z.string(),
  detail: z.string(),
  next_notified_assignment_id: z.string().uuid().nullable().optional(),
});

export const OwnerAssignmentSchema = z.object({
  assignment_id: z.string().uuid(),
  incident_id: z.string().uuid(),
  problem_id: z.string().uuid().nullable().optional(),
  problem_name: z.string().nullable().optional(),
  incident_description: z.string().nullable().optional(),
  distance_km: z.number().nullable().optional(),
  delivery_price: z.number().nullable().optional(),
  quoted_price: z.number().nullable().optional(),
  status: z.string(),
  mechanic_name: z.string().nullable().optional(),
  created_at: z.string(),
});

export const OwnerAssignmentsResponseSchema = z.object({
  assignments: z.array(OwnerAssignmentSchema),
});

export const OwnerOfferDetailSchema = z.object({
  assignment_id: z.string().uuid(),
  incident_id: z.string().uuid(),
  assignment_status: z.string().optional(),
  incident_status: z.string().nullable().optional(),
  problem_id: z.string().uuid().nullable().optional(),
  problem_name: z.string().nullable().optional(),
  incident_description: z.string().nullable().optional(),
  incident_latitude: z.number(),
  incident_longitude: z.number(),
  repair_shop_latitude: z.number().nullable().optional(),
  repair_shop_longitude: z.number().nullable().optional(),
  distance_km: z.number().nullable().optional(),
  delivery_price: z.number().nullable().optional(),
  quoted_price: z.number().nullable().optional(),
  mechanic_name: z.string().nullable().optional(),
  notified_at: z.string().nullable().optional(),
  expires_at: z.string().nullable().optional(),
  evidence_urls: z.array(z.string()).optional(),
});

export const RealtimeOfferCreatedEventSchema = z.object({
  type: z.literal('assignment.offer.created'),
  payload: OwnerOfferDetailSchema,
});

export const RealtimeOfferStatusChangedPayloadSchema = z.object({
  assignment_id: z.string().uuid(),
  incident_id: z.string().uuid(),
  status: z.string(),
});

export const RealtimeOfferStatusChangedEventSchema = z.object({
  type: z.literal('assignment.offer.status_changed'),
  payload: RealtimeOfferStatusChangedPayloadSchema,
});

export const RealtimeOfferEventSchema = z.discriminatedUnion('type', [
  RealtimeOfferCreatedEventSchema,
  RealtimeOfferStatusChangedEventSchema,
]);

export type OwnerPendingOfferData = z.infer<typeof OwnerPendingOfferSchema>;
export type OwnerHistoryOfferData = z.infer<typeof OwnerHistoryOfferSchema>;
export type OwnerOfferDetailData = z.infer<typeof OwnerOfferDetailSchema>;
export type OwnerOfferActionResponseData = z.infer<typeof OwnerOfferActionResponseSchema>;
export type OwnerAssignmentData = z.infer<typeof OwnerAssignmentSchema>;
export type RealtimeOfferEventData = z.infer<typeof RealtimeOfferEventSchema>;
export type RealtimeOfferStatusChangedData = z.infer<typeof RealtimeOfferStatusChangedPayloadSchema>;
