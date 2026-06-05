import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-owner-assignment-mechanic-card',
  standalone: true,
  imports: [CommonModule],
  template: `
    <article class="rounded-2xl border border-[var(--app-card-soft-border)] bg-[var(--app-card-bg)]/95 p-4 shadow-xl backdrop-blur-sm">
      <p class="text-xs uppercase tracking-wide text-[var(--auth-text-secondary)]">Mecanico</p>
      <h3 class="mt-1 text-base font-semibold text-[var(--app-text-primary)]">{{ mechanicName || 'Sin mecanico asociado' }}</h3>
      <p class="mt-1 text-sm text-[var(--auth-text-secondary)]">
        {{
          mechanicName
            ? 'Cuando el servicio este activo, aqui veras su estado en tiempo real.'
            : 'Aun no hay un mecanico vinculado para este incidente.'
        }}
      </p>
      <p *ngIf="mechanicName && statusLabel" class="mt-2 text-xs font-semibold uppercase tracking-wide text-[var(--auth-text-secondary)]">
        Estado actual: {{ statusLabel }}
      </p>
    </article>
  `,
})
export class OwnerAssignmentMechanicCardComponent {
  @Input() mechanicName: string | null = null;
  @Input() statusLabel: string | null = null;
}
