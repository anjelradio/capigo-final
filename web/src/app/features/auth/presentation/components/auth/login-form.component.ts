import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { AppToastService } from '../../../../../core/services/app-toast.service';
import { CustomFieldedFormTextComponent } from '../../../../../features/shared/presentation/components/forms/custom-fielded-form-text.component';
import { FormSubmitButtonComponent } from '../../../../../features/shared/presentation/components/forms/form-submit-button.component';
import { ForgotPasswordModalTriggerComponent } from './forgot-password-modal-trigger.component';
import { LoginFormSchema } from '../../../data/schemas/auth.schema';
import { AuthActionsService } from '../../actions/auth/auth-actions.service';

@Component({
  selector: 'app-login-form',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    RouterLink,
    CustomFieldedFormTextComponent,
    FormSubmitButtonComponent,
    ForgotPasswordModalTriggerComponent,
  ],
  template: `
    <form [formGroup]="form" (ngSubmit)="submit()" class="mt-6 space-y-3.5 text-left">
      <app-custom-fielded-form-text
        name="email"
        type="email"
        label="Email"
        placeholder="correo@ejemplo.com"
        autocomplete="email"
      />

      <app-custom-fielded-form-text
        name="password"
        type="password"
        label="Contrasena"
        placeholder="********"
        autocomplete="current-password"
      />

      <div class="flex items-center justify-end">
        <app-forgot-password-modal-trigger />
      </div>

      <div class="pt-2.5">
        <app-form-submit-button
          [loading]="isSubmitting()"
          [disabled]="isSubmitting()"
          label="Iniciar sesion"
          loadingLabel="Ingresando..."
        />
      </div>
    </form>

    <p class="mt-6 text-left text-sm text-[var(--auth-text-secondary)]">
      No tienes una cuenta?
      <a
        routerLink="/auth/register"
        class="ml-1 font-semibold text-[var(--auth-link)] underline underline-offset-2"
      >
        Registrate
      </a>
    </p>
  `,
})
export class LoginFormComponent {
  private readonly fb = inject(FormBuilder);
  private readonly toast = inject(AppToastService);
  private readonly authActions = inject(AuthActionsService);

  readonly isSubmitting = signal(false);
  readonly form = this.fb.nonNullable.group({
    email: '',
    password: '',
  });

  async submit(): Promise<void> {
    if (this.isSubmitting()) {
      return;
    }

    const result = LoginFormSchema.safeParse(this.form.getRawValue());
    if (!result.success) {
      this.toast.showErrorList(result.error.issues.map((issue) => issue.message));
      return;
    }

    this.isSubmitting.set(true);

    try {
      const response = await this.authActions.login(result.data);

      if (!response.ok) {
        this.toast.showErrorList(response.errors);
        return;
      }

      this.form.reset({ email: '', password: '' });
      this.toast.success('Bienvenido de nuevo');
    } finally {
      this.isSubmitting.set(false);
    }
  }
}
