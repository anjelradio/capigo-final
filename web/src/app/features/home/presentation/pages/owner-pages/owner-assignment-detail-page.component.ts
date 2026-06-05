import { CommonModule } from '@angular/common';
import { Component, DestroyRef, inject, signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';

import { APP_ROUTES } from '../../../../../core/config/routes';
import { AppToastService } from '../../../../../core/services/app-toast.service';
import { RepairShopRepository } from '../../../../../features/repair-shop/data/repositories/repair-shop.repository';
import type { ShopMechanicData } from '../../../../../features/repair-shop/data/schemas/repair-shop.schema';
import { RealtimeIncidentRepository } from '../../../../../features/realtime/data/repositories/realtime-incident.repository';
import { RealtimeOffersRepository } from '../../../../../features/realtime/data/repositories/realtime-offers.repository';
import type {
  IncidentActivityEvent,
  IncidentActivitySnapshot,
} from '../../../../../features/realtime/domain/entities/incident-activity';
import type { OwnerOfferDetail } from '../../../../../features/realtime/domain/entities/owner-offer';
import { IncidentActivitySocketService } from '../../../../../features/realtime/presentation/services/incident-activity-socket.service';
import { RealtimeOffersSocketService } from '../../../../../features/realtime/presentation/services/realtime-offers-socket.service';
import { AuthTokenService } from '../../../../../core/services/auth-token.service';
import { HomeHeaderComponent } from '../../components/home-header/home-header.component';
import { OwnerAssignmentDetailMapComponent } from '../../components/owner-assignment-detail/owner-assignment-detail-map.component';
import { OwnerAssignmentIncidentCardComponent } from '../../components/owner-assignment-detail/owner-assignment-incident-card.component';
import { OwnerAssignmentMechanicCardComponent } from '../../components/owner-assignment-detail/owner-assignment-mechanic-card.component';
import { OfferMechanicAssignmentModalComponent } from '../../../../../features/realtime/presentation/components/offer-mechanic-assignment-modal.component';

@Component({
  selector: 'app-owner-assignment-detail-page',
  standalone: true,
  imports: [
    CommonModule,
    HomeHeaderComponent,
    OwnerAssignmentDetailMapComponent,
    OwnerAssignmentIncidentCardComponent,
    OwnerAssignmentMechanicCardComponent,
    OfferMechanicAssignmentModalComponent,
  ],
  template: `
    <main class="app-dashboard-bg min-h-screen">
      <app-home-header />

      <section class="relative h-[calc(100vh-78px)] w-full overflow-hidden">
        <app-owner-assignment-detail-map
          [incidentLatitude]="offerDetail()?.incidentLatitude ?? null"
          [incidentLongitude]="offerDetail()?.incidentLongitude ?? null"
          [shopLatitude]="offerDetail()?.repairShopLatitude ?? null"
          [shopLongitude]="offerDetail()?.repairShopLongitude ?? null"
          [mechanicLatitude]="snapshotData()?.snapshot?.mechanicLatitude ?? null"
          [mechanicLongitude]="snapshotData()?.snapshot?.mechanicLongitude ?? null"
        />

        <div class="pointer-events-none absolute inset-0 bg-gradient-to-b from-black/20 via-transparent to-black/20"></div>

        <div class="absolute left-4 top-16 z-[500] w-[420px] max-w-[calc(100%-2rem)]">
          <button
            type="button"
            class="mb-3 inline-flex items-center gap-2 rounded-full bg-[var(--app-card-bg)]/95 px-3 py-2 text-xs font-semibold text-[var(--app-text-primary)] shadow-lg"
            (click)="goBack()"
          >
            <span aria-hidden="true">←</span>
            Volver
          </button>

          <app-owner-assignment-incident-card
            [detail]="offerDetail()"
            [detailStatus]="statusLabel(currentIncidentStatus())"
            [detailStatusRaw]="currentIncidentStatus()"
            [canSubmitOffer]="canSubmitOffer()"
            [isSubmitting]="isSubmittingOffer()"
            [showTimeline]="isTrackingMode()"
            [events]="events()"
            (submitOffer)="openSubmitOfferModal()"
          />
        </div>

        <div class="absolute bottom-4 left-1/2 z-[500] w-[720px] max-w-[calc(100%-2rem)] -translate-x-1/2">
          <app-owner-assignment-mechanic-card
            [mechanicName]="offerDetail()?.mechanicName ?? null"
            [statusLabel]="statusLabel(currentIncidentStatus())"
          />
        </div>
      </section>

      <app-offer-mechanic-assignment-modal
        [open]="isMechanicModalOpen()"
        [mechanics]="availableMechanics()"
        [selectedMechanicId]="selectedMechanicId()"
        [quotedPrice]="quotedPrice()"
        [isSubmitting]="isSubmittingOffer()"
        (openChange)="setMechanicModalOpen($event)"
        (selectedMechanicIdChange)="setSelectedMechanicId($event)"
        (quotedPriceChange)="setQuotedPrice($event)"
        (assign)="confirmSubmitOffer()"
      />
    </main>
  `,
})
export class OwnerAssignmentDetailPageComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly destroyRef = inject(DestroyRef);
  private readonly appToast = inject(AppToastService);
  private readonly offersRepository = inject(RealtimeOffersRepository);
  private readonly incidentRepository = inject(RealtimeIncidentRepository);
  private readonly incidentSocket = inject(IncidentActivitySocketService);
  private readonly realtimeOffersSocket = inject(RealtimeOffersSocketService);
  private readonly repairShopRepository = inject(RepairShopRepository);
  private readonly authTokenService = inject(AuthTokenService);

  readonly assignmentId = this.route.snapshot.paramMap.get('assignmentId') ?? '';
  readonly offerDetail = signal<OwnerOfferDetail | null>(null);
  readonly snapshotData = signal<IncidentActivitySnapshot | null>(null);
  readonly events = signal<IncidentActivityEvent[]>([]);
  readonly availableMechanics = signal<ShopMechanicData[]>([]);
  readonly selectedMechanicId = signal<string | null>(null);
  readonly quotedPrice = signal<string>('');
  readonly isMechanicModalOpen = signal(false);
  readonly isSubmittingOffer = signal(false);

  constructor() {
    const snapshotSubscription = this.incidentSocket.snapshot$.subscribe((snapshot) => {
      const mapped = this.incidentRepository.mapSnapshotFromSocket(snapshot);
      this.snapshotData.set(mapped);
      this.events.set(mapped.events);
    });

    const eventSubscription = this.incidentSocket.event$.subscribe((event) => {
      const mapped = this.incidentRepository.mapSocketEvent(event);
      if (!mapped) return;

      const nextStatus = this.extractStatusFromEvent(event.payload);
      this.events.update((current) => {
        if (current.some((item) => item.id === mapped.id)) {
          return current;
        }
        return [...current, mapped];
      });

      const nextMechanicLatitude = this.extractNumber(
        event.payload['mechanic_latitude'] ?? event.payload['latitude'],
      );
      const nextMechanicLongitude = this.extractNumber(
        event.payload['mechanic_longitude'] ?? event.payload['longitude'],
      );

      this.snapshotData.update((current) => {
        if (!current) return current;
        return {
          ...current,
          snapshot: {
            ...current.snapshot,
            status: nextStatus ?? current.snapshot.status,
            mechanicLatitude: nextMechanicLatitude ?? current.snapshot.mechanicLatitude,
            mechanicLongitude: nextMechanicLongitude ?? current.snapshot.mechanicLongitude,
            mechanicLocationUpdatedAt:
              typeof event.payload['mechanic_location_updated_at'] === 'string'
                ? event.payload['mechanic_location_updated_at']
                : current.snapshot.mechanicLocationUpdatedAt,
          },
        };
      });
    });
    const offerStatusChangedSubscription = this.realtimeOffersSocket.offerStatusChanged$.subscribe((event) => {
      if (event.assignmentId !== this.assignmentId) return;
      void this.loadData();
    });

    this.destroyRef.onDestroy(() => {
      snapshotSubscription.unsubscribe();
      eventSubscription.unsubscribe();
      offerStatusChangedSubscription.unsubscribe();
      this.incidentSocket.disconnect();
    });

    void this.loadData();
  }

  async goBack(): Promise<void> {
    await this.router.navigateByUrl(APP_ROUTES.APP_OWNER_REQUESTS);
  }

  statusLabel(status: string | null): string {
    if (!status) return 'Sin estado';
    const statusMap: Record<string, string> = {
      pending: 'Pendiente',
      offered: 'Ofertado',
      accepted: 'Aceptado',
      completed: 'Completado',
      cancelled: 'Cancelado',
      failed: 'Fallido',
      assigned: 'Asignado',
      on_the_way: 'En camino',
      arrived: 'Llegado',
      searching_shop: 'Buscando taller',
      classifying: 'Clasificando',
      classified: 'Clasificado',
    };
    return statusMap[status] ?? status;
  }

  currentIncidentStatus(): string | null {
    return this.snapshotData()?.snapshot?.status || this.offerDetail()?.incidentStatus || null;
  }

  currentAssignmentStatus(): string {
    return (this.offerDetail()?.assignmentStatus || '').trim().toLowerCase();
  }

  isTrackingMode(): boolean {
    const incidentStatus = (this.currentIncidentStatus() || '').trim().toLowerCase();
    const assignmentStatus = this.currentAssignmentStatus();
    return (
      assignmentStatus === 'accepted' ||
      incidentStatus === 'assigned' ||
      incidentStatus === 'on_the_way' ||
      incidentStatus === 'arrived'
    );
  }

  canSubmitOffer(): boolean {
    return this.currentAssignmentStatus() === 'pending';
  }

  async openSubmitOfferModal(): Promise<void> {
    if (!this.canSubmitOffer()) return;

    const mechanicsResponse = await this.repairShopRepository.listMyShopMechanics(true);
    if (!mechanicsResponse.ok) {
      this.appToast.showErrorList(mechanicsResponse.errors);
      return;
    }

    this.availableMechanics.set(mechanicsResponse.data);
    if (mechanicsResponse.data.length === 0) {
      this.appToast.warning('No tienes mecanicos disponibles para asignar.');
      return;
    }

    this.selectedMechanicId.set(mechanicsResponse.data[0].id);
    this.quotedPrice.set('');
    this.isMechanicModalOpen.set(true);
  }

  setMechanicModalOpen(open: boolean): void {
    if (this.isSubmittingOffer()) return;
    this.isMechanicModalOpen.set(open);
  }

  setSelectedMechanicId(mechanicId: string): void {
    this.selectedMechanicId.set(mechanicId);
  }

  setQuotedPrice(value: string): void {
    this.quotedPrice.set(value);
  }

  async confirmSubmitOffer(): Promise<void> {
    const mechanicId = this.selectedMechanicId();
    const rawPrice = this.quotedPrice().trim();
    const parsedPrice = Number.parseFloat(rawPrice);
    if (!mechanicId || !Number.isFinite(parsedPrice) || parsedPrice <= 0) {
      this.appToast.warning('Ingresa un precio valido mayor a 0.');
      return;
    }

    this.isSubmittingOffer.set(true);
    const response = await this.offersRepository.submitOffer(this.assignmentId, mechanicId, parsedPrice);
    this.isSubmittingOffer.set(false);

    if (!response.ok) {
      this.appToast.showErrorList(response.errors);
      return;
    }

    this.appToast.success('Oferta enviada correctamente.');
    this.isMechanicModalOpen.set(false);
    await this.loadData();
  }

  private async loadData(): Promise<void> {
    const detailResponse = await this.offersRepository.getOfferDetail(this.assignmentId);
    if (!detailResponse.ok) {
      this.appToast.showErrorList(detailResponse.errors);
      return;
    }

    this.offerDetail.set(detailResponse.data);

    const snapshotResponse = await this.incidentRepository.getIncidentSnapshot(detailResponse.data.incidentId);
    if (snapshotResponse.ok) {
      this.snapshotData.set(snapshotResponse.data);
      this.events.set(snapshotResponse.data.events);
    }

    const token = this.authTokenService.getToken();
    if (!token) return;
    this.incidentSocket.connect(detailResponse.data.incidentId, token);
  }

  private extractStatusFromEvent(payload: Record<string, unknown>): string | null {
    const statusValue = payload['status'];
    if (typeof statusValue !== 'string') return null;
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
