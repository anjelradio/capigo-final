import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';

@Component({
  selector: 'app-primary-action-button',
  standalone: true,
  imports: [CommonModule],
  template: `
    <button
      type="button"
      [disabled]="disabled"
      [ngClass]="customClass"
      class="inline-flex h-12 w-full items-center justify-center rounded-[var(--auth-control-radius)] bg-[var(--auth-button-bg)] px-4 py-2 text-sm font-semibold text-[var(--auth-button-text)] transition hover:bg-[var(--auth-button-hover)] disabled:cursor-not-allowed disabled:opacity-60"
      (click)="pressed.emit()"
    >
      {{ label }}
    </button>
  `,
})
export class PrimaryActionButtonComponent {
  @Input() label = 'Accion';
  @Input() disabled = false;
  @Input() customClass = '';

  @Output() pressed = new EventEmitter<void>();
}
