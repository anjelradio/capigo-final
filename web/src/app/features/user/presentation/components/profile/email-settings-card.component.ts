import { CommonModule } from '@angular/common';
import { Component, Input, computed, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

import { AppToastService } from '../../../../../core/services/app-toast.service';
import { PrimaryCardComponent } from '../../../../../features/shared/presentation/components/cards/primary-card.component';
import { PrimaryActionButtonComponent } from '../../../../../features/shared/presentation/components/buttons/primary-action-button.component';
import { CustomFieldedFormTextComponent } from '../../../../../features/shared/presentation/components/forms/custom-fielded-form-text.component';
import { FormSubmitButtonComponent } from '../../../../../features/shared/presentation/components/forms/form-submit-button.component';
import { AppModalComponent } from '../../../../../features/shared/presentation/components/modals/app-modal.component';
import {
  UpdateEmailFormSchema,
  VerifyEmailChangeOtpFormSchema,
} from '../../../data/schemas/user.schema';
import { UserActionsService } from '../../actions/user/user-actions.service';
import type { UserProfile } from '../../../domain/entities/user-profile';

type EmailChangeStep = 'confirm' | 'otp' | 'new_email';

@Component({
  selector: 'app-email-settings-card',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    PrimaryCardComponent,
    PrimaryActionButtonComponent,
    CustomFieldedFormTextComponent,
    AppModalComponent,
    FormSubmitButtonComponent,
  ],
  template: `
    <app-primary-card
      backgroundClass="bg-[var(--dashboard-card-soft-blue)]"
      customClass="space-y-5"
    >
      <header>
        <h2 class="text-xl font-semibold text-[var(--auth-text-primary)]">Correo electrónico</h2>
        <p class="mt-1 text-sm text-[var(--auth-text-secondary)]">
          Gestiona el correo vinculado a tu cuenta.
        </p>
      </header>

      <div class="rounded-xl border border-white/70 bg-white/70 px-4 py-3">
        <p class="text-xs font-medium uppercase tracking-wide text-slate-500">Correo actual</p>
        <p class="mt-1 text-sm font-medium text-slate-700">{{ profile?.email ?? 'Sin correo' }}</p>
      </div>

      <app-primary-action-button
        label="Cambiar correo electrónico"
        customClass="sm:w-auto sm:min-w-[260px]"
        (pressed)="openModal()"
      />
    </app-primary-card>

    <app-modal
      [open]="isModalOpen()"
      [showCloseButton]="false"
      (openChange)="onModalChange($event)"
    >
      <header class="border-b border-slate-200 px-6 pb-5 pt-7">
        <h2 class="text-2xl font-bold text-[var(--dashboard-nav-blue)]">{{ stepTitle() }}</h2>
        <p class="mt-2 text-sm text-slate-600">{{ stepDescription() }}</p>
      </header>

      <section *ngIf="step() === 'confirm'" class="space-y-5 px-6 py-6">
        <div class="rounded-xl border border-slate-200 bg-white px-4 py-3">
          <p class="text-xs font-medium uppercase tracking-wide text-slate-500">Correo actual</p>
          <p class="mt-1 text-sm font-medium text-slate-700">
            {{ profile?.email ?? 'Sin correo' }}
          </p>
        </div>

        <div class="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
          <button
            type="button"
            (click)="closeModal()"
            class="h-12 rounded-[var(--auth-control-radius)] border border-slate-300 px-5 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
          >
            Cancelar
          </button>
          <app-form-submit-button
            [loading]="isSubmitting()"
            label="Si, enviar código"
            loadingLabel="Enviando..."
            customClass="sm:w-auto sm:min-w-[200px]"
            type="button"
            (click)="requestOtp()"
          />
        </div>
      </section>

      <form
        *ngIf="step() === 'otp'"
        [formGroup]="otpForm"
        (submit)="$event.preventDefault(); verifyOtp()"
        class="space-y-5 px-6 py-6"
      >
        <app-custom-fielded-form-text
          name="otp"
          type="text"
          label="Codigo OTP"
          inputMode="numeric"
          [maxLength]="6"
          placeholder="000000"
          className="text-center text-lg tracking-[0.35em]"
        />

        <div class="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
          <button
            type="button"
            (click)="step.set('confirm')"
            class="h-12 rounded-[var(--auth-control-radius)] border border-slate-300 px-5 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
          >
            Volver
          </button>
          <app-form-submit-button
            [loading]="isSubmitting()"
            [disabled]="otpForm.invalid"
            label="Validar código OTP"
            loadingLabel="Validando..."
            customClass="sm:w-auto sm:min-w-[200px]"
          />
        </div>
      </form>

      <form
        *ngIf="step() === 'new_email'"
        [formGroup]="newEmailForm"
        (submit)="$event.preventDefault(); submitNewEmail()"
        class="space-y-5 px-6 py-6"
      >
        <app-custom-fielded-form-text
          name="new_email"
          type="email"
          label="Nuevo correo electronico"
          placeholder="correo@ejemplo.com"
          autocomplete="email"
        />

        <div class="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
          <button
            type="button"
            (click)="step.set('otp')"
            class="h-12 rounded-[var(--auth-control-radius)] border border-slate-300 px-5 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
          >
            Volver
          </button>
          <app-form-submit-button
            [loading]="isSubmitting()"
            [disabled]="newEmailForm.invalid"
            label="Guardar cambios"
            loadingLabel="Guardando..."
            customClass="sm:w-auto sm:min-w-[200px]"
          />
        </div>
      </form>
    </app-modal>
  `,
})
export class EmailSettingsCardComponent {
  private readonly fb = inject(FormBuilder);
  private readonly toast = inject(AppToastService);
  private readonly userActions = inject(UserActionsService);

