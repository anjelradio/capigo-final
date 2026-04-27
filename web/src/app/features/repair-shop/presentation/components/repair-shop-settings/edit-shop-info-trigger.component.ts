import { Component, computed, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { LucideAngularModule, PenLine } from 'lucide-angular';

import { AppToastService } from '../../../../../core/services/app-toast.service';
import { RepairShopStore } from '../../../../../core/store/repair-shop.store';
import { CustomFieldedFormTextComponent } from '../../../../../features/shared/presentation/components/forms/custom-fielded-form-text.component';
import { FormSubmitButtonComponent } from '../../../../../features/shared/presentation/components/forms/form-submit-button.component';
import { AppModalComponent } from '../../../../../features/shared/presentation/components/modals/app-modal.component';
import { RepairShopActionsService } from '../../actions/repair-shop/repair-shop-actions.service';

@Component({
  selector: 'app-edit-shop-info-trigger',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    LucideAngularModule,
    AppModalComponent,
    CustomFieldedFormTextComponent,
    FormSubmitButtonComponent,
  ],
  template: `
    <button
      type="button"
      (click)="openModal()"
      class="inline-flex h-12 items-center justify-center gap-2 rounded-[var(--auth-control-radius)] bg-[var(--auth-button-bg)] px-5 text-sm font-semibold text-[var(--auth-button-text)] transition hover:bg-[var(--auth-button-hover)]"
    >
      <lucide-angular [img]="editIcon" [size]="16" />
      Editar informacion del taller
    </button>

    <app-modal
      [open]="isModalOpen()"
      [showCloseButton]="false"
      (openChange)="onModalChange($event)"
    >
      <header class="border-b border-[var(--app-card-soft-border)] px-6 pb-5 pt-7">
        <h2 class="text-2xl font-bold text-[var(--dashboard-nav-blue)]">
          Editar informacion del taller
        </h2>
        <p class="mt-2 text-sm text-[var(--app-text-secondary)]">
          Actualiza el nombre y la direccion visible para los clientes.
        </p>
      </header>

      <form
        [formGroup]="shopNameForm"
        (submit)="$event.preventDefault(); submitShopName()"
        class="space-y-5 px-6 py-6"
      >
        <app-custom-fielded-form-text name="name" type="text" label="Nombre del taller" />

        <label class="block space-y-1.5">
          <span class="text-sm font-medium text-[var(--auth-label)]">Direccion del taller</span>
          <textarea
            formControlName="text_address"
            rows="3"
            class="w-full resize-none rounded-[var(--auth-control-radius)] border border-[var(--auth-input-border)] bg-[var(--auth-input-bg)] px-4 py-3 text-sm outline-none transition focus:border-[var(--auth-input-focus)]"
          ></textarea>
        </label>

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
            [loading]="isSaving()"
            [disabled]="shopNameForm.invalid"
            label="Guardar cambios"
            loadingLabel="Guardando..."
            customClass="sm:w-auto sm:min-w-[180px]"
          />
        </div>
      </form>
    </app-modal>
  `,
})
export class EditShopInfoTriggerComponent {
  private readonly fb = inject(FormBuilder);
  private readonly repairShopActions = inject(RepairShopActionsService);
  private readonly repairShopStore = inject(RepairShopStore);
  private readonly toast = inject(AppToastService);

  readonly editIcon = PenLine;
  readonly isModalOpen = signal(false);
  readonly isSaving = signal(false);
  readonly currentShopName = computed(() => this.repairShopStore.shop()?.name ?? 'Mi Taller');
  readonly currentShopAddress = computed(
    () => this.repairShopStore.shop()?.text_address ?? 'Ubicacion de taller',
  );

  readonly shopNameForm = this.fb.nonNullable.group({
    name: ['', [Validators.required, Validators.minLength(5), Validators.maxLength(70)]],
    text_address: ['', [Validators.required, Validators.minLength(5), Validators.maxLength(240)]],
  });

  openModal(): void {
    this.shopNameForm.setValue({
      name: this.currentShopName(),
      text_address: this.currentShopAddress(),
    });
    this.isModalOpen.set(true);
  }

  onModalChange(open: boolean): void {
    this.isModalOpen.set(open);
  }

  closeModal(): void {
    this.isModalOpen.set(false);
    this.isSaving.set(false);
  }

  async submitShopName(): Promise<void> {
    if (this.shopNameForm.invalid || this.isSaving()) {
      this.shopNameForm.markAllAsTouched();
      return;
    }

    this.isSaving.set(true);
    try {
      const response = await this.repairShopActions.updateMyShopProfile(
        this.shopNameForm.getRawValue(),
      );
      if (!response.ok) {
        this.toast.showErrorList(response.errors);
        return;
      }

      this.toast.success('Nombre del taller actualizado correctamente');
      this.closeModal();
    } finally {
      this.isSaving.set(false);
    }
  }
}
