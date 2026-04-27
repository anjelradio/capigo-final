import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

import { AppToastService } from '../../../../../core/services/app-toast.service';
import { PrimaryCardComponent } from '../../../../../features/shared/presentation/components/cards/primary-card.component';
import { PrimaryActionButtonComponent } from '../../../../../features/shared/presentation/components/buttons/primary-action-button.component';
import { CustomFieldedFormTextComponent } from '../../../../../features/shared/presentation/components/forms/custom-fielded-form-text.component';
import { FormSubmitButtonComponent } from '../../../../../features/shared/presentation/components/forms/form-submit-button.component';
import { AppModalComponent } from '../../../../../features/shared/presentation/components/modals/app-modal.component';
import { UpdatePasswordFormSchema } from '../../../data/schemas/user.schema';
import { UserActionsService } from '../../actions/user/user-actions.service';

@Component({
  selector: 'app-password-settings-card',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    PrimaryCardComponent,
    PrimaryActionButtonComponent,
    CustomFieldedFormTextComponent,
    FormSubmitButtonComponent,
    AppModalComponent,
  ],
  template: `
    <app-primary-card
      backgroundClass="bg-[var(--dashboard-card-soft-sand)]"
      customClass="space-y-5"
    >
      <header>
        <h2 class="text-xl font-semibold text-[var(--auth-text-primary)]">Contraseña</h2>
        <p class="mt-1 text-sm text-[var(--auth-text-secondary)]">
          Refuerza la seguridad de tu cuenta cambiando tu contraseña.
        </p>
      </header>

      <app-primary-action-button
        label="Cambiar contraseña"
        customClass="sm:w-auto sm:min-w-[220px]"
        (pressed)="openModal()"
      />
    </app-primary-card>

    <app-modal
      [open]="isModalOpen()"
      [showCloseButton]="false"
      (openChange)="onModalChange($event)"
    >
      <header class="border-b border-slate-200 px-6 pb-5 pt-7">
        <h2 class="text-2xl font-bold text-[var(--dashboard-nav-blue)]">Cambiar contraseña</h2>
        <p class="mt-2 text-sm text-slate-600">
          Completa los campos para actualizar tu contraseña de forma segura.
        </p>
      </header>

      <form
        [formGroup]="form"
        (submit)="$event.preventDefault(); submit()"
        class="space-y-5 px-6 py-6"
      >
        <app-custom-fielded-form-text
          name="current_password"
          type="password"
          label="Contrasena actual"
          autocomplete="current-password"
        />

        <app-custom-fielded-form-text
          name="new_password"
          type="password"
          label="Nueva contrasena"
          autocomplete="new-password"
        />

        <app-custom-fielded-form-text
          name="confirm_new_password"
          type="password"
          label="Confirmar nueva contrasena"
          autocomplete="new-password"
        />

        <div class="flex flex-col-reverse gap-3 pt-1 sm:flex-row sm:justify-end">
          <button
            type="button"
            (click)="closeModal()"
            class="h-12 rounded-[var(--auth-control-radius)] border border-slate-300 px-5 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
          >
            Cancelar
          </button>
          <app-form-submit-button
            [loading]="isSubmitting()"
            [disabled]="form.invalid"
            label="Guardar cambios"
            loadingLabel="Guardando..."
            customClass="sm:w-auto sm:min-w-[180px]"
          />
        </div>
      </form>
    </app-modal>
  `,
})
export class PasswordSettingsCardComponent {
  private readonly fb = inject(FormBuilder);
  private readonly toast = inject(AppToastService);
  private readonly userActions = inject(UserActionsService);

  readonly isModalOpen = signal(false);
  readonly isSubmitting = signal(false);
  readonly form = this.fb.nonNullable.group({
    current_password: ['', [Validators.required]],
    new_password: ['', [Validators.required]],
    confirm_new_password: ['', [Validators.required]],
  });

  onModalChange(open: boolean): void {
    if (!open) {
      this.closeModal();
      return;
    }

    this.openModal();
  }

  openModal(): void {
    this.form.reset({
      current_password: '',
      new_password: '',
      confirm_new_password: '',
    });
    this.isModalOpen.set(true);
  }

  closeModal(): void {
    this.isModalOpen.set(false);
    this.isSubmitting.set(false);
  }

  async submit(): Promise<void> {
    if (this.form.invalid || this.isSubmitting()) {
      this.form.markAllAsTouched();
      return;
    }

    const result = UpdatePasswordFormSchema.safeParse(this.form.getRawValue());
    if (!result.success) {
      this.toast.showErrorList(result.error.issues.map((issue) => issue.message));
      return;
    }

    this.isSubmitting.set(true);
    try {
      const response = await this.userActions.updatePassword(result.data);
      if (!response.ok) {
        this.toast.showErrorList(response.errors);
        return;
      }

      this.toast.success('Contraseña actualizada correctamente');
      this.closeModal();
    } finally {
      this.isSubmitting.set(false);
    }
  }
}
