import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';

type PrimaryCardVariant = 'default' | 'yellow' | 'aqua' | 'soft-blue' | 'soft-sand';

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
      case 'soft-blue':
        return 'bg-[var(--dashboard-card-soft-blue)]';
      case 'soft-sand':
        return 'bg-[var(--dashboard-card-soft-sand)]';
      default:
        return 'bg-[var(--dashboard-card-default)]';
    }
  }

  get resolvedTextClass(): string {
    if (this.textClass) {
      return this.textClass;
    }

    if (this.variant === 'yellow') {
      return 'text-[var(--app-accent-text)]';
    }

    return 'text-[var(--app-text-primary)]';
  }

  get resolvedBorderClass(): string {
    if (this.borderClass) {
      return this.borderClass;
    }

    switch (this.variant) {
      case 'yellow':
        return 'border border-[var(--dashboard-card-yellow-border)]';
      case 'aqua':
        return 'border border-[var(--dashboard-card-aqua-border)]';
      case 'soft-blue':
        return 'border border-[var(--dashboard-card-soft-blue-border)]';
      case 'soft-sand':
        return 'border border-[var(--dashboard-card-soft-sand-border)]';
      default:
        return 'border border-[var(--dashboard-card-default-border)]';
    }
  }
}
