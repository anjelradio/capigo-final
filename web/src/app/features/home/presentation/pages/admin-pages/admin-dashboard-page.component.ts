import { Component, inject, signal } from '@angular/core';
import { Router } from '@angular/router';

import { AppToastService } from '../../../../../core/services/app-toast.service';
import { APP_ROUTES } from '../../../../../core/config/routes';
import { HomeHeaderComponent } from '../../components/home-header/home-header.component';
import type { AdminRepairShopData } from '../../../../repair-shop/data/schemas/repair-shop.schema';
import { AdminRepairShopActionsService } from '../../../../repair-shop/presentation/actions/repair-shop/admin-repair-shop-actions.service';
import { AdminRepairShopsListComponent } from '../../../../repair-shop/presentation/components/admin-repair-shops/admin-repair-shops-list.component';
import { PageHeadingComponent } from '../../../../shared/presentation/components/layout/page-heading.component';

@Component({
  selector: 'app-admin-dashboard-page',
  standalone: true,
  imports: [HomeHeaderComponent, PageHeadingComponent, AdminRepairShopsListComponent],
  template: `
    <main class="app-dashboard-bg min-h-screen">
      <app-home-header />

      <section class="mx-auto w-full max-w-[1500px] px-4 pb-10 pt-6 sm:px-6">
        <app-page-heading
          title="Bienvenido, administrador"
          subtitle="Aqui puedes gestionar todos los talleres registrados, tanto activos como inactivos."
        />

        <app-admin-repair-shops-list
          [shops]="shops()"
          [isLoading]="isLoading()"
          (viewDetail)="onViewDetail($event)"
        />
      </section>
    </main>
  `,
})
export class AdminDashboardPageComponent {
  private readonly adminRepairShopActions = inject(AdminRepairShopActionsService);
  private readonly appToast = inject(AppToastService);
  private readonly router = inject(Router);

  readonly shops = signal<AdminRepairShopData[]>([]);
  readonly isLoading = signal(false);

  constructor() {
    void this.loadShops();
  }

  async onViewDetail(shopId: string): Promise<void> {
    await this.router.navigateByUrl(`${APP_ROUTES.APP_ADMIN_REPAIR_SHOPS}/${shopId}`);
  }

  private async loadShops(): Promise<void> {
    this.isLoading.set(true);
    const response = await this.adminRepairShopActions.listAllShops();
    this.isLoading.set(false);

    if (!response.ok) {
      this.appToast.showErrorList(response.errors);
      return;
    }

    this.shops.set(response.data);
  }
}
