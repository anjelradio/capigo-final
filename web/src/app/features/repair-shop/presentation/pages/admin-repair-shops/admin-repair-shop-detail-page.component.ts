import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';

import { APP_ROUTES } from '../../../../../core/config/routes';
import { AppToastService } from '../../../../../core/services/app-toast.service';
import { HomeHeaderComponent } from '../../../../home/presentation/components/home-header/home-header.component';
import { CircularProgressLoaderComponent } from '../../../../shared/presentation/components/loaders/circular-progress-loader.component';
import { PageHeadingComponent } from '../../../../shared/presentation/components/layout/page-heading.component';
import { PrimaryCardComponent } from '../../../../shared/presentation/components/cards/primary-card.component';
import { formatUtcDateToLocal } from '../../../../shared/data/infrastructure/date-time';
import type {
  AdminRecentServiceData,
  AdminRepairShopOverviewData,
} from '../../../data/schemas/repair-shop.schema';
import { AdminRepairShopActionsService } from '../../actions/repair-shop/admin-repair-shop-actions.service';

@Component({
  selector: 'app-admin-repair-shop-detail-page',
  standalone: true,
  imports: [
    CommonModule,
    HomeHeaderComponent,
    PageHeadingComponent,
    CircularProgressLoaderComponent,
    PrimaryCardComponent,
  ],
  template: `
    <main class="app-dashboard-bg min-h-screen">
      <app-home-header />

      <section class="mx-auto w-full max-w-[1500px] px-4 pb-10 pt-6 sm:px-6">
        <button
          type="button"
          class="mb-4 inline-flex items-center justify-center rounded-full border border-[var(--app-card-soft-border)] bg-[var(--app-card-soft-bg)] px-4 py-2 text-sm font-semibold text-[var(--app-text-primary)] transition hover:bg-slate-100"
          (click)="goBack()"
        >
          Volver a talleres
        </button>

        <app-page-heading
          [title]="overview()?.shop?.name ?? 'Detalle de taller'"
          [subtitle]="overviewSubtitle()"
        />

        <section *ngIf="isLoading()" class="flex items-center justify-center py-14">
          <app-circular-progress-loader [size]="42" label="Cargando detalle del taller" />
        </section>

        <section *ngIf="!isLoading() && overview() as data" class="mt-6 grid gap-6 lg:grid-cols-2">
          <app-primary-card customClass="h-full space-y-4">
            <header>
              <h3 class="text-xl font-semibold text-[var(--app-text-primary)]">Mecanicos registrados</h3>
              <p class="mt-1 text-sm text-[var(--auth-text-secondary)]">
                Resumen general de vinculaciones del taller.
              </p>
            </header>

            <div>
              <p class="text-xs uppercase tracking-wide text-[var(--auth-text-secondary)]">Total mecanicos</p>
              <div class="mt-3 flex flex-col gap-4 xl:flex-row xl:items-stretch xl:justify-between">
                <div class="rounded-2xl border border-[var(--app-card-soft-border)] bg-[var(--app-card-soft-bg)] px-5 py-4 xl:min-w-[180px]">
                  <p class="text-xs uppercase tracking-wide text-[var(--auth-text-secondary)]">Registrados</p>
                  <p class="mt-1 text-5xl font-bold leading-none text-[var(--app-text-primary)]">
                    {{ data.mechanic_stats.total }}
                  </p>
                </div>

                <div class="grid flex-1 gap-2 text-sm sm:grid-cols-2">
                  <div class="rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-2 font-semibold text-emerald-700">
                    Disponibles: {{ data.mechanic_stats.available }}
                  </div>
                  <div class="rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 font-semibold text-rose-700">
                    No disponibles: {{ data.mechanic_stats.unavailable }}
                  </div>
                  <div class="rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-2 font-semibold text-emerald-700">
                    Activos: {{ data.mechanic_stats.active_records }}
                  </div>
                  <div class="rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 font-semibold text-rose-700">
                    Inactivos: {{ data.mechanic_stats.inactive_records }}
                  </div>
                </div>
              </div>
            </div>

            <div class="pt-2">
              <button
                type="button"
                class="inline-flex h-11 items-center justify-center rounded-full bg-[var(--app-accent)] px-5 text-sm font-semibold text-[var(--app-accent-text)] transition hover:brightness-105"
                (click)="goToMechanics()"
              >
                Administrar
              </button>
            </div>
          </app-primary-card>

          <app-primary-card customClass="h-full space-y-4">
            <header>
              <h3 class="text-xl font-semibold text-[var(--app-text-primary)]">Acciones</h3>
              <p class="mt-1 text-sm text-[var(--auth-text-secondary)]">
                Bitacora preliminar del taller (vista temporal).
              </p>
            </header>

            <div class="grid gap-2 text-sm text-[var(--auth-text-secondary)]">
              <p>Usuario propietario inicio sesion correctamente.</p>
              <p>Un servicio fue finalizado en plataforma.</p>
              <p>Actualizacion reciente de perfil del taller.</p>
            </div>

            <div class="pt-2">
              <button
                type="button"
                class="inline-flex h-11 items-center justify-center rounded-full border border-[var(--app-card-soft-border)] bg-[var(--app-card-soft-bg)] px-5 text-sm font-semibold text-[var(--app-text-primary)] transition hover:bg-slate-100"
                (click)="appToast.info('Bitacora completa: proxima fase.')"
              >
                Ver bitacora
              </button>
            </div>
          </app-primary-card>
        </section>

        <section class="mt-8 space-y-4">
          <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <h3 class="text-base font-semibold uppercase tracking-wide text-[var(--app-accent)]">
              ULTIMOS SERVICIOS REALIZADOS
            </h3>
            <button
              type="button"
              class="inline-flex h-10 items-center justify-center rounded-full border border-[var(--app-card-soft-border)] bg-[var(--app-card-soft-bg)] px-4 text-xs font-semibold uppercase tracking-wide text-[var(--app-text-primary)] transition hover:bg-slate-100"
              (click)="appToast.info('La vista completa de registros estara disponible en la siguiente fase.')"
            >
              Ver todos los registros
            </button>
          </div>

          <app-primary-card customClass="space-y-4 min-h-[220px]">
            <div *ngIf="isLoadingRecentServices()" class="flex items-center justify-center py-8">
              <app-circular-progress-loader [size]="40" label="Cargando ultimos servicios" />
            </div>

            <div
              *ngIf="!isLoadingRecentServices() && recentServices().length === 0"
              class="rounded-xl border border-dashed border-[var(--app-card-soft-border)] bg-[var(--app-card-soft-bg)] p-4 text-sm text-[var(--auth-text-secondary)]"
            >
              Aun no hay servicios aceptados registrados para este taller.
            </div>

            <div *ngIf="!isLoadingRecentServices() && recentServices().length > 0" class="overflow-x-auto">
              <table class="min-w-full text-left text-sm">
                <thead>
                  <tr
                    class="border-b border-[var(--app-card-soft-border)] text-xs uppercase tracking-wide text-[var(--auth-text-secondary)]"
                  >
                    <th class="px-2 py-2">Problema</th>
                    <th class="px-2 py-2">Incidente</th>
                    <th class="px-2 py-2">Estado incidente</th>
                    <th class="px-2 py-2">Mecanico</th>
                    <th class="px-2 py-2">Fecha</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    *ngFor="let service of recentServices(); trackBy: trackByRecentService"
                    class="border-b border-[var(--app-card-soft-border)]/60"
                  >
                    <td class="px-2 py-3 font-medium text-[var(--app-text-primary)]">
                      {{ service.problem_name || 'Sin clasificacion' }}
                    </td>
                    <td class="px-2 py-3 text-[var(--auth-text-secondary)]">
                      <p
                        class="max-w-[340px] leading-5"
                        style="display: -webkit-box; overflow: hidden; -webkit-box-orient: vertical; -webkit-line-clamp: 2;"
                      >
                        {{ service.incident_description || 'Sin descripcion' }}
                      </p>
                    </td>
                    <td class="px-2 py-3">
                      <span
                        class="inline-flex rounded-full px-3 py-1 text-xs font-semibold"
                        [ngClass]="incidentStatusClass(service.incident_status)"
                      >
                        {{ incidentStatusLabel(service.incident_status) }}
                      </span>
                    </td>
                    <td class="px-2 py-3 text-[var(--auth-text-secondary)]">
                      {{ service.mechanic_name || 'Sin asignar' }}
                    </td>
                    <td class="px-2 py-3 text-[var(--auth-text-secondary)]">
                      {{ formatDate(service.accepted_at || service.created_date) }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </app-primary-card>
        </section>
      </section>
    </main>
  `,
})
export class AdminRepairShopDetailPageComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  readonly appToast = inject(AppToastService);
  private readonly adminRepairShopActions = inject(AdminRepairShopActionsService);

  readonly isLoading = signal(false);
  readonly overview = signal<AdminRepairShopOverviewData | null>(null);
  readonly recentServices = signal<AdminRecentServiceData[]>([]);
  readonly isLoadingRecentServices = signal(false);

  constructor() {
    void this.loadOverview();
  }

  overviewSubtitle(): string {
    const shop = this.overview()?.shop;
    if (!shop) {
      return 'Resumen general del taller seleccionado.';
    }

    return `${shop.text_address} | Owner: ${shop.owner_name} | Creado: ${formatUtcDateToLocal(shop.created_date)}`;
  }

  async goBack(): Promise<void> {
    await this.router.navigateByUrl(APP_ROUTES.APP_ADMIN_REPAIR_SHOPS);
  }

  async goToMechanics(): Promise<void> {
    const currentShopId = this.overview()?.shop.id;
    if (!currentShopId) {
      return;
    }

    await this.router.navigateByUrl(`${APP_ROUTES.APP_ADMIN_REPAIR_SHOPS}/${currentShopId}/mechanics`);
  }

  trackByRecentService(_: number, service: AdminRecentServiceData): string {
    return service.assignment_id;
  }

  formatDate(value: string | null | undefined): string {
    return formatUtcDateToLocal(value);
  }

  incidentStatusLabel(status: string): string {
    if (status === 'completed') {
      return 'Completado';
    }
    if (status === 'cancelled') {
      return 'Cancelado';
    }
    if (status === 'assigned') {
      return 'Asignado';
    }
    if (status === 'on_the_way') {
      return 'En camino';
    }
    if (status === 'arrived') {
      return 'Llegado';
    }
    if (status === 'failed') {
      return 'Fallido';
    }
    if (status === 'searching_shop') {
      return 'Buscando taller';
    }
    if (status === 'classified') {
      return 'Clasificado';
    }
    if (status === 'classifying') {
      return 'Clasificando';
    }
    if (status === 'pending') {
      return 'Pendiente';
    }
    return status;
  }

  incidentStatusClass(status: string): string {
    if (status === 'completed') {
      return 'bg-emerald-100 text-emerald-800';
    }
    if (status === 'cancelled' || status === 'failed') {
      return 'bg-rose-100 text-rose-800';
    }
    if (status === 'assigned' || status === 'on_the_way' || status === 'arrived') {
      return 'bg-sky-100 text-sky-800';
    }
    return 'bg-slate-200 text-slate-700';
  }

  private async loadOverview(): Promise<void> {
    const shopId = this.route.snapshot.paramMap.get('shopId');
    if (!shopId) {
      this.appToast.error('No se pudo identificar el taller seleccionado.');
      await this.goBack();
      return;
    }

    this.isLoading.set(true);
    const response = await this.adminRepairShopActions.getShopOverview(shopId);
    this.isLoading.set(false);

    if (!response.ok) {
      this.appToast.showErrorList(response.errors);
      await this.goBack();
      return;
    }

    this.overview.set(response.data);

    this.isLoadingRecentServices.set(true);
    const recentServicesResponse = await this.adminRepairShopActions.listRecentServices(shopId);
    this.isLoadingRecentServices.set(false);

    if (!recentServicesResponse.ok) {
      this.appToast.showErrorList(recentServicesResponse.errors);
      return;
    }

    this.recentServices.set(recentServicesResponse.data);
  }
}
