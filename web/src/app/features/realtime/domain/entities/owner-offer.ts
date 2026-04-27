export type OwnerPendingOffer = {
  assignmentId: string;
  incidentId: string;
  problemId: string | null;
  problemName: string | null;
  incidentDescription: string | null;
  distanceKm: number | null;
  deliveryPrice: number | null;
  notifiedAt: string | null;
  expiresAt: string | null;
};

export type OwnerOfferDetail = OwnerPendingOffer & {
  incidentLatitude: number;
  incidentLongitude: number;
  repairShopLatitude: number | null;
  repairShopLongitude: number | null;
  mechanicName: string | null;
  evidenceUrls: string[];
};

export type OwnerOfferHistoryItem = OwnerPendingOffer & {
  status: string;
  respondedAt: string | null;
};

export type OwnerOfferActionResult = {
  assignmentId: string;
  incidentId: string;
  status: string;
  detail: string;
  nextNotifiedAssignmentId: string | null;
};

export type OwnerAssignmentItem = {
  assignmentId: string;
  incidentId: string;
  problemId: string | null;
  problemName: string | null;
  incidentDescription: string | null;
  distanceKm: number | null;
  deliveryPrice: number | null;
  status: string;
  mechanicName: string | null;
  createdAt: string;
};