  readonly isModalOpen = signal(false);
  readonly isSubmitting = signal(false);
  readonly step = signal<EmailChangeStep>('confirm');
  readonly emailChangeToken = signal('');
  readonly otpForm = this.fb.nonNullable.group({
    otp: ['', [Validators.required]],
  });
  readonly newEmailForm = this.fb.nonNullable.group({
    new_email: ['', [Validators.required, Validators.email]],
  });

  @Input() profile: UserProfile | null = null;

  readonly stepTitle = computed(() => {
    switch (this.step()) {
      case 'otp':
        return 'Verificar codigo OTP';
      case 'new_email':
        return 'Ingresa tu nuevo correo';
      default:
        return 'Cambiar correo electrónico';
    }
  });

  readonly stepDescription = computed(() => {
    switch (this.step()) {
      case 'otp':
        return 'Se te envio un codigo OTP a tu correo actual. Ingresalo para continuar.';
      case 'new_email':
        return 'Introduce el nuevo correo para actualizar tu cuenta.';
      default:
        return 'Te enviaremos un codigo OTP al correo actual para confirmar el cambio.';
    }
  });

  openModal(): void {
    this.step.set('confirm');
    this.emailChangeToken.set('');
    this.otpForm.reset({ otp: '' });
    this.newEmailForm.reset({ new_email: '' });
    this.isModalOpen.set(true);
  }

  onModalChange(open: boolean): void {
    if (!open) {
      this.closeModal();
      return;
    }

    this.openModal();
  }

  closeModal(): void {
    this.isModalOpen.set(false);
    this.isSubmitting.set(false);
  }

  async requestOtp(): Promise<void> {
    if (this.isSubmitting()) {
      return;
    }

    this.isSubmitting.set(true);
    try {
      const response = await this.userActions.requestEmailChangeOtp();
      if (!response.ok) {
        this.toast.showErrorList(response.errors);
        return;
      }

      this.step.set('otp');
      this.toast.success('Se envio un codigo OTP a tu correo actual');
    } finally {
      this.isSubmitting.set(false);
    }
  }

  async verifyOtp(): Promise<void> {
    if (this.otpForm.invalid || this.isSubmitting()) {
      this.otpForm.markAllAsTouched();
      return;
    }

    const result = VerifyEmailChangeOtpFormSchema.safeParse(this.otpForm.getRawValue());
    if (!result.success) {
      this.toast.showErrorList(result.error.issues.map((issue) => issue.message));
      return;
    }

    this.isSubmitting.set(true);
    try {
      const response = await this.userActions.verifyEmailChangeOtp(result.data);
      if (!response.ok) {
        this.toast.showErrorList(response.errors);
        return;
      }

      this.emailChangeToken.set(response.data.change_email_token);
      this.step.set('new_email');
      this.toast.success('Codigo OTP verificado correctamente');
    } finally {
      this.isSubmitting.set(false);
    }
  }

  async submitNewEmail(): Promise<void> {
    if (this.newEmailForm.invalid || this.isSubmitting()) {
      this.newEmailForm.markAllAsTouched();
      return;
    }

    const result = UpdateEmailFormSchema.safeParse({
      new_email: this.newEmailForm.controls.new_email.value,
      change_email_token: this.emailChangeToken(),
    });
    if (!result.success) {
      this.toast.showErrorList(result.error.issues.map((issue) => issue.message));
      return;
    }

    this.isSubmitting.set(true);
    try {
      const response = await this.userActions.updateEmail(result.data);
      if (!response.ok) {
        this.toast.showErrorList(response.errors);
        return;
      }

      this.toast.success('Correo actualizado correctamente');
      this.closeModal();
    } finally {
      this.isSubmitting.set(false);
    }
  }
}
