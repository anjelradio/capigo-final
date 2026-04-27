import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Output, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';

import { AppToastService } from '../../../../../core/services/app-toast.service';
import {
  parseLocalDateTimeInputToUtcIso,
  toDatetimeLocalInputValue,
} from '../../../../shared/data/infrastructure/date-time';
import { CustomFieldedFormTextComponent } from '../../../../shared/presentation/components/forms/custom-fielded-form-text.component';
import { FormSubmitButtonComponent } from '../../../../shared/presentation/components/forms/form-submit-button.component';
import { AppModalComponent } from '../../../../shared/presentation/components/modals/app-modal.component';
import { RepairShopActionsService } from '../../actions/repair-shop/repair-shop-actions.service';

@Component({
  selector: 'app-generate-invitation-trigger',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    AppModalComponent,
    CustomFieldedFormTextComponent,
    FormSubmitButtonComponent,
  ],
  template: `
    <button
      type="button"
      (click)="openModal()"
      class="mt-6 inline-flex h-12 items-center justify-center gap-2 rounded-[var(--auth-control-radius)] bg-[var(--auth-button-bg)] px-5 text-sm font-semibold text-[var(--auth-button-text)] transition hover:bg-[var(--auth-button-hover)]"
    >
      Generar invitacion
    </button>

    <app-modal
      [open]="isModalOpen()"
      [showCloseButton]="false"
      (openChange)="onModalChange($event)"
    >
      <header class="border-b border-slate-200 px-6 pb-5 pt-7">
        <h2 class="text-2xl font-bold text-[var(--dashboard-nav-blue)]">Generar invitacion</h2>
        <p class="mt-2 text-sm text-slate-600">
          Selecciona una fecha de expiracion para el nuevo codigo.
        </p>
      </header>

      <form
        [formGroup]="invitationForm"
        (submit)="$event.preventDefault(); submitInvitation()"
        class="space-y-5 px-6 py-6"
      >
        <app-custom-fielded-form-text
          name="expires_at"
          type="datetime-local"
          label="Fecha de expiracion"
        />

        <div class="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
          <button
            type="button"
            (click)="closeModal()"
            [disabled]="isSubmitting()"
            class="h-12 rounded-[var(--auth-control-radius)] border border-slate-300 px-5 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
          >
            Cancelar
          </button>
          <app-form-submit-button
            [loading]="isSubmitting()"
            [disabled]="invitationForm.invalid"
            label="Aceptar"
            loadingLabel="Generando..."
            customClass="sm:w-auto sm:min-w-[170px]"
          />
        </div>
      </form>
    </app-modal>
  `,
})
export class GenerateInvitationTriggerComponent {
  private readonly fb = inject(FormBuilder);
  private readonly repairShopActions = inject(RepairShopActionsService);
  private readonly toast = inject(AppToastService);

  @Output() invitationCreated = new EventEmitter<void>();

  readonly isModalOpen = signal(false);
  readonly isSubmitting = signal(false);
  readonly invitationForm = this.fb.nonNullable.group({
    expires_at: '',
  });

  openModal(): void {
    const defaultFutureDate = new Date(Date.now() + 24 * 60 * 60 * 1000);
    this.invitationForm.reset({
      expires_at: toDatetimeLocalInputValue(defaultFutureDate),
    });
    this.isModalOpen.set(true);
  }

  onModalChange(open: boolean): void {
    this.isModalOpen.set(open);
  }

  closeModal(): void {
    this.isModalOpen.set(false);
    this.isSubmitting.set(false);
  }

  async submitInvitation(): Promise<void> {
    if (this.isSubmitting()) {
      return;
    }

    const rawValue = this.invitationForm.controls.expires_at.getRawValue().trim();
    if (!rawValue) {
      this.toast.error('Selecciona una fecha de expiracion');
      return;
    }

    const expiresAtUtcIso = parseLocalDateTimeInputToUtcIso(rawValue);
    if (!expiresAtUtcIso) {
      this.toast.error('La fecha seleccionada no es valida');
      return;
    }

    const date = new Date(expiresAtUtcIso);

    if (date.getTime() <= Date.now()) {
      this.toast.error('La fecha de expiracion debe ser futura');
      return;
    }

    this.isSubmitting.set(true);
    try {
      const response = await this.repairShopActions.createMyShopInvitation({
        expires_at: expiresAtUtcIso,
      });

      if (!response.ok) {
        this.toast.showErrorList(response.errors);
        return;
      }

      this.toast.success('Invitacion generada correctamente');
      this.closeModal();
      this.invitationCreated.emit();
    } finally {
      this.isSubmitting.set(false);
    }
  }
}
