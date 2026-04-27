import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';

import { AppToastService } from '../../../../../core/services/app-toast.service';
import { CustomFieldedFormTextComponent } from '../../../../../features/shared/presentation/components/forms/custom-fielded-form-text.component';
import { FormSubmitButtonComponent } from '../../../../../features/shared/presentation/components/forms/form-submit-button.component';
import { RepairShopFormSchema } from '../../../data/schemas/repair-shop.schema';
import { RepairShopActionsService } from '../../actions/repair-shop/repair-shop-actions.service';
import { LocationPickerMapComponent } from './location-picker-map.component';

const SANTA_CRUZ_CENTER = {
  latitude: -17.7833,
  longitude: -63.1821,
};

@Component({
  selector: 'app-create-repair-shop-form',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    CustomFieldedFormTextComponent,
    LocationPickerMapComponent,
    FormSubmitButtonComponent,
  ],
  template: `
    <form [formGroup]="form" (ngSubmit)="submit()" class="mt-6 space-y-4">
      <app-custom-fielded-form-text
        name="name"
        type="text"
        label="Nombre del taller"
        placeholder="Ejemplo: Taller Los Andes"
      />

      <div class="space-y-1.5 text-left">
        <p class="text-sm font-medium text-[var(--auth-label)]">Ubicacion del taller</p>
        <p class="text-xs text-[var(--auth-text-secondary)]">
          Haz clic en el mapa o arrastra el marcador para definir la ubicacion.
        </p>
      </div>

      <app-location-picker-map
        [latitude]="selectedLatitude()"
        [longitude]="selectedLongitude()"
        (locationChange)="onLocationChange($event)"
      />

      <div class="pt-2">
        <app-form-submit-button
          [loading]="isSubmitting()"
          [disabled]="isSubmitting()"
          label="Registrar taller"
          loadingLabel="Preparando datos..."
        />
      </div>
    </form>
  `,
})
export class CreateRepairShopFormComponent {
  private readonly repairShopActions = inject(RepairShopActionsService);
  private readonly fb = inject(FormBuilder);
  private readonly toast = inject(AppToastService);

  readonly isSubmitting = signal(false);
  readonly selectedLatitude = signal<number>(Number(SANTA_CRUZ_CENTER.latitude.toFixed(6)));
  readonly selectedLongitude = signal<number>(Number(SANTA_CRUZ_CENTER.longitude.toFixed(6)));

  readonly form = this.fb.nonNullable.group({
    name: '',
  });

  onLocationChange(location: { latitude: number; longitude: number }): void {
    this.selectedLatitude.set(location.latitude);
    this.selectedLongitude.set(location.longitude);
  }

  async submit(): Promise<void> {
    if (this.isSubmitting()) {
      return;
    }

    this.isSubmitting.set(true);

    try {
      const payload = {
        name: this.form.controls.name.getRawValue(),
        latitude: this.selectedLatitude(),
        longitude: this.selectedLongitude(),
      };

      const parsed = RepairShopFormSchema.safeParse(payload);
      if (!parsed.success) {
        this.toast.showErrorList(parsed.error.issues.map((issue) => issue.message));
        return;
      }

      const response = await this.repairShopActions.createRepairShop(parsed.data);
      if (!response.ok) {
        this.toast.showErrorList(response.errors);
        return;
      }

      this.form.reset({ name: '' });
      this.toast.success('Taller registrado correctamente');
    } finally {
      this.isSubmitting.set(false);
    }
  }
}
