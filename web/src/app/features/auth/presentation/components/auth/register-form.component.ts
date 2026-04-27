import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { AppToastService } from '../../../../../core/services/app-toast.service';
import { CustomFieldedFormTextComponent } from '../../../../../features/shared/presentation/components/forms/custom-fielded-form-text.component';
import { FormSubmitButtonComponent } from '../../../../../features/shared/presentation/components/forms/form-submit-button.component';
import { RegisterFormSchema } from '../../../data/schemas/auth.schema';
import { AuthActionsService } from '../../actions/auth/auth-actions.service';

@Component({
  selector: 'app-register-form',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    RouterLink,
    CustomFieldedFormTextComponent,
    FormSubmitButtonComponent,
  ],
  template: `
    <form [formGroup]="form" (ngSubmit)="submit()" class="mt-6 space-y-3.5 text-left">
      <app-custom-fielded-form-text
        name="first_name"
        type="text"
        label="Nombre"
        placeholder="Juan"
        autocomplete="given-name"
      />

      <app-custom-fielded-form-text
        name="last_name"
        type="text"
        label="Apellido"
        placeholder="Perez"
        autocomplete="family-name"
      />

      <app-custom-fielded-form-text
        name="phone"
        type="tel"
        label="Telefono"
        placeholder="987654321"
        autocomplete="tel"
      />

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
        autocomplete="new-password"
      />

      <div class="pt-2.5">
        <app-form-submit-button
          [loading]="isSubmitting()"
          [disabled]="isSubmitting()"
          label="Crear cuenta"
          loadingLabel="Creando cuenta..."
        />
      </div>
    </form>

    <p class="mt-6 text-left text-sm text-[var(--auth-text-secondary)]">
      Ya tienes una cuenta?
      <a
        routerLink="/auth/login"
        class="ml-1 font-semibold text-[var(--auth-link)] underline underline-offset-2"
      >
        Inicia sesion
      </a>
    </p>
  `,
})
export class RegisterFormComponent {
  private readonly fb = inject(FormBuilder);
  private readonly toast = inject(AppToastService);
  private readonly authActions = inject(AuthActionsService);

  readonly isSubmitting = signal(false);
  readonly form = this.fb.nonNullable.group({
    first_name: '',
    last_name: '',
    phone: '',
    email: '',
    password: '',
  });

  async submit(): Promise<void> {
    if (this.isSubmitting()) {
      return;
    }

    const result = RegisterFormSchema.safeParse(this.form.getRawValue());
    if (!result.success) {
      this.toast.showErrorList(result.error.issues.map((issue) => issue.message));
      return;
    }

    this.isSubmitting.set(true);

    try {
      const response = await this.authActions.register(result.data);

      if (!response.ok) {
        this.toast.showErrorList(response.errors);
        return;
      }

      this.form.reset({
        first_name: '',
        last_name: '',
        phone: '',
        email: '',
        password: '',
      });
      this.toast.success('Cuenta creada correctamente');
    } finally {
      this.isSubmitting.set(false);
    }
  }
}
