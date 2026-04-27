import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';

import { AppToastService } from '../../../../../core/services/app-toast.service';
import { RepairShopActionsService } from '../../actions/repair-shop/repair-shop-actions.service';
import type { ShopMechanicData } from '../../../data/schemas/repair-shop.schema';
import { PrimaryCardComponent } from '../../../../shared/presentation/components/cards/primary-card.component';
import { CircularProgressLoaderComponent } from '../../../../shared/presentation/components/loaders/circular-progress-loader.component';
import { DeleteShopMechanicTriggerComponent } from './delete-shop-mechanic-trigger.component';

@Component({
  selector: 'app-shop-mechanics-list-card',
  standalone: true,
  imports: [
    CommonModule,
    PrimaryCardComponent,
    DeleteShopMechanicTriggerComponent,
    CircularProgressLoaderComponent,
  ],
  template: `
    <section class="space-y-4">
      <header class="flex items-center justify-between">
        <h2 class="text-xl font-semibold uppercase tracking-wide text-[var(--app-accent)]">Mecanicos vinculados</h2>
      </header>

      <app-primary-card variant="default" customClass="min-h-[220px] space-y-4">

        <div *ngIf="isLoading()" class="flex items-center justify-center py-8">
          <app-circular-progress-loader [size]="40" label="Cargando mecanicos" />
        </div>

        <div
          *ngIf="!isLoading() && mechanics().length === 0"
          class="rounded-xl border border-dashed border-[var(--app-card-soft-border)] bg-[var(--app-card-soft-bg)] p-4 text-sm text-[var(--auth-text-secondary)]"
        >
          No hay mecanicos vinculados aun.
        </div>

        <div *ngIf="!isLoading() && mechanics().length > 0" class="overflow-x-auto">
          <table class="min-w-full text-left text-sm">
            <thead>
              <tr class="border-b border-[var(--app-card-soft-border)] text-xs uppercase tracking-wide text-[var(--auth-text-secondary)]">
                <th class="px-2 py-2">Nombre</th>
                <th class="px-2 py-2">Apellido</th>
                <th class="px-2 py-2">Telefono</th>
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
                    (deleted)="reloadMechanics()"
                  />
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </app-primary-card>
    </section>
  `,
})
export class ShopMechanicsListCardComponent implements OnInit {
  private readonly repairShopActions = inject(RepairShopActionsService);
  private readonly appToast = inject(AppToastService);

  readonly mechanics = signal<ShopMechanicData[]>([]);
  readonly isLoading = signal(false);

  ngOnInit(): void {
    void this.loadMechanics();
  }

  trackByMechanic(_: number, mechanic: ShopMechanicData): string {
    return mechanic.id;
  }

  async reloadMechanics(): Promise<void> {
    this.isLoading.set(true);
    const response = await this.repairShopActions.listMyShopMechanics(false);
    this.isLoading.set(false);

    if (!response.ok) {
      this.appToast.showErrorList(response.errors);
      return;
    }

    this.mechanics.set(response.data);
  }

  private async loadMechanics(): Promise<void> {
    await this.reloadMechanics();
  }
}
