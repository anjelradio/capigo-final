import { CommonModule } from '@angular/common';
import { Component, Input, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

import { AppToastService } from '../../../../../core/services/app-toast.service';
import { PrimaryCardComponent } from '../../../../../features/shared/presentation/components/cards/primary-card.component';
import { FormSubmitButtonComponent } from '../../../../../features/shared/presentation/components/forms/form-submit-button.component';
import { CustomFieldedFormTextComponent } from '../../../../../features/shared/presentation/components/forms/custom-fielded-form-text.component';
import { AppModalComponent } from '../../../../../features/shared/presentation/components/modals/app-modal.component';
import { PrimaryActionButtonComponent } from '../../../../../features/shared/presentation/components/buttons/primary-action-button.component';
import { UserProfileUpdateFormSchema } from '../../../data/schemas/user.schema';
import { UserActionsService } from '../../actions/user/user-actions.service';
import type { UserProfile } from '../../../domain/entities/user-profile';

@Component({
  selector: 'app-personal-info-card',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    PrimaryCardComponent,
    PrimaryActionButtonComponent,
    FormSubmitButtonComponent,
    CustomFieldedFormTextComponent,
    AppModalComponent,
  ],
  template: `
    <app-primary-card variant="default" customClass="space-y-5">
      <header>
        <h2 class="text-xl font-semibold text-[var(--auth-text-primary)]">Informacion personal</h2>
        <p class="mt-1 text-sm text-[var(--auth-text-secondary)]">
          Actualiza y revisa los datos basicos de tu cuenta.
        </p>
      </header>

      <div class="grid gap-4 sm:grid-cols-2">
        <label class="space-y-1.5">
          <span class="text-xs font-medium uppercase tracking-wide text-slate-500">Nombre</span>
          <input
            type="text"
            [value]="profile?.first_name ?? ''"
            readonly
            class="h-11 w-full rounded-xl border border-[var(--dashboard-card-default-border)] bg-white/80 px-3 text-sm text-slate-700"
          />
        </label>

        <label class="space-y-1.5">
          <span class="text-xs font-medium uppercase tracking-wide text-slate-500">Apellido</span>
          <input
            type="text"
            [value]="profile?.last_name ?? ''"
            readonly
            class="h-11 w-full rounded-xl border border-[var(--dashboard-card-default-border)] bg-white/80 px-3 text-sm text-slate-700"
          />
        </label>

        <label class="space-y-1.5 sm:col-span-2">
          <span class="text-xs font-medium uppercase tracking-wide text-slate-500">Telefono</span>
          <input
            type="text"
            [value]="profile?.phone ?? ''"
            readonly
            class="h-11 w-full rounded-xl border border-[var(--dashboard-card-default-border)] bg-white/80 px-3 text-sm text-slate-700"
          />
        </label>
      </div>

      <app-primary-action-button
        label="Editar informacion"
        customClass="sm:w-auto sm:min-w-[220px]"
        (pressed)="openEditModal()"
      />
    </app-primary-card>

    <app-modal
      [open]="isModalOpen()"
      [showCloseButton]="false"
      (openChange)="onModalChange($event)"
    >
      <header class="border-b border-slate-200 px-6 pb-5 pt-7">
        <h2 class="text-2xl font-bold text-[var(--dashboard-nav-blue)]">
          Editar informacion personal
        </h2>
        <p class="mt-2 text-sm text-slate-600">
          Actualiza tu nombre, apellido y telefono para mantener tus datos al dia.
        </p>
      </header>

      <form
        (submit)="$event.preventDefault(); submitEditProfile()"
        [formGroup]="form"
        class="space-y-5 px-6 py-6"
      >
        <app-custom-fielded-form-text name="first_name" type="text" label="Nombre" />

        <app-custom-fielded-form-text name="last_name" type="text" label="Apellido" />

        <app-custom-fielded-form-text
          name="phone"
          type="tel"
          label="Telefono"
          inputMode="numeric"
          [maxLength]="9"
        />

        <div class="flex flex-col-reverse gap-3 pt-1 sm:flex-row sm:justify-end">
          <button
            type="button"
            (click)="closeEditModal()"
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
export class PersonalInfoCardComponent {
  private readonly fb = inject(FormBuilder);
  private readonly toast = inject(AppToastService);
  private readonly userActions = inject(UserActionsService);

  readonly isModalOpen = signal(false);
  readonly isSubmitting = signal(false);
  readonly form = this.fb.nonNullable.group({
    first_name: ['', [Validators.required]],
    last_name: ['', [Validators.required]],
    phone: ['', [Validators.required]],
  });

  @Input() profile: UserProfile | null = null;

  onModalChange(open: boolean): void {
    if (!open) {
      this.closeEditModal();
      return;
    }

    this.openEditModal();
  }

  openEditModal(): void {
    this.form.setValue({
      first_name: this.profile?.first_name ?? '',
      last_name: this.profile?.last_name ?? '',
      phone: this.profile?.phone ?? '',
    });
    this.isModalOpen.set(true);
  }

  closeEditModal(): void {
    this.isModalOpen.set(false);
    this.isSubmitting.set(false);
  }

  async submitEditProfile(): Promise<void> {
    if (this.form.invalid || this.isSubmitting()) {
      this.form.markAllAsTouched();
      return;
    }

    const result = UserProfileUpdateFormSchema.safeParse(this.form.getRawValue());
    if (!result.success) {
      this.toast.showErrorList(result.error.issues.map((issue) => issue.message));
      return;
    }

    this.isSubmitting.set(true);

    try {
      const response = await this.userActions.updateProfile(result.data);
      if (!response.ok) {
        this.toast.showErrorList(response.errors);
        return;
      }

      this.toast.success('Informacion actualizada correctamente');
      this.closeEditModal();
    } finally {
      this.isSubmitting.set(false);
    }
  }
}
