import { CommonModule } from '@angular/common';
import {
  AfterViewInit,
  Component,
  DestroyRef,
  ElementRef,
  OnDestroy,
  ViewChild,
  inject,
  signal,
} from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import * as L from 'leaflet';

import { APP_ROUTES } from '../../../../../core/config/routes';
import { AuthTokenService } from '../../../../../core/services/auth-token.service';
import { AppToastService } from '../../../../../core/services/app-toast.service';
import { RealtimeIncidentRepository } from '../../../../../features/realtime/data/repositories/realtime-incident.repository';
import { RealtimeOffersRepository } from '../../../../../features/realtime/data/repositories/realtime-offers.repository';
import type {
  IncidentActivityEvent,
  IncidentActivitySnapshot,
} from '../../../../../features/realtime/domain/entities/incident-activity';
import type { OwnerOfferDetail } from '../../../../../features/realtime/domain/entities/owner-offer';
import { IncidentActivitySocketService } from '../../../../../features/realtime/presentation/services/incident-activity-socket.service';
import { formatUtcDateToLocal } from '../../../../../features/shared/data/infrastructure/date-time';
import { PageHeadingComponent } from '../../../../../features/shared/presentation/components/layout/page-heading.component';
import { HomeHeaderComponent } from '../../components/home-header/home-header.component';

const incidentIcon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const mechanicIcon = L.divIcon({
  className: 'mechanic-marker',
  html: '<div style="width:14px;height:14px;border-radius:9999px;background:#0ea5e9;border:2px solid white;box-shadow:0 0 0 2px rgba(14,165,233,0.25);"></div>',
  iconSize: [14, 14],
  iconAnchor: [7, 7],
});

const shopIcon = L.divIcon({
  className: 'shop-marker',
  html: '<div style="width:14px;height:14px;border-radius:9999px;background:#64748b;border:2px solid white;box-shadow:0 0 0 2px rgba(100,116,139,0.25);"></div>',
  iconSize: [14, 14],
  iconAnchor: [7, 7],
});

@Component({
  selector: 'app-owner-assignment-activity-page',
  standalone: true,
  imports: [CommonModule, HomeHeaderComponent, PageHeadingComponent],
  template: `
    <main class="app-dashboard-bg min-h-screen">
      <app-home-header />

      <section class="mx-auto w-full max-w-[1500px] px-4 pb-10 pt-6 sm:px-6">
        <button
          type="button"
          class="mb-4 inline-flex items-center gap-2 rounded-full border border-[var(--app-card-soft-border)] px-4 py-2 text-sm font-semibold text-[var(--app-text-primary)] transition hover:bg-[var(--app-card-soft-bg)]"
          (click)="goBack()"
        >
          <span aria-hidden="true">←</span>
          Volver atras
        </button>

        <app-page-heading
          title="Actividad de asignacion"
          subtitle="Monitorea el estado en tiempo real del incidente asignado."
        />

        <section class="mt-6 grid gap-4 lg:grid-cols-[1.4fr_1fr]">
          <article class="rounded-2xl border border-[var(--app-card-soft-border)] bg-[var(--app-card-bg)] p-4">
            <div #mapContainer class="h-[420px] w-full overflow-hidden rounded-xl"></div>
          </article>

          <article class="rounded-2xl border border-[var(--app-card-soft-border)] bg-[var(--app-card-bg)] p-5">
            <h3 class="text-lg font-semibold text-[var(--app-text-primary)]">Estado actual</h3>
            <div class="mt-3 space-y-2 text-sm text-[var(--auth-text-secondary)]">
              <p>
                <strong class="text-[var(--app-text-primary)]">Problema:</strong>
                {{ offerDetail()?.problemName || 'Incidente clasificado' }}
              </p>
              <p>
                <strong class="text-[var(--app-text-primary)]">Descripcion:</strong>
                {{ offerDetail()?.incidentDescription || 'Sin descripcion del cliente.' }}
              </p>
              <p>
                <strong class="text-[var(--app-text-primary)]">Estado:</strong>
                {{ statusLabel(snapshotData()?.snapshot?.status || null) }}
              </p>
              <p>
                <strong class="text-[var(--app-text-primary)]">Mecanico:</strong>
                {{ offerDetail()?.mechanicName || 'Sin mecanico asignado' }}
              </p>
            </div>

            <h4 class="mt-5 text-sm font-semibold text-[var(--app-text-primary)]">Timeline</h4>
            <div class="mt-2 max-h-[260px] space-y-2 overflow-y-auto pr-1">
              <article
                *ngFor="let event of events(); trackBy: trackByEvent"
                class="rounded-xl border border-[var(--app-card-soft-border)] bg-[var(--app-card-soft-bg)] px-3 py-2"
              >
                <p class="text-xs font-semibold uppercase text-[var(--app-text-primary)]">{{ eventTypeLabel(event.type) }}</p>
                <p class="mt-1 text-xs text-[var(--auth-text-secondary)]">{{ formatDate(event.createdAt) }}</p>
              </article>

              <article
                *ngIf="events().length === 0"
                class="rounded-xl border border-dashed border-[var(--app-card-soft-border)] bg-[var(--app-card-soft-bg)] px-3 py-4 text-sm text-[var(--auth-text-secondary)]"
              >
                Aun no hay eventos para mostrar.
              </article>
            </div>
          </article>
        </section>
      </section>
    </main>
  `,
})
export class OwnerAssignmentActivityPageComponent implements AfterViewInit, OnDestroy {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly destroyRef = inject(DestroyRef);
  private readonly authTokenService = inject(AuthTokenService);
  private readonly appToast = inject(AppToastService);
  private readonly offersRepository = inject(RealtimeOffersRepository);
  private readonly incidentRepository = inject(RealtimeIncidentRepository);
  private readonly incidentSocket = inject(IncidentActivitySocketService);

