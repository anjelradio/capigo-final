import { CommonModule } from '@angular/common';
import { Component, OnInit, computed, inject, signal } from '@angular/core';

import { AppToastService } from '../../../../../core/services/app-toast.service';
import { FormSubmitButtonComponent } from '../../../../../features/shared/presentation/components/forms/form-submit-button.component';
import type { ServiceData } from '../../../data/schemas/repair-shop.schema';
import { RepairShopActionsService } from '../../actions/repair-shop/repair-shop-actions.service';

@Component({
  selector: 'app-register-shop-services-form',
  standalone: true,
  imports: [CommonModule, FormSubmitButtonComponent],
  template: `
    <section class="mt-6 space-y-4">
      <div class="text-left">
        <p class="text-sm font-medium text-[var(--auth-label)]">Servicios disponibles</p>
        <p class="mt-1 text-xs text-[var(--auth-text-secondary)]">
          Selecciona los servicios que ofrece tu taller.
        </p>
      </div>

      <div
        *ngIf="isLoading()"
        class="rounded-2xl border border-[var(--auth-input-border)] bg-white/65 p-4 text-sm"
      >
        Cargando servicios...
      </div>

      <div
        *ngIf="!isLoading()"
        class="flex flex-wrap content-start justify-center gap-2.5 rounded-2xl border border-[var(--auth-input-border)] bg-white/65 p-3 sm:gap-3"
      >
        <button
          *ngFor="let service of services(); trackBy: trackById"
          type="button"
          (click)="toggleService(service.id)"
          class="inline-flex min-h-9 items-center justify-center rounded-full border px-4 py-2 text-center text-sm font-semibold tracking-tight transition"
          [ngClass]="
            isSelected(service.id)
              ? 'border-[var(--auth-input-focus)] bg-[var(--auth-input-focus)] text-white shadow-sm'
              : 'border-[var(--auth-input-border)] bg-white/80 text-[var(--auth-text-secondary)] hover:border-[var(--auth-input-focus)]/45 hover:text-[var(--auth-text-primary)]'
          "
        >
          {{ service.name }}
        </button>
      </div>

      <p class="text-left text-xs text-[var(--auth-text-secondary)]">
        Seleccionados: {{ selectedCount() }}
      </p>

      <div class="pt-2">
        <app-form-submit-button
          [loading]="isSubmitting()"
          [disabled]="selectedCount() === 0 || isLoading()"
          label="Finalizar configuracion"
          loadingLabel="Guardando servicios..."
          [type]="'button'"
          (click)="submit()"
        />
      </div>
    </section>
  `,
})
export class RegisterShopServicesFormComponent implements OnInit {
  private readonly actions = inject(RepairShopActionsService);
  private readonly toast = inject(AppToastService);

  readonly isLoading = signal(false);
  readonly isSubmitting = signal(false);
  readonly services = signal<ServiceData[]>([]);
  readonly selectedServiceIds = signal<string[]>([]);

  readonly selectedCount = computed(() => this.selectedServiceIds().length);

  async ngOnInit(): Promise<void> {
    this.isLoading.set(true);
    try {
      const [servicesResponse, myServicesResponse] = await Promise.all([
        this.actions.listServices(),
        this.actions.getMyShopServices(),
      ]);

      if (!servicesResponse.ok) {
        this.toast.showErrorList(servicesResponse.errors);
        return;
      }

      this.services.set(servicesResponse.data);

      if (!myServicesResponse.ok) {
        this.toast.showErrorList(myServicesResponse.errors);
        return;
      }

      this.selectedServiceIds.set(myServicesResponse.data.map((service) => service.id));
    } finally {
      this.isLoading.set(false);
    }
  }

  isSelected(serviceId: string): boolean {
    return this.selectedServiceIds().includes(serviceId);
  }

  toggleService(serviceId: string): void {
    const current = this.selectedServiceIds();
    if (current.includes(serviceId)) {
      this.selectedServiceIds.set(current.filter((id) => id !== serviceId));
      return;
    }

    this.selectedServiceIds.set([...current, serviceId]);
  }

  async submit(): Promise<void> {
    if (this.isSubmitting() || this.selectedCount() === 0) {
      return;
    }

    this.isSubmitting.set(true);
    try {
      const response = await this.actions.assignMyShopServices({
        service_ids: this.selectedServiceIds(),
      });

      if (!response.ok) {
        this.toast.showErrorList(response.errors);
        return;
      }

      this.toast.success('Servicios guardados correctamente');
    } finally {
      this.isSubmitting.set(false);
    }
  }

  trackById(_: number, service: ServiceData): string {
    return service.id;
  }
}
