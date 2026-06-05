import { CommonModule } from '@angular/common';
import { Component, DestroyRef, inject, signal } from '@angular/core';
import { Router } from '@angular/router';

import { AppToastService } from '../../../../../core/services/app-toast.service';
import { RealtimeOffersRepository } from '../../../../../features/realtime/data/repositories/realtime-offers.repository';
import { RealtimeOffersSocketService } from '../../../../../features/realtime/presentation/services/realtime-offers-socket.service';
import { formatUtcDateToLocal } from '../../../../../features/shared/data/infrastructure/date-time';
import type {
  OwnerAssignmentItem,
} from '../../../../../features/realtime/domain/entities/owner-offer';
import { APP_ROUTES } from '../../../../../core/config/routes';
import { CircularProgressLoaderComponent } from '../../../../../features/shared/presentation/components/loaders/circular-progress-loader.component';
import { PageHeadingComponent } from '../../../../../features/shared/presentation/components/layout/page-heading.component';
import { HomeHeaderComponent } from '../../components/home-header/home-header.component';

@Component({
  selector: 'app-owner-assignments-page',
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
        <app-page-heading title="Asignaciones" subtitle="Revisa las asignaciones aceptadas, completadas y canceladas." />

        <section class="mt-6 grid gap-4">
          <div *ngIf="isLoading()" class="flex items-center justify-center py-8">
            <app-circular-progress-loader [size]="40" label="Cargando asignaciones" />
          </div>

          <ng-container *ngIf="!isLoading()">
            <article
              *ngFor="let assignment of assignments(); trackBy: trackByAssignment"
              class="rounded-2xl border border-[var(--app-card-soft-border)] bg-[var(--app-card-bg)] p-5 shadow-sm"
            >
              <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p class="text-xs uppercase tracking-wide text-[var(--auth-text-secondary)]">Asignacion</p>
                  <h4 class="text-lg font-semibold text-[var(--app-text-primary)]">
                    {{ assignment.problemName || 'Incidente clasificado' }}
                  </h4>
                  <p class="mt-1 text-sm text-[var(--auth-text-secondary)]">
                    {{ assignment.incidentDescription || 'Sin descripcion' }}
                  </p>
                </div>

                <div class="flex items-center gap-2">
                  <span class="inline-flex rounded-full px-3 py-1 text-xs font-semibold" [ngClass]="statusClass(assignment.status)">
                    {{ statusLabel(assignment.status) }}
                  </span>
                  <button
                    *ngIf="canDownloadReport(assignment.status)"
                    type="button"
                    class="inline-flex items-center justify-center rounded-full border border-[var(--app-card-soft-border)] bg-[var(--app-card-soft-bg)] px-4 py-2 text-sm font-semibold text-[var(--app-text-primary)] transition hover:brightness-105 disabled:opacity-60"
                    [disabled]="downloadingAssignmentId() === assignment.assignmentId"
                    (click)="downloadServiceReport(assignment)"
                  >
                    {{ downloadingAssignmentId() === assignment.assignmentId ? 'Descargando...' : 'Descargar reporte' }}
                  </button>
                  <button
                    type="button"
                    class="inline-flex items-center justify-center rounded-full bg-[var(--app-accent)] px-4 py-2 text-sm font-semibold text-[var(--app-accent-text)] transition hover:brightness-105"
                    (click)="handleAssignmentAction(assignment)"
                  >
                    {{ actionLabel(assignment.status) }}
                  </button>
                </div>
              </div>

              <div class="mt-4 grid gap-2 text-sm text-[var(--auth-text-secondary)] sm:grid-cols-2 lg:grid-cols-5">
                <p><strong class="text-[var(--app-text-primary)]">Mecanico:</strong> {{ assignment.mechanicName || 'Sin asignar' }}</p>
                <p><strong class="text-[var(--app-text-primary)]">Distancia:</strong> {{ formatDistance(assignment.distanceKm) }}</p>
                <p><strong class="text-[var(--app-text-primary)]">Precio:</strong> {{ formatPrice(assignment.deliveryPrice) }}</p>
                <p class="lg:col-span-2"><strong class="text-[var(--app-text-primary)]">Fecha:</strong> {{ formatDate(assignment.createdAt) }}</p>
              </div>
            </article>
          </ng-container>

          <article
            *ngIf="!isLoading() && assignments().length === 0"
            class="rounded-2xl border border-dashed border-[var(--app-card-soft-border)] bg-[var(--app-card-soft-bg)] p-6 text-center text-sm text-[var(--auth-text-secondary)]"
          >
            No tienes asignaciones por ahora.
          </article>
        </section>
      </section>

    </main>
  `,
})
export class OwnerAssignmentsPageComponent {
  private readonly destroyRef = inject(DestroyRef);
  private readonly offersRepository = inject(RealtimeOffersRepository);
  private readonly realtimeOffersSocket = inject(RealtimeOffersSocketService);
  private readonly appToast = inject(AppToastService);
  private readonly router = inject(Router);

  readonly assignments = signal<OwnerAssignmentItem[]>([]);
  readonly isLoading = signal(false);
  readonly downloadingAssignmentId = signal<string | null>(null);

  constructor() {
    void this.loadAssignments();

    const statusChangedSubscription = this.realtimeOffersSocket.offerStatusChanged$.subscribe(() => {
      void this.loadAssignments();
    });

    this.destroyRef.onDestroy(() => {
      statusChangedSubscription.unsubscribe();
    });
  }

  trackByAssignment(_: number, assignment: OwnerAssignmentItem): string {
    return assignment.assignmentId;
  }

  statusLabel(status: string): string {
    if (status === 'accepted') {
      return 'Aceptada';
    }
    if (status === 'completed') {
      return 'Completada';
    }
    return 'Cancelada';
  }

  statusClass(status: string): string {
    if (status === 'accepted') {
      return 'bg-emerald-100 text-emerald-800';
    }
    if (status === 'completed') {
      return 'bg-slate-200 text-slate-700';
    }
    return 'bg-rose-100 text-rose-800';
  }

  formatDistance(distanceKm: number | null): string {
    return distanceKm === null ? 'No disponible' : `${distanceKm.toFixed(2)} km`;
  }

  formatPrice(price: number | null): string {
    return price === null ? 'No disponible' : `Bs ${price.toFixed(2)}`;
  }

  formatDate(value: string): string {
    return formatUtcDateToLocal(value);
  }

  actionLabel(status: string): string {
    return status === 'accepted' ? 'Monitorear' : 'Ver detalle';
  }

  canDownloadReport(status: string): boolean {
    return status === 'completed';
  }

  async handleAssignmentAction(assignment: OwnerAssignmentItem): Promise<void> {
    await this.router.navigate([APP_ROUTES.APP_OWNER_ASSIGNMENTS, assignment.assignmentId, 'detail']);
  }

  async downloadServiceReport(assignment: OwnerAssignmentItem): Promise<void> {
    this.downloadingAssignmentId.set(assignment.assignmentId);
    const response = await this.offersRepository.downloadServiceReportPdf(assignment.assignmentId);
    this.downloadingAssignmentId.set(null);

    if (!response.ok) {
      this.appToast.showErrorList(response.errors);
      return;
    }

    const blobUrl = window.URL.createObjectURL(response.data);
    const link = document.createElement('a');
    link.href = blobUrl;
    link.download = `reporte-servicio-${assignment.incidentId}.pdf`;
    link.click();
    window.URL.revokeObjectURL(blobUrl);
  }

  private async loadAssignments(): Promise<void> {
    this.isLoading.set(true);
    const response = await this.offersRepository.listMyAssignments();
    this.isLoading.set(false);

    if (!response.ok) {
      this.appToast.showErrorList(response.errors);
      return;
    }

    this.assignments.set(response.data);
  }
}
