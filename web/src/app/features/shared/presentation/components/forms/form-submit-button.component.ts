import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-form-submit-button',
  standalone: true,
  imports: [CommonModule],
  template: `
    <button
      [attr.type]="type"
      [disabled]="disabled || loading"
      [attr.aria-disabled]="disabled || loading"
      class="inline-flex h-12 w-full items-center justify-center rounded-[var(--auth-control-radius)] bg-[var(--auth-button-bg)] px-4 py-2 text-sm font-semibold text-[var(--auth-button-text)] transition hover:bg-[var(--auth-button-hover)] disabled:cursor-not-allowed disabled:opacity-60"
      [ngClass]="customClass"
    >
      {{ loading ? loadingLabel : label }}
    </button>
  `,
})
export class FormSubmitButtonComponent {
  @Input() loading = false;
  @Input() disabled = false;
  @Input() label = 'Enviar';
  @Input() loadingLabel = 'Procesando...';
  @Input() type: 'submit' | 'button' | 'reset' = 'submit';
  @Input() customClass = '';
}
