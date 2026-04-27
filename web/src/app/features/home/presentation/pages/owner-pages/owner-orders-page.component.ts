import { CommonModule } from '@angular/common';
import { Component, DestroyRef, inject, signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';

import { AppToastService } from '../../../../../core/services/app-toast.service';
import { RepairShopRepository } from '../../../../../features/repair-shop/data/repositories/repair-shop.repository';
import type { ShopMechanicData } from '../../../../../features/repair-shop/data/schemas/repair-shop.schema';
import { RealtimeOffersRepository } from '../../../../../features/realtime/data/repositories/realtime-offers.repository';
import type {
  OwnerOfferDetail,
  OwnerOfferHistoryItem,
  OwnerPendingOffer,
} from '../../../../../features/realtime/domain/entities/owner-offer';
import { OwnerOfferDetailModalComponent } from '../../../../../features/realtime/presentation/components/owner-offer-detail-modal.component';
import { OfferMechanicAssignmentModalComponent } from '../../../../../features/realtime/presentation/components/offer-mechanic-assignment-modal.component';
import { RealtimeOffersSocketService } from '../../../../../features/realtime/presentation/services/realtime-offers-socket.service';
import { formatUtcDateToLocal } from '../../../../../features/shared/data/infrastructure/date-time';
import { CircularProgressLoaderComponent } from '../../../../../features/shared/presentation/components/loaders/circular-progress-loader.component';
import { PageHeadingComponent } from '../../../../../features/shared/presentation/components/layout/page-heading.component';
import { HomeHeaderComponent } from '../../components/home-header/home-header.component';

@Component({
  selector: 'app-owner-orders-page',
  standalone: true,
  imports: [
    CommonModule,
    HomeHeaderComponent,
    PageHeadingComponent,
    CircularProgressLoaderComponent,
    OwnerOfferDetailModalComponent,
    OfferMechanicAssignmentModalComponent,
  ],
  template: `
    <main class="app-dashboard-bg min-h-screen">
      <app-home-header />

      <section class="mx-auto w-full max-w-[1500px] px-4 pb-10 pt-6 sm:px-6">
        <app-page-heading
          title="Solicitudes"
          subtitle="Aqui podras revisar y gestionar las solicitudes del taller."
        />

        <section class="mt-6 grid gap-4">
          <h3 class="text-base font-semibold uppercase tracking-wide text-[var(--app-accent)]">
            Solicitudes pendientes
          </h3>
          <article
            *ngIf="isLoadingOffers()"
            class="rounded-2xl border border-[var(--app-card-soft-border)] bg-[var(--app-card-bg)] p-6 shadow-sm"
          >
            <div class="flex items-center justify-center py-3">
              <app-circular-progress-loader
                [size]="40"
                label="Cargando solicitudes pendientes"
                colorClass="border-slate-600"
              />
            </div>
          </article>
          <ng-container *ngIf="!isLoadingOffers()">
            <article
              *ngFor="let offer of pendingOffers(); trackBy: trackByAssignmentId"
              class="rounded-2xl border border-[var(--app-card-soft-border)] bg-[var(--app-card-bg)] p-5 shadow-sm"
            >
              <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p class="text-xs uppercase tracking-wide text-[var(--auth-text-secondary)]">Oferta activa</p>
                  <h4 class="text-lg font-semibold text-[var(--app-text-primary)]">
                    {{ offer.problemName || 'Incidente clasificado' }}
                  </h4>
                  <p class="mt-1 text-sm text-[var(--auth-text-secondary)]">
                    {{ offer.incidentDescription || 'Sin descripcion' }}
                  </p>
                </div>

                <button
                  type="button"
                  class="inline-flex items-center justify-center rounded-full bg-[var(--app-accent)] px-4 py-2 text-sm font-semibold text-[var(--app-accent-text)] transition hover:brightness-105"
                  (click)="openOfferDetail(offer.assignmentId)"
                >
                  Ver detalle
                </button>
              </div>

              <div class="mt-4 grid gap-2 text-sm text-[var(--auth-text-secondary)] sm:grid-cols-3">
                <p><strong class="text-[var(--app-text-primary)]">Distancia:</strong> {{ formatDistance(offer.distanceKm) }}</p>
                <p><strong class="text-[var(--app-text-primary)]">Precio:</strong> {{ formatPrice(offer.deliveryPrice) }}</p>
                <p><strong class="text-[var(--app-text-primary)]">Expira:</strong> {{ formatExpiresAt(offer.expiresAt) }}</p>
              </div>
            </article>
          </ng-container>

          <article
            *ngIf="!isLoadingOffers() && pendingOffers().length === 0"
            class="rounded-2xl border border-dashed border-[var(--app-card-soft-border)] bg-[var(--app-card-soft-bg)] p-6 text-center text-sm text-[var(--auth-text-secondary)]"
          >
            No tienes ofertas pendientes por ahora.
          </article>
        </section>

        <section class="mt-8 grid gap-4">
          <h3 class="text-base font-semibold uppercase tracking-wide text-[var(--app-accent)]">
            Historial de solicitudes
          </h3>

          <div *ngIf="isLoadingHistory()" class="flex items-center justify-center py-8">
            <app-circular-progress-loader [size]="40" label="Cargando historial de solicitudes" />
          </div>

          <ng-container *ngIf="!isLoadingHistory()">
            <article
              *ngFor="let offer of historyOffers(); trackBy: trackByAssignmentId"
              class="rounded-2xl border border-[var(--app-card-soft-border)] bg-[var(--app-card-soft-bg)] p-5"
            >
              <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <h4 class="text-lg font-semibold text-[var(--app-text-primary)]">
                    {{ offer.problemName || 'Incidente clasificado' }}
                  </h4>
                  <p class="mt-1 text-sm text-[var(--auth-text-secondary)]">
                    {{ offer.incidentDescription || 'Sin descripcion' }}
                  </p>
                </div>

                <div class="flex items-center gap-2">
                  <span
                    class="inline-flex rounded-full px-3 py-1 text-xs font-semibold"
                    [ngClass]="historyStatusClass(offer.status)"
                  >
                    {{ historyStatusLabel(offer.status) }}
                  </span>
                  <button
                    *ngIf="offer.status === 'accepted'"
                    type="button"
                    class="inline-flex items-center justify-center rounded-full bg-[var(--app-accent)] px-4 py-2 text-sm font-semibold text-[var(--app-accent-text)] transition hover:brightness-105"
                    (click)="openAcceptedHistoryDetail(offer.assignmentId)"
                  >
                    Ver detalle
                  </button>
                </div>
              </div>

              <div class="mt-4 grid gap-2 text-sm text-[var(--auth-text-secondary)] sm:grid-cols-3">
                <p><strong class="text-[var(--app-text-primary)]">Distancia:</strong> {{ formatDistance(offer.distanceKm) }}</p>
                <p><strong class="text-[var(--app-text-primary)]">Precio:</strong> {{ formatPrice(offer.deliveryPrice) }}</p>
                <p><strong class="text-[var(--app-text-primary)]">Actualizada:</strong> {{ formatExpiresAt(offer.respondedAt || offer.expiresAt) }}</p>
              </div>
            </article>
          </ng-container>

          <article
            *ngIf="!isLoadingHistory() && historyOffers().length === 0"
            class="rounded-2xl border border-dashed border-[var(--app-card-soft-border)] bg-[var(--app-card-soft-bg)] p-6 text-center text-sm text-[var(--auth-text-secondary)]"
          >
            Aun no tienes solicitudes en el historial.
          </article>
        </section>
      </section>

      <app-owner-offer-detail-modal
        [open]="isOfferModalOpen()"
        [detail]="selectedOfferDetail()"
        [isSubmitting]="isOfferActionSubmitting()"
        [showActions]="showOfferActions()"
        [onClose]="closeOfferModal"
        (accept)="acceptSelectedOffer()"
        (reject)="rejectSelectedOffer()"
      />

      <app-offer-mechanic-assignment-modal
        [open]="isMechanicModalOpen()"
        [mechanics]="availableMechanics()"
        [selectedMechanicId]="selectedMechanicId()"
        [isSubmitting]="isOfferActionSubmitting()"
        (openChange)="setMechanicModalOpen($event)"
        (selectedMechanicIdChange)="setSelectedMechanicId($event)"
        (assign)="confirmAcceptWithMechanic()"
      />
    </main>
  `,
})
export class OwnerOrdersPageComponent {
  private readonly destroyRef = inject(DestroyRef);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly repairShopRepository = inject(RepairShopRepository);
  private readonly realtimeOffersRepository = inject(RealtimeOffersRepository);
  private readonly realtimeOffersSocket = inject(RealtimeOffersSocketService);
  private readonly appToast = inject(AppToastService);

  readonly pendingOffers = signal<OwnerPendingOffer[]>([]);
  readonly historyOffers = signal<OwnerOfferHistoryItem[]>([]);
  readonly selectedOfferDetail = signal<OwnerOfferDetail | null>(null);
  readonly isOfferModalOpen = signal(false);
  readonly isMechanicModalOpen = signal(false);
  readonly isOfferActionSubmitting = signal(false);
  readonly showOfferActions = signal(true);
  readonly availableMechanics = signal<ShopMechanicData[]>([]);
  readonly selectedMechanicId = signal<string | null>(null);
  readonly isLoadingOffers = signal(false);
  readonly isLoadingHistory = signal(false);

  constructor() {
    this.loadPendingOffers();
    this.loadOfferHistory();

    const createdSubscription = this.realtimeOffersSocket.offerCreated$.subscribe((offer) => {
      this.mergeIncomingOffer(offer);
    });
    const routeSubscription = this.route.queryParamMap.subscribe((params) => {
      const assignmentId = params.get('offer');
      if (!assignmentId) {
        return;
      }

      void this.openOfferDetailInternal(assignmentId, {
        clearQueryParamOnSuccess: true,
        showActions: true,
      });
    });

    this.destroyRef.onDestroy(() => {
      createdSubscription.unsubscribe();
      routeSubscription.unsubscribe();
    });
  }

  readonly closeOfferModal = (): void => {
    if (this.isOfferActionSubmitting()) {
      return;
    }
    this.isOfferModalOpen.set(false);
    this.isMechanicModalOpen.set(false);
    this.selectedMechanicId.set(null);
  };

  setMechanicModalOpen(open: boolean): void {
    if (this.isOfferActionSubmitting()) {
      return;
    }

    this.isMechanicModalOpen.set(open);
    if (!open) {
      this.selectedMechanicId.set(null);
    }
  }

  setSelectedMechanicId(mechanicId: string): void {
    this.selectedMechanicId.set(mechanicId);
  }

  trackByAssignmentId(_: number, offer: OwnerPendingOffer): string {
    return offer.assignmentId;
  }

  formatDistance(distanceKm: number | null): string {
    return distanceKm === null ? 'No disponible' : `${distanceKm.toFixed(2)} km`;
  }

  formatPrice(price: number | null): string {
    return price === null ? 'No disponible' : `Bs ${price.toFixed(2)}`;
  }

  formatExpiresAt(expiresAt: string | null): string {
    return formatUtcDateToLocal(expiresAt, 'No definido');
  }

  async openOfferDetail(assignmentId: string): Promise<void> {
    await this.openOfferDetailInternal(assignmentId, {
      clearQueryParamOnSuccess: false,
      showActions: true,
    });
  }

  async openAcceptedHistoryDetail(assignmentId: string): Promise<void> {
    await this.openOfferDetailInternal(assignmentId, {
      clearQueryParamOnSuccess: false,
      showActions: false,
    });
  }

  historyStatusLabel(status: string): string {
    if (status === 'expired') {
      return 'Expirada';
    }
    if (status === 'rejected') {
      return 'Rechazada';
    }
    if (status === 'accepted') {
      return 'Aceptada';
    }
    if (status === 'completed') {
      return 'Completada';
    }
    if (status === 'cancelled' || status === 'canceled') {
      return 'Cancelada';
    }
    if (status === 'failed') {
      return 'Fallida';
    }
    if (status === 'pending') {
      return 'Pendiente';
    }
    return status;
  }

  historyStatusClass(status: string): string {
    if (status === 'completed') {
      return 'bg-sky-100 text-sky-800';
    }
    if (status === 'cancelled' || status === 'canceled') {
      return 'bg-slate-200 text-slate-800';
    }
    if (status === 'accepted') {
      return 'bg-emerald-100 text-emerald-800';
    }
    if (status === 'rejected') {
      return 'bg-rose-100 text-rose-800';
    }
    return 'bg-amber-100 text-amber-900';
  }

  private async openOfferDetailInternal(
    assignmentId: string,
    options: { clearQueryParamOnSuccess: boolean; showActions: boolean },
  ): Promise<void> {
    const response = await this.realtimeOffersRepository.getOfferDetail(assignmentId);
    if (!response.ok) {
      this.appToast.showErrorList(response.errors);
      return;
    }

    this.selectedOfferDetail.set(response.data);
    this.showOfferActions.set(options.showActions);
    this.isOfferModalOpen.set(true);

    if (options.clearQueryParamOnSuccess) {
      await this.router.navigate([], {
        relativeTo: this.route,
        queryParams: { offer: null },
        queryParamsHandling: 'merge',
        replaceUrl: true,
      });
    }
  }

  private async loadPendingOffers(): Promise<void> {
    this.isLoadingOffers.set(true);
    const response = await this.realtimeOffersRepository.listMyPendingOffers();
    this.isLoadingOffers.set(false);

    if (!response.ok) {
      this.appToast.showErrorList(response.errors);
      return;
    }

    this.pendingOffers.set(response.data);
  }

  private async loadOfferHistory(): Promise<void> {
    this.isLoadingHistory.set(true);
    const response = await this.realtimeOffersRepository.listMyOfferHistory();
    this.isLoadingHistory.set(false);

    if (!response.ok) {
      this.appToast.showErrorList(response.errors);
      return;
    }

    this.historyOffers.set(response.data);
  }

  private mergeIncomingOffer(offer: OwnerOfferDetail): void {
    this.pendingOffers.update((currentOffers) => {
      const next = currentOffers.filter((item) => item.assignmentId !== offer.assignmentId);
      return [offer, ...next];
    });
  }

  async acceptSelectedOffer(): Promise<void> {
    if (!this.selectedOfferDetail() || this.isOfferActionSubmitting()) {
      return;
    }

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
    this.isMechanicModalOpen.set(true);
  }

  async confirmAcceptWithMechanic(): Promise<void> {
    const detail = this.selectedOfferDetail();
    const mechanicId = this.selectedMechanicId();
    if (!detail || !mechanicId || this.isOfferActionSubmitting()) {
      return;
    }

    this.isOfferActionSubmitting.set(true);
    const response = await this.realtimeOffersRepository.acceptOffer(detail.assignmentId, mechanicId);
    this.isOfferActionSubmitting.set(false);

    if (!response.ok) {
      this.appToast.showErrorList(response.errors);
      return;
    }

    this.appToast.success('Solicitud aceptada correctamente');
    this.isMechanicModalOpen.set(false);
    this.isOfferModalOpen.set(false);
    this.selectedMechanicId.set(null);
    await this.reloadOfferLists();
  }

  async rejectSelectedOffer(): Promise<void> {
    const detail = this.selectedOfferDetail();
    if (!detail || this.isOfferActionSubmitting()) {
      return;
    }

    this.isOfferActionSubmitting.set(true);
    const response = await this.realtimeOffersRepository.rejectOffer(detail.assignmentId);
    this.isOfferActionSubmitting.set(false);

    if (!response.ok) {
      this.appToast.showErrorList(response.errors);
      return;
    }

    this.appToast.info('Solicitud rechazada. Se notificara al siguiente taller en cola.');
    this.isOfferModalOpen.set(false);
    await this.reloadOfferLists();
  }

  private async reloadOfferLists(): Promise<void> {
    await Promise.all([this.loadPendingOffers(), this.loadOfferHistory()]);
  }
}
