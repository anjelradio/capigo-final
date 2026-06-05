import { CommonModule } from '@angular/common';
import { Component, DestroyRef, inject, signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';

import { APP_ROUTES } from '../../../../../core/config/routes';
import { AppToastService } from '../../../../../core/services/app-toast.service';
import { RealtimeOffersRepository } from '../../../../../features/realtime/data/repositories/realtime-offers.repository';
import type {
  OwnerOfferHistoryItem,
  OwnerPendingOffer,
} from '../../../../../features/realtime/domain/entities/owner-offer';
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
                <p><strong class="text-[var(--app-text-primary)]">Delivery:</strong> {{ formatPrice(offer.deliveryPrice) }}</p>
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
                    type="button"
                    class="inline-flex items-center justify-center rounded-full bg-[var(--app-accent)] px-4 py-2 text-sm font-semibold text-[var(--app-accent-text)] transition hover:brightness-105"
                    (click)="openOfferDetail(offer.assignmentId)"
                  >
                    Ver detalle
                  </button>
                </div>
              </div>

              <div class="mt-4 grid gap-2 text-sm text-[var(--auth-text-secondary)] sm:grid-cols-3">
                <p><strong class="text-[var(--app-text-primary)]">Distancia:</strong> {{ formatDistance(offer.distanceKm) }}</p>
                <p><strong class="text-[var(--app-text-primary)]">Delivery:</strong> {{ formatPrice(offer.deliveryPrice) }}</p>
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
    </main>
  `,
})
export class OwnerOrdersPageComponent {
  private readonly destroyRef = inject(DestroyRef);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly realtimeOffersRepository = inject(RealtimeOffersRepository);
  private readonly realtimeOffersSocket = inject(RealtimeOffersSocketService);
  private readonly appToast = inject(AppToastService);

  readonly pendingOffers = signal<OwnerPendingOffer[]>([]);
  readonly historyOffers = signal<OwnerOfferHistoryItem[]>([]);
  readonly isLoadingOffers = signal(false);
  readonly isLoadingHistory = signal(false);

  constructor() {
    this.loadPendingOffers();
    this.loadOfferHistory();

    const createdSubscription = this.realtimeOffersSocket.offerCreated$.subscribe((offer) => {
      this.mergeIncomingOffer(offer);
    });
    const statusChangedSubscription = this.realtimeOffersSocket.offerStatusChanged$.subscribe((event) => {
      this.handleOfferStatusChanged(event.assignmentId, event.status);
    });
    const routeSubscription = this.route.queryParamMap.subscribe((params) => {
      const assignmentId = params.get('offer');
      if (!assignmentId) return;
      void this.router.navigate([APP_ROUTES.APP_OWNER_ASSIGNMENTS, assignmentId, 'detail']);
    });

    this.destroyRef.onDestroy(() => {
      createdSubscription.unsubscribe();
      statusChangedSubscription.unsubscribe();
      routeSubscription.unsubscribe();
    });
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
    await this.router.navigate([APP_ROUTES.APP_OWNER_ASSIGNMENTS, assignmentId, 'detail']);
  }

  historyStatusLabel(status: string): string {
    if (status === 'offered') return 'Ofertada';
    if (status === 'expired') return 'Expirada';
    if (status === 'rejected') return 'Rechazada';
    if (status === 'accepted') return 'Aceptada';
    if (status === 'completed') return 'Completada';
    if (status === 'cancelled' || status === 'canceled') return 'Cancelada';
    if (status === 'failed') return 'Fallida';
    if (status === 'pending') return 'Pendiente';
    return status;
  }

  historyStatusClass(status: string): string {
    if (status === 'offered') return 'bg-indigo-100 text-indigo-800';
    if (status === 'completed') return 'bg-sky-100 text-sky-800';
    if (status === 'cancelled' || status === 'canceled') return 'bg-slate-200 text-slate-800';
    if (status === 'accepted') return 'bg-emerald-100 text-emerald-800';
    if (status === 'rejected') return 'bg-rose-100 text-rose-800';
    return 'bg-amber-100 text-amber-900';
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

  private mergeIncomingOffer(offer: OwnerPendingOffer): void {
    this.pendingOffers.update((currentOffers) => {
      const next = currentOffers.filter((item) => item.assignmentId !== offer.assignmentId);
      return [offer, ...next];
    });
  }

  private handleOfferStatusChanged(assignmentId: string, status: string): void {
    this.pendingOffers.update((currentOffers) =>
      currentOffers.filter((item) => item.assignmentId !== assignmentId),
    );

    const normalizedStatus = status.trim().toLowerCase();
    if (normalizedStatus === 'accepted' || normalizedStatus === 'rejected') {
      void this.loadOfferHistory();
      return;
    }
    void this.loadPendingOffers();
  }
}
