export type OwnerWalletBalance = {
  walletId: string;
  repairShopId: string;
  balance: number;
  updatedAt: string;
};

export type OwnerWalletTransaction = {
  id: string;
  type: string;
  status: string;
  amount: number;
  balanceBefore: number;
  balanceAfter: number;
  description: string | null;
  createdAt: string;
};

export type OwnerWalletTopupQr = {
  transactionId: string;
  internalReference: string;
  amount: number;
  walletId: string;
  repairShopId: string;
  generatedAt: string;
  expiresAt: string;
  status: string;
  qrPayload: string;
  qrImageUrl: string;
};

export type OwnerWalletTopupConfirm = {
  transactionId: string;
  status: string;
  previousBalance: number;
  newBalance: number;
};