  readonly assignmentId = this.route.snapshot.paramMap.get('assignmentId') ?? '';
  readonly incidentId = signal<string | null>(null);
  readonly offerDetail = signal<OwnerOfferDetail | null>(null);
  readonly snapshotData = signal<IncidentActivitySnapshot | null>(null);
  readonly events = signal<IncidentActivityEvent[]>([]);

  @ViewChild('mapContainer', { static: true })
  private mapContainerRef!: ElementRef<HTMLDivElement>;

  private map: L.Map | null = null;
  private incidentMarker: L.Marker | null = null;
  private shopMarker: L.Marker | null = null;
  private mechanicMarker: L.Marker | null = null;
  private hasCenteredMap = false;

  constructor() {
    const snapshotSubscription = this.incidentSocket.snapshot$.subscribe((snapshot) => {
      const mapped = this.incidentRepository.mapSnapshotFromSocket(snapshot);
      this.snapshotData.set(mapped);
      this.events.set(mapped.events);
      this.refreshMapMarkers();
    });

    const eventSubscription = this.incidentSocket.event$.subscribe((event) => {
      const mapped = this.incidentRepository.mapSocketEvent(event);
      if (!mapped) {
        return;
      }

      this.events.update((current) => {
        if (current.some((item) => item.id === mapped.id)) {
          return current;
        }
        return [...current, mapped];
      });

      const nextStatus = this.extractStatusFromEvent(event.payload);
      if (nextStatus) {
        this.snapshotData.update((current) => {
          if (!current) {
            return current;
          }

          return {
            ...current,
            snapshot: {
              ...current.snapshot,
              status: nextStatus,
            },
          };
        });
      }

      if (event.type === 'mechanic.location.updated') {
        const latitude = this.extractNumber(
          event.payload['mechanic_latitude'] ?? event.payload['latitude'],
        );
        const longitude = this.extractNumber(
          event.payload['mechanic_longitude'] ?? event.payload['longitude'],
        );
        if (latitude !== null && longitude !== null) {
          this.snapshotData.update((current) => {
            if (!current) {
              return current;
            }
            return {
              ...current,
              snapshot: {
                ...current.snapshot,
                mechanicLatitude: latitude,
                mechanicLongitude: longitude,
                mechanicLocationUpdatedAt:
                  typeof event.payload['mechanic_location_updated_at'] === 'string'
                    ? event.payload['mechanic_location_updated_at']
                    : typeof event.payload['updated_at'] === 'string'
                    ? event.payload['updated_at']
                    : current.snapshot.mechanicLocationUpdatedAt,
              },
            };
          });
          this.refreshMapMarkers();
        }
      }
    });

    this.destroyRef.onDestroy(() => {
      snapshotSubscription.unsubscribe();
      eventSubscription.unsubscribe();
    });

    void this.loadActivity();
  }

