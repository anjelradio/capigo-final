import { z } from 'zod';

export const OwnerWalletBalanceSchema = z.object({
  wallet_id: z.string().uuid(),
  repair_shop_id: z.string().uuid(),
  balance: z.number(),
  updated_at: z.string(),
});

export const OwnerWalletTransactionSchema = z.object({
  id: z.string().uuid(),
  type: z.string(),
  status: z.string(),
  amount: z.number(),
  balance_before: z.number(),
  balance_after: z.number(),
  description: z.string().nullable().optional(),
  created_at: z.string(),
});

export const OwnerWalletTransactionsResponseSchema = z.object({
  transactions: z.array(OwnerWalletTransactionSchema),
});

export const OwnerWalletTopupQrRequestSchema = z.object({
  amount: z.number().positive('El monto debe ser mayor a 0'),
});

export const OwnerWalletTopupQrSchema = z.object({
  transaction_id: z.string().uuid(),
  internal_reference: z.string(),
  amount: z.number(),
  wallet_id: z.string().uuid(),
  repair_shop_id: z.string().uuid(),
  generated_at: z.string(),
  expires_at: z.string(),
  status: z.string(),
  qr_payload: z.string(),
  qr_image_url: z.string().url(),
});

export const OwnerWalletTopupConfirmSchema = z.object({
  transaction_id: z.string().uuid(),
  status: z.string(),
  previous_balance: z.number(),
  new_balance: z.number(),
});

export type OwnerWalletBalanceData = z.infer<typeof OwnerWalletBalanceSchema>;
export type OwnerWalletTransactionData = z.infer<typeof OwnerWalletTransactionSchema>;
export type OwnerWalletTopupQrRequestData = z.infer<typeof OwnerWalletTopupQrRequestSchema>;
export type OwnerWalletTopupQrData = z.infer<typeof OwnerWalletTopupQrSchema>;
export type OwnerWalletTopupConfirmData = z.infer<typeof OwnerWalletTopupConfirmSchema>;
