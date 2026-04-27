import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-circular-progress-loader',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div
      class="inline-flex items-center justify-center"
      role="status"
      aria-live="polite"
      [attr.aria-label]="label"
    >
      <span
        class="inline-block animate-spin rounded-full border-4 border-t-transparent"
        [ngClass]="colorClass"
        [ngStyle]="{ width: sizePx, height: sizePx }"
      ></span>
    </div>
  `,
})
export class CircularProgressLoaderComponent {
  @Input() size = 34;
  @Input() label = 'Cargando';
  @Input() colorClass = 'border-[var(--app-accent)]';

  get sizePx(): string {
    return `${this.size}px`;
  }
}