  ngAfterViewInit(): void {
    this.map = L.map(this.mapContainerRef.nativeElement, {
      zoomControl: true,
      dragging: true,
      scrollWheelZoom: true,
      doubleClickZoom: true,
      touchZoom: true,
      keyboard: false,
    }).setView([-17.7833, -63.1821], 12);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap contributors',
    }).addTo(this.map);

    this.refreshMapMarkers();
  }

  ngOnDestroy(): void {
    this.incidentSocket.disconnect();
    this.map?.remove();
    this.map = null;
    this.incidentMarker = null;
    this.shopMarker = null;
    this.mechanicMarker = null;
  }

  async goBack(): Promise<void> {
    await this.router.navigateByUrl(APP_ROUTES.APP_OWNER_ASSIGNMENTS);
  }

  trackByEvent(_: number, event: IncidentActivityEvent): string {
    return event.id;
  }

  statusLabel(status: string | null): string {
    if (!status) {
      return 'Sin estado';
    }
    const statusMap: Record<string, string> = {
      pending: 'Pendiente',
      classifying: 'Clasificando',
      classified: 'Clasificado',
      searching_shop: 'Buscando taller',
      assigned: 'Asignado',
      on_the_way: 'En camino',
      arrived: 'Llegado',
      completed: 'Completado',
      cancelled: 'Cancelado',
      failed: 'Fallido',
    };

    return statusMap[status] ?? status;
  }

  eventTypeLabel(type: string): string {
    return type
      .split('.')
      .map((part) => part.replaceAll('_', ' '))
      .join(' - ');
  }

  formatDate(value: string): string {
    return formatUtcDateToLocal(value);
  }

  private async loadActivity(): Promise<void> {
    const detailResponse = await this.offersRepository.getOfferDetail(this.assignmentId);
    if (!detailResponse.ok) {
      this.appToast.showErrorList(detailResponse.errors);
      return;
    }

    this.offerDetail.set(detailResponse.data);
    this.incidentId.set(detailResponse.data.incidentId);
    this.refreshMapMarkers();

    const snapshotResponse = await this.incidentRepository.getIncidentSnapshot(detailResponse.data.incidentId);
    if (!snapshotResponse.ok) {
      this.appToast.showErrorList(snapshotResponse.errors);
      return;
    }

    this.snapshotData.set(snapshotResponse.data);
    this.events.set(snapshotResponse.data.events);
    this.refreshMapMarkers();

    const token = this.authTokenService.getToken();
    if (!token) {
      return;
    }

    this.incidentSocket.connect(detailResponse.data.incidentId, token);
  }

  private refreshMapMarkers(): void {
    if (!this.map) {
      return;
    }

    const detail = this.offerDetail();
    if (detail) {
      const incidentPoint: L.LatLngTuple = [detail.incidentLatitude, detail.incidentLongitude];
      if (!this.incidentMarker) {
        this.incidentMarker = L.marker(incidentPoint, { icon: incidentIcon }).addTo(this.map);
      } else {
        this.incidentMarker.setLatLng(incidentPoint);
      }
      this.incidentMarker.bindPopup('Ubicacion del incidente');

      if (!this.hasCenteredMap) {
        this.map.setView(incidentPoint, 13);
        this.hasCenteredMap = true;
      }
    }

    if (detail && detail.repairShopLatitude !== null && detail.repairShopLongitude !== null) {
      const shopPoint: L.LatLngTuple = [detail.repairShopLatitude, detail.repairShopLongitude];
      if (!this.shopMarker) {
        this.shopMarker = L.marker(shopPoint, { icon: shopIcon }).addTo(this.map);
      } else {
        this.shopMarker.setLatLng(shopPoint);
      }
      this.shopMarker.bindPopup('Ubicacion del taller');
    } else if (this.shopMarker) {
      this.map.removeLayer(this.shopMarker);
      this.shopMarker = null;
    }

    const snapshot = this.snapshotData()?.snapshot;
    if (!snapshot || snapshot.mechanicLatitude === null || snapshot.mechanicLongitude === null) {
      if (this.mechanicMarker) {
        this.map.removeLayer(this.mechanicMarker);
        this.mechanicMarker = null;
      }
      return;
    }

    const mechanicPoint: L.LatLngTuple = [snapshot.mechanicLatitude, snapshot.mechanicLongitude];
    if (!this.mechanicMarker) {
      this.mechanicMarker = L.marker(mechanicPoint, { icon: mechanicIcon }).addTo(this.map);
    } else {
      this.mechanicMarker.setLatLng(mechanicPoint);
    }

    this.mechanicMarker.bindPopup('Ubicacion del mecanico');
  }

  private extractStatusFromEvent(payload: Record<string, unknown>): string | null {
    const statusValue = payload['status'];
    if (typeof statusValue !== 'string') {
      return null;
    }

    const trimmedStatus = statusValue.trim();
    return trimmedStatus.length > 0 ? trimmedStatus : null;
  }

  private extractNumber(value: unknown): number | null {
    if (typeof value === 'number') {
      return Number.isFinite(value) ? value : null;
    }
    if (typeof value !== 'string') {
      return null;
    }

    const parsed = Number.parseFloat(value);
    return Number.isFinite(parsed) ? parsed : null;
  }
}
