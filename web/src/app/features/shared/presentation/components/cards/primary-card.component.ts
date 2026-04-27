import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';

type PrimaryCardVariant = 'default' | 'yellow' | 'aqua';

@Component({
  selector: 'app-primary-card',
  standalone: true,
  imports: [CommonModule],
  template: `
    <article
      class="rounded-[28px] p-5 shadow-sm"
      [ngClass]="[resolvedBackgroundClass, resolvedTextClass, resolvedBorderClass, customClass]"
    >
      <ng-content />
    </article>
  `,
})
export class PrimaryCardComponent {
  @Input() variant: PrimaryCardVariant = 'default';
  @Input() backgroundClass = '';
  @Input() textClass = '';
  @Input() borderClass = '';
  @Input() customClass = '';

  get resolvedBackgroundClass(): string {
    if (this.backgroundClass) {
      return this.backgroundClass;
    }

    switch (this.variant) {
      case 'yellow':
        return 'bg-[var(--dashboard-card-yellow)]';
      case 'aqua':
        return 'bg-[var(--dashboard-card-aqua)]';
      default:
        return 'bg-[var(--dashboard-card-default)]';
    }
  }

  get resolvedTextClass(): string {
    if (this.textClass) {
      return this.textClass;
    }

    return 'text-[var(--app-text-primary)]';
  }

  get resolvedBorderClass(): string {
    if (this.borderClass) {
      return this.borderClass;
    }

    return 'border border-[var(--dashboard-card-default-border)]';
  }
}
