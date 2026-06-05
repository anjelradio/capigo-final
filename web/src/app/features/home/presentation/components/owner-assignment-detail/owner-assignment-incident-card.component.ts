import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';

import type { IncidentActivityEvent } from '../../../../realtime/domain/entities/incident-activity';
import type { OwnerOfferDetail } from '../../../../realtime/domain/entities/owner-offer';
import { OfferEvidenceCarouselComponent } from '../../../../realtime/presentation/components/offer-evidence-carousel.component';

@Component({
  selector: 'app-owner-assignment-incident-card',
  standalone: true,
  imports: [CommonModule, OfferEvidenceCarouselComponent],
  template: `
    <article class="rounded-2xl border border-[var(--app-card-soft-border)] bg-[var(--app-card-bg)]/95 p-4 shadow-xl backdrop-blur-sm">
      <div *ngIf="canSubmitOffer" class="mb-3">
        <button
          type="button"
          class="w-full rounded-xl bg-amber-400 px-4 py-2 text-sm font-extrabold text-amber-950 transition hover:brightness-95 disabled:cursor-not-allowed disabled:opacity-60"
          [disabled]="isSubmitting"
          (click)="submitOffer.emit()"
        >
          {{ isSubmitting ? 'Enviando oferta...' : 'Enviar oferta' }}
        </button>
      </div>

      <hr *ngIf="canSubmitOffer" class="mb-3 border-[var(--app-card-soft-border)]" />

      <p class="text-xs uppercase tracking-wide text-[var(--auth-text-secondary)]">Detalle del incidente</p>
      <h3 class="mt-1 text-lg font-semibold text-[var(--app-text-primary)]">
        {{ detail?.problemName || 'Incidente clasificado' }}
      </h3>
      <p class="mt-2 text-sm text-[var(--auth-text-secondary)]">
        {{ detail?.incidentDescription || 'Sin descripcion enviada por el cliente.' }}
      </p>

      <div class="mt-4 grid grid-cols-2 gap-2 text-xs text-[var(--auth-text-secondary)]">
        <p><strong class="text-[var(--app-text-primary)]">Distancia:</strong> {{ formatDistance(detail?.distanceKm) }}</p>
        <p><strong class="text-[var(--app-text-primary)]">Delivery:</strong> {{ formatPrice(detail?.deliveryPrice) }}</p>
        <p><strong class="text-[var(--app-text-primary)]">Oferta:</strong> {{ formatPrice(detail?.quotedPrice) }}</p>
        <p class="flex items-center gap-2">
          <strong class="text-[var(--app-text-primary)]">Estado:</strong>
          <span
            class="inline-flex rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide"
            [ngClass]="statusBadgeClass(detailStatusRaw)"
          >
            {{ detailStatus || 'sin estado' }}
          </span>
        </p>
      </div>

      <div class="mt-4">
        <app-offer-evidence-carousel [images]="detail?.evidenceUrls ?? []" />
      </div>

      <div *ngIf="showTimeline" class="mt-4">
        <hr class="mb-3 border-[var(--app-card-soft-border)]" />
        <p class="text-xs uppercase tracking-wide text-[var(--auth-text-secondary)]">Actualizaciones en tiempo real</p>
        <div class="mt-2 max-h-44 space-y-2 overflow-y-auto pr-1">
          <article
            *ngFor="let event of events; trackBy: trackByEvent"
            class="rounded-xl border border-[var(--app-card-soft-border)] bg-[var(--app-card-soft-bg)] px-3 py-2"
          >
            <p class="text-xs font-semibold uppercase text-[var(--app-text-primary)]">{{ eventTypeLabel(event.type) }}</p>
            <p class="mt-1 text-xs text-[var(--auth-text-secondary)]">{{ event.createdAt }}</p>
          </article>

          <article
            *ngIf="events.length === 0"
            class="rounded-xl border border-dashed border-[var(--app-card-soft-border)] bg-[var(--app-card-soft-bg)] px-3 py-3 text-sm text-[var(--auth-text-secondary)]"
          >
            Aun no hay eventos para mostrar.
          </article>
        </div>
      </div>
    </article>
  `,
})
export class OwnerAssignmentIncidentCardComponent {
  @Input() detail: OwnerOfferDetail | null = null;
  @Input() detailStatus = '';
  @Input() detailStatusRaw: string | null = null;
  @Input() canSubmitOffer = false;
  @Input() isSubmitting = false;
  @Input() showTimeline = false;
  @Input() events: IncidentActivityEvent[] = [];

  @Output() submitOffer = new EventEmitter<void>();

  formatDistance(distanceKm?: number | null): string {
    if (distanceKm === null || distanceKm === undefined) return 'No disponible';
    return `${distanceKm.toFixed(2)} km`;
  }

  formatPrice(price?: number | null): string {
    if (price === null || price === undefined) return 'No disponible';
    return `Bs ${price.toFixed(2)}`;
  }

  trackByEvent(_: number, event: IncidentActivityEvent): string {
    return event.id;
  }

  eventTypeLabel(type: string): string {
    return type
      .split('.')
      .map((part) => part.replaceAll('_', ' '))
      .join(' - ');
  }

  statusBadgeClass(status: string | null): string {
    const normalized = (status || '').trim().toLowerCase();
    if (normalized === 'completed') return 'bg-emerald-100 text-emerald-800';
    if (normalized === 'cancelled' || normalized === 'failed') return 'bg-rose-100 text-rose-800';
    if (normalized === 'accepted' || normalized === 'assigned') return 'bg-sky-100 text-sky-800';
    if (normalized === 'on_the_way' || normalized === 'arrived') return 'bg-indigo-100 text-indigo-800';
    if (normalized === 'offered') return 'bg-amber-100 text-amber-900';
    return 'bg-slate-200 text-slate-800';
  }
}
