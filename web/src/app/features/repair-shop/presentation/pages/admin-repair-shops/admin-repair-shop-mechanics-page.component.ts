import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';

import { APP_ROUTES } from '../../../../../core/config/routes';
import { AppToastService } from '../../../../../core/services/app-toast.service';
import { HomeHeaderComponent } from '../../../../home/presentation/components/home-header/home-header.component';
import { formatUtcDateToLocal } from '../../../../shared/data/infrastructure/date-time';
import { PrimaryCardComponent } from '../../../../shared/presentation/components/cards/primary-card.component';
import { CircularProgressLoaderComponent } from '../../../../shared/presentation/components/loaders/circular-progress-loader.component';
import { PageHeadingComponent } from '../../../../shared/presentation/components/layout/page-heading.component';
import type {
  AdminRepairShopData,
  ShopMechanicData,
} from '../../../data/schemas/repair-shop.schema';
import { AdminRepairShopActionsService } from '../../actions/repair-shop/admin-repair-shop-actions.service';
import { DeleteShopMechanicTriggerComponent } from '../../components/shop-mechanics/delete-shop-mechanic-trigger.component';

@Component({
  selector: 'app-admin-repair-shop-mechanics-page',
  standalone: true,
  imports: [
    CommonModule,
    HomeHeaderComponent,
    PageHeadingComponent,
    PrimaryCardComponent,
    CircularProgressLoaderComponent,
    DeleteShopMechanicTriggerComponent,
  ],
  template: `
    <main class="app-dashboard-bg min-h-screen">
      <app-home-header />

      <section class="mx-auto w-full max-w-[1500px] px-4 pb-10 pt-6 sm:px-6">
        <button
          type="button"
          class="mb-4 inline-flex items-center justify-center rounded-full border border-[var(--app-card-soft-border)] bg-[var(--app-card-soft-bg)] px-4 py-2 text-sm font-semibold text-[var(--app-text-primary)] transition hover:bg-slate-100"
          (click)="goBackToDetail()"
        >
          Volver al detalle
        </button>

        <app-page-heading [title]="'Mecanicos del taller'" [subtitle]="pageSubtitle()" />

        <section class="mt-6">
          <app-primary-card customClass="space-y-4 min-h-[220px]">
            <div *ngIf="isLoading()" class="flex items-center justify-center py-8">
              <app-circular-progress-loader [size]="40" label="Cargando mecanicos" />
            </div>

            <div
              *ngIf="!isLoading() && mechanics().length === 0"
              class="rounded-xl border border-dashed border-[var(--app-card-soft-border)] bg-[var(--app-card-soft-bg)] p-4 text-sm text-[var(--auth-text-secondary)]"
            >
              No hay mecanicos vinculados en este taller.
            </div>

            <div *ngIf="!isLoading() && mechanics().length > 0" class="overflow-x-auto">
              <table class="min-w-full text-left text-sm">
                <thead>
                  <tr class="border-b border-[var(--app-card-soft-border)] text-xs uppercase tracking-wide text-[var(--auth-text-secondary)]">
                    <th class="px-2 py-2">Nombre</th>
                    <th class="px-2 py-2">Apellido</th>
                    <th class="px-2 py-2">Telefono</th>
                    <th class="px-2 py-2">Correo</th>
                    <th class="px-2 py-2">Union</th>
                    <th class="px-2 py-2">Estado</th>
                    <th class="px-2 py-2">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    *ngFor="let mechanic of mechanics(); trackBy: trackByMechanic"
                    class="border-b border-[var(--app-card-soft-border)]/60"
                  >
                    <td class="px-2 py-3 font-medium text-[var(--app-text-primary)]">{{ mechanic.user.first_name }}</td>
                    <td class="px-2 py-3 text-[var(--app-text-primary)]">{{ mechanic.user.last_name }}</td>
                    <td class="px-2 py-3 text-[var(--auth-text-secondary)]">{{ mechanic.user.phone }}</td>
                    <td class="px-2 py-3 text-[var(--auth-text-secondary)]">{{ mechanic.user.email }}</td>
                    <td class="px-2 py-3 text-[var(--auth-text-secondary)]">
                      {{ formatDate(mechanic.created_date) }}
                    </td>
                    <td class="px-2 py-3">
                      <span
                        class="inline-flex rounded-full px-3 py-1 text-xs font-semibold"
                        [ngClass]="mechanic.is_available ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-200 text-slate-700'"
                      >
                        {{ mechanic.is_available ? 'Disponible' : 'No disponible' }}
                      </span>
                    </td>
                    <td class="px-2 py-3">
                      <app-delete-shop-mechanic-trigger
                        [mechanicId]="mechanic.id"
                        [mechanicName]="mechanic.user.first_name + ' ' + mechanic.user.last_name"
                        [shopId]="shopId()"
                        [isAdminContext]="true"
                        (deleted)="reloadMechanics()"
                      />
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
export class AdminRepairShopMechanicsPageComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly adminRepairShopActions = inject(AdminRepairShopActionsService);
  private readonly appToast = inject(AppToastService);

  readonly shopId = signal('');
  readonly shop = signal<AdminRepairShopData | null>(null);
  readonly mechanics = signal<ShopMechanicData[]>([]);
  readonly isLoading = signal(false);

  constructor() {
    void this.initialize();
  }

  trackByMechanic(_: number, mechanic: ShopMechanicData): string {
    return mechanic.id;
  }

  formatDate(value: string): string {
    return formatUtcDateToLocal(value);
  }

  pageSubtitle(): string {
    const currentShop = this.shop();
    if (!currentShop) {
      return 'Listado de mecanicos vinculados al taller.';
    }
    return `${currentShop.name} | ${currentShop.text_address}`;
  }

  async goBackToDetail(): Promise<void> {
    const currentShopId = this.shopId();
    if (!currentShopId) {
      await this.router.navigateByUrl(APP_ROUTES.APP_ADMIN_REPAIR_SHOPS);
      return;
    }

    await this.router.navigateByUrl(`${APP_ROUTES.APP_ADMIN_REPAIR_SHOPS}/${currentShopId}`);
  }

  async reloadMechanics(): Promise<void> {
    const currentShopId = this.shopId();
    if (!currentShopId) {
      return;
    }

    this.isLoading.set(true);
    const response = await this.adminRepairShopActions.listShopMechanics(currentShopId);
    this.isLoading.set(false);

    if (!response.ok) {
      this.appToast.showErrorList(response.errors);
      return;
    }

    this.mechanics.set(response.data);
  }

  private async initialize(): Promise<void> {
    const routeShopId = this.route.snapshot.paramMap.get('shopId');
    if (!routeShopId) {
      this.appToast.error('No se pudo identificar el taller seleccionado.');
      await this.router.navigateByUrl(APP_ROUTES.APP_ADMIN_REPAIR_SHOPS);
      return;
    }

    this.shopId.set(routeShopId);

    this.isLoading.set(true);
    const [overviewResponse, mechanicsResponse] = await Promise.all([
      this.adminRepairShopActions.getShopOverview(routeShopId),
      this.adminRepairShopActions.listShopMechanics(routeShopId),
    ]);
    this.isLoading.set(false);

    if (!overviewResponse.ok) {
      this.appToast.showErrorList(overviewResponse.errors);
      await this.router.navigateByUrl(APP_ROUTES.APP_ADMIN_REPAIR_SHOPS);
      return;
    }

    if (!mechanicsResponse.ok) {
      this.appToast.showErrorList(mechanicsResponse.errors);
      return;
    }

    this.shop.set(overviewResponse.data.shop);
    this.mechanics.set(mechanicsResponse.data);
  }
}
