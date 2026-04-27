import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';

import { AppToastService } from '../../../../../core/services/app-toast.service';
import { CustomFieldedFormTextComponent } from '../../../../../features/shared/presentation/components/forms/custom-fielded-form-text.component';
import { FormSubmitButtonComponent } from '../../../../../features/shared/presentation/components/forms/form-submit-button.component';
import { AppModalComponent } from '../../../../../features/shared/presentation/components/modals/app-modal.component';
import {
  RequestPasswordResetOtpFormSchema,
  VerifyPasswordResetOtpFormSchema,
} from '../../../data/schemas/auth.schema';
import { AuthActionsService } from '../../actions/auth/auth-actions.service';

type ForgotPasswordStep = 'email' | 'otp';

@Component({
  selector: 'app-forgot-password-modal-trigger',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    AppModalComponent,
    FormSubmitButtonComponent,
    CustomFieldedFormTextComponent,
  ],
  template: `
    <button
      type="button"
      class="text-sm font-medium text-[var(--auth-link)] underline underline-offset-2"
      (click)="openModal()"
    >
      Olvidaste tu contrasena?
    </button>

    <app-modal
      [open]="isModalOpen()"
      [showCloseButton]="false"
      panelClass="max-w-[calc(100%-2rem)] sm:max-w-xl"
      (openChange)="onOpenChange($event)"
    >
      <header class="border-b border-slate-200 px-6 pb-5 pt-7">
        <h2 class="text-2xl font-bold text-[var(--dashboard-nav-blue)]">
          {{ step() === 'email' ? 'Recuperar contrasena' : 'Verificar codigo OTP' }}
        </h2>
        <p class="mt-2 text-sm text-slate-600">
          {{
            step() === 'email'
              ? 'Ingresa el correo de tu cuenta para enviarte un codigo OTP de recuperacion.'
              : 'Ingresa el codigo OTP. Si es valido, te enviaremos una nueva contrasena a tu correo.'
          }}
        </p>
      </header>

      <form
        *ngIf="step() === 'email'"
        [formGroup]="requestOtpForm"
        (submit)="$event.preventDefault(); submitRequestOtp()"
        class="space-y-6 px-6 py-6"
      >
        <app-custom-fielded-form-text
          name="email"
          type="email"
          label="Correo de la cuenta"
          placeholder="correo@ejemplo.com"
          autocomplete="email"
        />

        <div class="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
          <button
            type="button"
            (click)="resetModal()"
            class="h-12 rounded-[var(--auth-control-radius)] border border-slate-300 px-5 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
          >
            Cancelar
          </button>
          <app-form-submit-button
            [loading]="isSubmitting()"
            [disabled]="requestOtpForm.invalid"
            label="Enviar codigo"
            loadingLabel="Enviando..."
            customClass="sm:w-auto sm:min-w-[170px]"
          />
        </div>
      </form>

      <form
        *ngIf="step() === 'otp'"
        [formGroup]="verifyOtpForm"
        (submit)="$event.preventDefault(); submitVerifyOtp()"
        class="space-y-6 px-6 py-6"
      >
        <app-custom-fielded-form-text
          name="otp"
          type="text"
          label="Codigo OTP"
          placeholder="000000"
          inputMode="numeric"
          [maxLength]="6"
          className="text-center text-lg tracking-[0.35em]"
        />

        <div class="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
          <button
            type="button"
            (click)="backToEmailStep()"
            class="h-12 rounded-[var(--auth-control-radius)] border border-slate-300 px-5 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
          >
            Volver
          </button>
          <app-form-submit-button
            [loading]="isSubmitting()"
            [disabled]="verifyOtpForm.invalid"
            label="Verificar codigo"
            loadingLabel="Verificando..."
            customClass="sm:w-auto sm:min-w-[170px]"
          />
        </div>
      </form>
    </app-modal>
  `,
})
export class ForgotPasswordModalTriggerComponent {
  private readonly fb = inject(FormBuilder);
  private readonly authActions = inject(AuthActionsService);
  private readonly toast = inject(AppToastService);

  readonly isModalOpen = signal(false);
  readonly step = signal<ForgotPasswordStep>('email');
  readonly isSubmitting = signal(false);
  readonly requestOtpForm = this.fb.nonNullable.group({
    email: '',
  });
  readonly verifyOtpForm = this.fb.nonNullable.group({
    otp: '',
  });

  onOpenChange(open: boolean): void {
    if (!open) {
      this.resetModal();
      return;
    }

    this.isModalOpen.set(true);
  }

  openModal(): void {
    this.isModalOpen.set(true);
  }

  backToEmailStep(): void {
    this.step.set('email');
    this.verifyOtpForm.reset({ otp: '' });
  }

  resetModal(): void {
    this.isModalOpen.set(false);
    this.step.set('email');
    this.requestOtpForm.reset({ email: '' });
    this.verifyOtpForm.reset({ otp: '' });
    this.isSubmitting.set(false);
  }

  async submitRequestOtp(): Promise<void> {
    if (this.isSubmitting()) {
      return;
    }

    const result = RequestPasswordResetOtpFormSchema.safeParse(this.requestOtpForm.getRawValue());
    if (!result.success) {
      this.toast.showErrorList(result.error.issues.map((issue) => issue.message));
      return;
    }

    this.isSubmitting.set(true);
    try {
      const response = await this.authActions.requestPasswordResetOtp(result.data);
      if (!response.ok) {
        this.toast.showErrorList(response.errors);
        return;
      }

      this.step.set('otp');
      this.toast.success('Si el correo existe, enviamos un codigo OTP');
    } finally {
      this.isSubmitting.set(false);
    }
  }

  async submitVerifyOtp(): Promise<void> {
    if (this.isSubmitting()) {
      return;
    }

    const result = VerifyPasswordResetOtpFormSchema.safeParse({
      email: this.requestOtpForm.controls.email.getRawValue(),
      otp: this.verifyOtpForm.controls.otp.getRawValue(),
    });
    if (!result.success) {
      this.toast.showErrorList(result.error.issues.map((issue) => issue.message));
      return;
    }

    this.isSubmitting.set(true);
    try {
      const response = await this.authActions.verifyPasswordResetOtp(result.data);
      if (!response.ok) {
        this.toast.showErrorList(response.errors);
        return;
      }

      this.toast.success(
        'Revisa tu correo. Te enviamos una nueva contrasena temporal para iniciar sesion.',
      );
      this.resetModal();
    } finally {
      this.isSubmitting.set(false);
    }
  }
}
