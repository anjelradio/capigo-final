import { Injectable, inject } from '@angular/core';

import type { ApiResult } from '../../../shared/data/types/api-result';
import type {
  IncidentActivityEvent,
  IncidentActivitySnapshot,
} from '../../domain/entities/incident-activity';
import { RealtimeIncidentApiService } from '../api/realtime-incident-api.service';
import type {
  IncidentSnapshotResponseData,
  IncidentSocketRealtimeEventData,
} from '../schemas/realtime-incident.schema';

@Injectable({ providedIn: 'root' })
export class RealtimeIncidentRepository {
  private readonly incidentApi = inject(RealtimeIncidentApiService);

  async getIncidentSnapshot(incidentId: string): Promise<ApiResult<IncidentActivitySnapshot>> {
    const response = await this.incidentApi.getIncidentSnapshot(incidentId);
    if (!response.ok) {
      return response;
    }

    return {
      ok: true,
      data: this.mapSnapshot(response.data),
    };
  }

  mapSocketEvent(event: IncidentSocketRealtimeEventData): IncidentActivityEvent | null {
    if (!event.meta) {
      return null;
    }

    return {
      id: event.meta.event_id,
      type: event.type,
      payload: event.payload,
      createdAt: event.meta.created_at,
    };
  }

  mapSnapshotFromSocket(data: IncidentSnapshotResponseData): IncidentActivitySnapshot {
    return this.mapSnapshot(data);
  }

  private mapSnapshot(data: IncidentSnapshotResponseData): IncidentActivitySnapshot {
    return {
      incidentId: data.incident_id,
      snapshot: {
        status: data.snapshot.status ?? null,
        assignmentId: data.snapshot.assignment_id ?? null,
        repairShopId: data.snapshot.repair_shop_id ?? null,
        mechanicId: data.snapshot.mechanic_id ?? null,
        mechanicLatitude: data.snapshot.mechanic_latitude ?? null,
        mechanicLongitude: data.snapshot.mechanic_longitude ?? null,
        mechanicLocationUpdatedAt: data.snapshot.mechanic_location_updated_at ?? null,
        lastEventAt: data.snapshot.last_event_at ?? null,
      },
      events: data.events.map((event) => ({
        id: event.id,
        type: event.type,
        payload: event.payload,
        createdAt: event.created_at,
      })),
    };
  }
}
