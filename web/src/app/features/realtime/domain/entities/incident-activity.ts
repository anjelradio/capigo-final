export type IncidentLiveSnapshot = {
  status: string | null;
  assignmentId: string | null;
  repairShopId: string | null;
  mechanicId: string | null;
  mechanicLatitude: number | null;
  mechanicLongitude: number | null;
  mechanicLocationUpdatedAt: string | null;
  lastEventAt: string | null;
};

export type IncidentActivityEvent = {
  id: string;
  type: string;
  payload: Record<string, unknown>;
  createdAt: string;
};

export type IncidentActivitySnapshot = {
  incidentId: string;
  snapshot: IncidentLiveSnapshot;
  events: IncidentActivityEvent[];
};
