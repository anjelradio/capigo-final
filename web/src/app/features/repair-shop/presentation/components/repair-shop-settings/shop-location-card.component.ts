import { Component, computed, inject } from '@angular/core';
import { LucideAngularModule, MapPinned } from 'lucide-angular';

import { RepairShopStore } from '../../../../../core/store/repair-shop.store';
import { PrimaryCardComponent } from '../../../../../features/shared/presentation/components/cards/primary-card.component';
import { EditShopLocationTriggerComponent } from './edit-shop-location-trigger.component';

@Component({
  selector: 'app-shop-location-card',
  standalone: true,
  imports: [LucideAngularModule, PrimaryCardComponent, EditShopLocationTriggerComponent],
  template: `
    <app-primary-card
      variant="default"
      backgroundClass="bg-[var(--dashboard-card-soft-blue)]"
      customClass="space-y-4"
    >
      <header class="flex items-start justify-between gap-3">
        <div>
          <h2 class="text-xl font-semibold text-[var(--auth-text-primary)]">
            Ubicacion del taller
          </h2>
          <p class="mt-1 text-sm text-[var(--auth-text-secondary)]">
            Ajusta la ubicacion del taller cuando sea necesario.
          </p>
        </div>
        <div
          class="grid h-11 w-11 place-items-center rounded-full bg-[var(--app-accent)] text-[var(--app-accent-text)]"
        >
          <lucide-angular [img]="mapIcon" [size]="20" />
        </div>
      </header>

      <div
        class="rounded-2xl border border-[var(--app-card-soft-border)] bg-[var(--app-card-soft-bg)] px-4 py-3 text-sm text-[var(--app-text-secondary)]"
      >
        <p class="text-xs font-medium uppercase tracking-wide text-[var(--app-text-secondary)]">
          Ubicacion actual
        </p>
        <p class="mt-1 font-semibold text-[var(--app-text-primary)]">{{ currentShopAddress() }}</p>
      </div>

      <app-edit-shop-location-trigger />
    </app-primary-card>
  `,
})
export class ShopLocationCardComponent {
  private readonly repairShopStore = inject(RepairShopStore);

  readonly mapIcon = MapPinned;

  readonly currentShopAddress = computed(
    () => this.repairShopStore.shop()?.text_address ?? 'Ubicacion de taller',
  );
}
