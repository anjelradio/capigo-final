import { Component, inject, signal } from '@angular/core';

import { AppToastService } from '../../../../../core/services/app-toast.service';
import { RepairShopStore } from '../../../../../core/store/repair-shop.store';
import { FormSubmitButtonComponent } from '../../../../../features/shared/presentation/components/forms/form-submit-button.component';
import { AppModalComponent } from '../../../../../features/shared/presentation/components/modals/app-modal.component';
import { RepairShopActionsService } from '../../actions/repair-shop/repair-shop-actions.service';
import { LocationPickerMapComponent } from '../repair-shop-onboarding/location-picker-map.component';

@Component({
  selector: 'app-edit-shop-location-trigger',
  standalone: true,
  imports: [AppModalComponent, FormSubmitButtonComponent, LocationPickerMapComponent],
  template: `
    <button
      type="button"
      (click)="openModal()"
      class="inline-flex h-11 items-center justify-center rounded-full bg-[var(--auth-button-bg)] px-5 text-sm font-medium text-[var(--auth-button-text)] transition hover:bg-[var(--auth-button-hover)]"
    >
      Actualizar ubicacion
    </button>

    <app-modal
      [open]="isModalOpen()"
      [showCloseButton]="false"
      [panelClass]="'max-w-4xl'"
      (openChange)="onModalChange($event)"
    >
      <header class="border-b border-[var(--app-card-soft-border)] px-6 pb-5 pt-7">
        <h2 class="text-2xl font-bold text-[var(--dashboard-nav-blue)]">
          Actualizar ubicacion del taller
        </h2>
        <p class="mt-2 text-sm text-[var(--app-text-secondary)]">
          Selecciona el punto en el mapa y guardaremos la ubicacion actualizada.
        </p>
      </header>

      <section class="space-y-5 px-6 py-6">
        <app-location-picker-map
          [open]="isModalOpen()"
          [latitude]="draftLatitude()"
          [longitude]="draftLongitude()"
          (locationChange)="onLocationPicked($event)"
        />

        <div class="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
          <button
            type="button"
            (click)="closeModal()"
            [disabled]="isSaving()"
            class="h-12 rounded-[var(--auth-control-radius)] border border-[var(--app-card-soft-border)] px-5 text-sm font-medium text-[var(--app-text-primary)] transition hover:bg-[var(--app-card-soft-bg)]"
          >
            Cancelar
          </button>
          <app-form-submit-button
            [type]="'button'"
            [loading]="isSaving()"
            (click)="submitLocation()"
            label="Actualizar ubicacion"
            loadingLabel="Actualizando..."
            customClass="sm:w-auto sm:min-w-[220px]"
          />
        </div>
      </section>
    </app-modal>
  `,
})
export class EditShopLocationTriggerComponent {
  private readonly repairShopActions = inject(RepairShopActionsService);
  private readonly repairShopStore = inject(RepairShopStore);
  private readonly toast = inject(AppToastService);

  readonly isModalOpen = signal(false);
  readonly isSaving = signal(false);
  readonly draftLatitude = signal<number>(-17.7833);
  readonly draftLongitude = signal<number>(-63.1821);

  openModal(): void {
    const shop = this.repairShopStore.shop();
    this.draftLatitude.set(shop?.latitude ?? -17.7833);
    this.draftLongitude.set(shop?.longitude ?? -63.1821);
    this.isModalOpen.set(true);
  }

  onModalChange(open: boolean): void {
    this.isModalOpen.set(open);
  }

  closeModal(): void {
    this.isModalOpen.set(false);
    this.isSaving.set(false);
  }

  onLocationPicked(location: { latitude: number; longitude: number }): void {
    this.draftLatitude.set(location.latitude);
    this.draftLongitude.set(location.longitude);
  }

  async submitLocation(): Promise<void> {
    if (this.isSaving()) {
      return;
    }

    this.isSaving.set(true);
    try {
      const response = await this.repairShopActions.updateMyShopLocation({
        latitude: this.draftLatitude(),
        longitude: this.draftLongitude(),
      });

      if (!response.ok) {
        this.toast.showErrorList(response.errors);
        return;
      }

      this.toast.success('Ubicacion actualizada correctamente');
      this.closeModal();
    } finally {
      this.isSaving.set(false);
    }
  }
}
