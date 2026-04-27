import { Component, computed, inject } from '@angular/core';
import { LucideAngularModule, Wrench } from 'lucide-angular';

import { RepairShopStore } from '../../../../../core/store/repair-shop.store';
import { PrimaryCardComponent } from '../../../../../features/shared/presentation/components/cards/primary-card.component';
import { EditShopInfoTriggerComponent } from './edit-shop-info-trigger.component';

@Component({
  selector: 'app-shop-info-card',
  standalone: true,
  imports: [LucideAngularModule, PrimaryCardComponent, EditShopInfoTriggerComponent],
  template: `
    <app-primary-card variant="default" customClass="space-y-5">
      <header class="flex items-center justify-between gap-3">
        <div>
          <h2 class="text-xl font-semibold text-[var(--auth-text-primary)]">
            Informacion del taller
          </h2>
          <p class="mt-1 text-sm text-[var(--auth-text-secondary)]">
            Gestiona el nombre y la direccion principal de tu taller.
          </p>
        </div>
        <div
          class="grid h-11 w-11 place-items-center rounded-full bg-[var(--app-accent)] text-[var(--app-accent-text)]"
        >
          <lucide-angular [img]="wrenchIcon" [size]="20" />
        </div>
      </header>

      <div
        class="rounded-2xl border border-[var(--app-card-soft-border)] bg-[var(--app-card-soft-bg)] px-4 py-3"
      >
        <p class="text-xs font-medium uppercase tracking-wide text-[var(--app-text-secondary)]">
          Nombre actual
        </p>
        <p class="mt-1 text-sm font-semibold text-[var(--app-text-primary)]">
          {{ currentShopName() }}
        </p>
      </div>

      <div
        class="rounded-2xl border border-[var(--app-card-soft-border)] bg-[var(--app-card-soft-bg)] px-4 py-3"
      >
        <p class="text-xs font-medium uppercase tracking-wide text-[var(--app-text-secondary)]">
          Ubicacion actual
        </p>
        <p class="mt-1 text-sm font-semibold text-[var(--app-text-primary)]">
          {{ currentShopAddress() }}
        </p>
      </div>

      <app-edit-shop-info-trigger />
    </app-primary-card>
  `,
})
export class ShopInfoCardComponent {
  private readonly repairShopStore = inject(RepairShopStore);

  readonly wrenchIcon = Wrench;

  readonly currentShopName = computed(() => this.repairShopStore.shop()?.name ?? 'Mi Taller');
  readonly currentShopAddress = computed(
    () => this.repairShopStore.shop()?.text_address ?? 'Ubicacion de taller',
  );
}
