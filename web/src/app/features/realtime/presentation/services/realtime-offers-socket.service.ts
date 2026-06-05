import { Injectable, inject } from '@angular/core';
import { Router } from '@angular/router';
import { Subject, take } from 'rxjs';

import { environment } from '../../../../../environments/environment';
import { API_ENDPOINTS } from '../../../../core/config/api-endpoints';
import { APP_ROUTES } from '../../../../core/config/routes';
import { AppToastService } from '../../../../core/services/app-toast.service';
import { RealtimeOffersRepository } from '../../data/repositories/realtime-offers.repository';
import { RealtimeOfferEventSchema } from '../../data/schemas/realtime-offer.schema';
import type { OwnerOfferDetail } from '../../domain/entities/owner-offer';

type OfferStatusChangedEvent = {
  assignmentId: string;
  incidentId: string;
  status: string;
};

const RECONNECT_DELAY_MS = 2500;

@Injectable({ providedIn: 'root' })
export class RealtimeOffersSocketService {
  private readonly appToast = inject(AppToastService);
  private readonly router = inject(Router);
  private readonly realtimeOffersRepository = inject(RealtimeOffersRepository);

  private socket: WebSocket | null = null;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private activeToken: string | null = null;
  private manualDisconnect = false;
  private readonly seenAssignmentIds = new Set<string>();

  private readonly offerCreatedSubject = new Subject<OwnerOfferDetail>();
  private readonly offerStatusChangedSubject = new Subject<OfferStatusChangedEvent>();
  private readonly offerClickedSubject = new Subject<string>();
  private readonly notificationAudio = new Audio('/notification.mp3');

  readonly offerCreated$ = this.offerCreatedSubject.asObservable();
  readonly offerStatusChanged$ = this.offerStatusChangedSubject.asObservable();
  readonly offerClicked$ = this.offerClickedSubject.asObservable();

  connect(token: string): void {
    if (!token) {
      return;
    }

    const isSameToken = token === this.activeToken;
    const isSocketOpen =
      this.socket?.readyState === WebSocket.OPEN || this.socket?.readyState === WebSocket.CONNECTING;
    if (isSameToken && isSocketOpen) {
      return;
    }

    this.manualDisconnect = false;
    this.clearReconnectTimer();
    this.activeToken = token;
    this.openSocket(token);
  }

  disconnect(): void {
    this.manualDisconnect = true;
    this.activeToken = null;
    this.clearReconnectTimer();
    this.seenAssignmentIds.clear();

    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }

  private openSocket(token: string): void {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }

    const wsUrl = this.buildWsUrl(token);
    this.socket = new WebSocket(wsUrl);

    this.socket.onopen = () => {
      console.info('[realtime] shop offers socket connected');
    };
    this.socket.onmessage = (event) => this.handleMessage(event.data);
    this.socket.onclose = (event) => {
      console.warn('[realtime] shop offers socket closed', event.code, event.reason || 'no-reason');
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
    if (!this.activeToken || this.reconnectTimer) {
      return;
    }

    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      if (!this.activeToken || this.manualDisconnect) {
        return;
      }

      this.openSocket(this.activeToken);
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

    const parsedEvent = RealtimeOfferEventSchema.safeParse(parsedJson);
    if (!parsedEvent.success) {
      console.warn('[realtime] invalid socket payload', parsedEvent.error.flatten());
      return;
    }

    if (parsedEvent.data.type === 'assignment.offer.status_changed') {
      this.offerStatusChangedSubject.next({
        assignmentId: parsedEvent.data.payload.assignment_id,
        incidentId: parsedEvent.data.payload.incident_id,
        status: parsedEvent.data.payload.status,
      });
      return;
    }

    const offerDetail = this.realtimeOffersRepository.mapOfferDetailFromSocket(parsedEvent.data.payload);
    const assignmentId = offerDetail.assignmentId;
    if (this.seenAssignmentIds.has(assignmentId)) {
      return;
    }

    this.seenAssignmentIds.add(assignmentId);
    this.offerCreatedSubject.next(offerDetail);
    this.playNotificationSound();

    const problem = offerDetail.problemName ?? 'Incidente';
    const distance = offerDetail.distanceKm ? `${offerDetail.distanceKm.toFixed(1)} km` : 'distancia n/d';
    const price =
      offerDetail.deliveryPrice !== null ? `Bs ${offerDetail.deliveryPrice.toFixed(2)}` : 'precio n/d';
    const toastTap$ = this.appToast.infoClickable(
      `${problem} | ${distance} | ${price}`,
      'Nueva oferta disponible',
    );

    toastTap$?.pipe(take(1)).subscribe(async () => {
      await this.router.navigate([APP_ROUTES.APP_OWNER_ASSIGNMENTS, assignmentId, 'detail']);
      this.offerClickedSubject.next(assignmentId);
    });
  }

  private buildWsUrl(token: string): string {
    const wsApiBase = environment.apiUrl.replace(/^http/, 'ws');
    return `${wsApiBase}${API_ENDPOINTS.REALTIME.SHOP_OFFERS_WS}?token=${encodeURIComponent(token)}`;
  }

  private playNotificationSound(): void {
    try {
      this.notificationAudio.currentTime = 0;
      void this.notificationAudio.play().catch(() => undefined);
    } catch {
      // no-op
    }
  }
}
