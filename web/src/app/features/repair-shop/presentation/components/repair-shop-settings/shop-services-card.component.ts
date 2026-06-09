import { CommonModule } from '@angular/common';
import { Component, OnInit, computed, inject, signal } from '@angular/core';

import { AppToastService } from '../../../../../core/services/app-toast.service';
import { PrimaryCardComponent } from '../../../../../features/shared/presentation/components/cards/primary-card.component';
import { CircularProgressLoaderComponent } from '../../../../../features/shared/presentation/components/loaders/circular-progress-loader.component';
import type { ServiceData } from '../../../data/schemas/repair-shop.schema';
import { RepairShopActionsService } from '../../actions/repair-shop/repair-shop-actions.service';

@Component({
  selector: 'app-shop-services-card',
  standalone: true,
  imports: [CommonModule, PrimaryCardComponent, CircularProgressLoaderComponent],
  template: `
    <app-primary-card
        variant="default"
        customClass="relative h-full space-y-5 overflow-hidden"
      >
        <img
          src="/images/capis/capi-1.webp"
          alt="Capigo"
          class="pointer-events-none absolute -bottom-6 -right-2 hidden h-auto w-[270px] select-none lg:block"
        />

        <header class="relative z-10">
          <h2 class="text-xl font-semibold text-[var(--auth-text-primary)]">Servicios del taller</h2>
          <p class="mt-1 text-sm text-[var(--auth-text-secondary)]">
            Estos son los servicios que actualmente aparecen en tu perfil.
          </p>
        </header>

        <div
          *ngIf="isLoading()"
          class="relative z-10 rounded-2xl border border-[var(--app-card-soft-border)] bg-[var(--app-card-soft-bg)] px-4 py-3 text-sm text-[var(--app-text-secondary)]"
        >
          <div class="flex items-center justify-center py-3">
            <app-circular-progress-loader
              [size]="36"
              label="Cargando servicios del taller"
              colorClass="border-slate-600"
            />
          </div>
        </div>

      <div *ngIf="!isLoading()" class="relative z-10 flex flex-wrap gap-2.5">
        <button
          *ngFor="let item of allServices(); trackBy: trackByServiceId"
          type="button"
          (click)="toggleServiceSelection(item.id)"
          class="inline-flex items-center justify-center rounded-full border px-4 py-2 text-sm font-medium transition"
          [ngClass]="
            isServiceSelected(item.id)
              ? 'border-[var(--auth-input-focus)] bg-[var(--auth-input-focus)] text-[var(--app-accent-text)] shadow-sm'
              : 'border-[var(--app-card-soft-border)] bg-[var(--app-card-soft-bg)] text-[var(--app-text-primary)]'
          "
          [class.cursor-pointer]="isEditing()"
          [class.cursor-default]="!isEditing()"
        >
          {{ item.name }}
        </button>
      </div>

      <p class="relative z-10 text-xs text-[var(--auth-text-secondary)]">
        Seleccionados: {{ selectedServicesCount() }}
      </p>

      <div *ngIf="!isEditing()" class="relative z-10 pt-2">
        <button
          type="button"
          (click)="startEdit()"
          [disabled]="isLoading()"
          class="inline-flex h-12 items-center justify-center rounded-[var(--auth-control-radius)] bg-[var(--auth-button-bg)] px-5 text-sm font-semibold text-[var(--auth-button-text)] transition hover:bg-[var(--auth-button-hover)]"
        >
          Modificar servicios
        </button>
      </div>

      <div
        *ngIf="isEditing()"
        class="relative z-10 flex flex-col-reverse gap-3 pt-2 sm:flex-row sm:justify-end"
      >
        <button
          type="button"
          (click)="cancelEdit()"
          [disabled]="isSaving()"
          class="h-12 rounded-[var(--auth-control-radius)] border border-[var(--app-card-soft-border)] bg-[var(--app-card-bg)] px-5 text-sm font-medium text-[var(--app-text-primary)] transition hover:bg-[var(--app-card-soft-bg)]"
        >
          Cancelar
        </button>
        <button
          type="button"
          (click)="saveChanges()"
          [disabled]="isSaving() || draftServiceIds().length === 0"
          class="h-12 rounded-[var(--auth-control-radius)] bg-[var(--auth-button-bg)] px-5 text-sm font-semibold text-[var(--auth-button-text)] transition hover:bg-[var(--auth-button-hover)]"
        >
          {{ isSaving() ? 'Guardando...' : 'Guardar cambios' }}
        </button>
      </div>
      </app-primary-card>
  `,
})
export class ShopServicesCardComponent implements OnInit {
  private readonly repairShopActions = inject(RepairShopActionsService);
  private readonly toast = inject(AppToastService);

  readonly isLoading = signal(false);
  readonly isSaving = signal(false);
  readonly isEditing = signal(false);
  readonly allServices = signal<ServiceData[]>([]);
  readonly selectedServiceIds = signal<string[]>([]);
  readonly draftServiceIds = signal<string[]>([]);

  readonly selectedServicesCount = computed(() =>
    this.isEditing() ? this.draftServiceIds().length : this.selectedServiceIds().length,
  );

  async ngOnInit(): Promise<void> {
    await this.loadServicesData();
  }

  isServiceSelected(serviceId: string): boolean {
    const selected = this.isEditing() ? this.draftServiceIds() : this.selectedServiceIds();
    return selected.includes(serviceId);
  }

  toggleServiceSelection(serviceId: string): void {
    if (!this.isEditing()) {
      return;
    }

    const current = this.draftServiceIds();
    if (current.includes(serviceId)) {
      this.draftServiceIds.set(current.filter((id) => id !== serviceId));
      return;
    }

    this.draftServiceIds.set([...current, serviceId]);
  }

  startEdit(): void {
    this.draftServiceIds.set([...this.selectedServiceIds()]);
    this.isEditing.set(true);
  }

  cancelEdit(): void {
    this.draftServiceIds.set([...this.selectedServiceIds()]);
    this.isEditing.set(false);
    this.isSaving.set(false);
  }

  async saveChanges(): Promise<void> {
    if (this.isSaving() || this.draftServiceIds().length === 0) {
      return;
    }

    this.isSaving.set(true);
    try {
      const response = await this.repairShopActions.assignMyShopServices(
        {
          service_ids: this.draftServiceIds(),
        },
        { navigateOnSuccess: false },
      );

      if (!response.ok) {
        this.toast.showErrorList(response.errors);
        return;
      }

      this.toast.success('Servicios actualizados correctamente');
      this.isEditing.set(false);
      await this.loadServicesData();
    } finally {
      this.isSaving.set(false);
    }
  }

  trackByServiceId(_: number, service: ServiceData): string {
    return service.id;
  }

  private async loadServicesData(): Promise<void> {
    this.isLoading.set(true);
    try {
      const [allServicesResponse, myServicesResponse] = await Promise.all([
        this.repairShopActions.listServices(),
        this.repairShopActions.getMyShopServices(),
      ]);

      if (!allServicesResponse.ok) {
        this.toast.showErrorList(allServicesResponse.errors);
        return;
      }

      if (!myServicesResponse.ok) {
        this.toast.showErrorList(myServicesResponse.errors);
        return;
      }

      const selectedIds = myServicesResponse.data.map((service) => service.id);
      this.allServices.set(allServicesResponse.data);
      this.selectedServiceIds.set(selectedIds);
      this.draftServiceIds.set([...selectedIds]);
    } finally {
      this.isLoading.set(false);
    }
  }
}
