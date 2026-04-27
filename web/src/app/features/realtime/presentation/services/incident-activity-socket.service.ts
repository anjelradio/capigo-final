import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

import { environment } from '../../../../../environments/environment';
import { API_ENDPOINTS } from '../../../../core/config/api-endpoints';
import {
  IncidentSocketRealtimeEventSchema,
  IncidentSocketSnapshotEventSchema,
  type IncidentSnapshotResponseData,
  type IncidentSocketRealtimeEventData,
} from '../../data/schemas/realtime-incident.schema';

const RECONNECT_DELAY_MS = 2500;

@Injectable({ providedIn: 'root' })
export class IncidentActivitySocketService {
  private socket: WebSocket | null = null;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private manualDisconnect = false;
  private activeToken: string | null = null;
  private activeIncidentId: string | null = null;

  private readonly snapshotSubject = new Subject<IncidentSnapshotResponseData>();
  private readonly eventSubject = new Subject<IncidentSocketRealtimeEventData>();

  readonly snapshot$ = this.snapshotSubject.asObservable();
  readonly event$ = this.eventSubject.asObservable();

  connect(incidentId: string, token: string): void {
    if (!incidentId || !token) {
      return;
    }

    const sameConnection =
      this.activeIncidentId === incidentId &&
      this.activeToken === token &&
      (this.socket?.readyState === WebSocket.OPEN || this.socket?.readyState === WebSocket.CONNECTING);

    if (sameConnection) {
      return;
    }

    this.manualDisconnect = false;
    this.clearReconnectTimer();
    this.activeIncidentId = incidentId;
    this.activeToken = token;
    this.openSocket();
  }

  disconnect(): void {
    this.manualDisconnect = true;
    this.activeIncidentId = null;
    this.activeToken = null;
    this.clearReconnectTimer();

    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }

  private openSocket(): void {
    if (!this.activeIncidentId || !this.activeToken) {
      return;
    }

    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }

    const wsUrl = this.buildWsUrl(this.activeIncidentId, this.activeToken);
    this.socket = new WebSocket(wsUrl);

    this.socket.onmessage = (event) => this.handleMessage(event.data);
    this.socket.onclose = () => {
      this.socket = null;
      if (!this.manualDisconnect) {
        this.scheduleReconnect();
      }
    };
    this.socket.onerror = () => {
      this.socket?.close();
    };
  }

  private scheduleReconnect(): void {
    if (!this.activeIncidentId || !this.activeToken || this.reconnectTimer) {
      return;
    }

    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      if (!this.activeIncidentId || !this.activeToken || this.manualDisconnect) {
        return;
      }

      this.openSocket();
    }, RECONNECT_DELAY_MS);
  }

  private clearReconnectTimer(): void {
    if (!this.reconnectTimer) {
      return;
    }

    clearTimeout(this.reconnectTimer);
    this.reconnectTimer = null;
  }

  private handleMessage(rawData: unknown): void {
    if (typeof rawData !== 'string') {
      return;
    }

    let parsedJson: unknown;
    try {
      parsedJson = JSON.parse(rawData);
    } catch {
      return;
    }

    const snapshotResult = IncidentSocketSnapshotEventSchema.safeParse(parsedJson);
    if (snapshotResult.success) {
      this.snapshotSubject.next(snapshotResult.data.payload);
      return;
    }

    const eventResult = IncidentSocketRealtimeEventSchema.safeParse(parsedJson);
    if (eventResult.success) {
      this.eventSubject.next(eventResult.data);
    }
  }

  private buildWsUrl(incidentId: string, token: string): string {
    const wsApiBase = environment.apiUrl.replace(/^http/, 'ws');
    return `${wsApiBase}${API_ENDPOINTS.REALTIME.INCIDENT_WS_BASE}/${incidentId}?token=${encodeURIComponent(token)}`;
  }
}
