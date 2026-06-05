import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';

import type { ShopMechanicData } from '../../../repair-shop/data/schemas/repair-shop.schema';
import { AppModalComponent } from '../../../shared/presentation/components/modals/app-modal.component';

@Component({
  selector: 'app-offer-mechanic-assignment-modal',
  standalone: true,
  imports: [CommonModule, AppModalComponent],
  template: `
    <app-modal [open]="open" [panelClass]="'max-w-2xl'" (openChange)="onOpenChange($event)">
      <section class="space-y-4 px-6 py-6">
        <header class="space-y-1">
          <p class="text-xs font-semibold uppercase tracking-wide text-[var(--auth-text-secondary)]">
            Enviar oferta
          </p>
          <h3 class="text-2xl font-semibold text-[var(--app-text-primary)]">
            Define cotizacion y mecanico propuesto
          </h3>
        </header>

        <div>
          <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-[var(--auth-text-secondary)]">
            Precio ofertado (Bs)
          </label>
          <input
            type="number"
            min="0"
            step="0.01"
            [value]="quotedPrice"
            (input)="onQuotedPriceChange($event)"
            class="w-full rounded-xl border border-[var(--app-card-soft-border)] bg-[var(--app-card-soft-bg)] px-3 py-2 text-sm text-[var(--app-text-primary)] outline-none focus:border-[var(--app-accent)]"
            placeholder="Ej. 120"
          />
        </div>

        <div class="max-h-64 space-y-2 overflow-y-auto pr-1">
          <p class="text-xs font-semibold uppercase tracking-wide text-[var(--auth-text-secondary)]">
            Selecciona mecanico
          </p>
          <label
            *ngFor="let mechanic of mechanics"
            class="flex cursor-pointer items-center justify-between rounded-xl border border-[var(--app-card-soft-border)] bg-[var(--app-card-soft-bg)] px-4 py-3"
          >
            <div>
              <p class="text-sm font-semibold text-[var(--app-text-primary)]">
                {{ mechanic.user.first_name }} {{ mechanic.user.last_name }}
              </p>
              <p class="text-xs text-[var(--auth-text-secondary)]">{{ mechanic.user.phone }}</p>
            </div>

            <input
              type="radio"
              name="selected-mechanic"
              [value]="mechanic.id"
              [checked]="selectedMechanicId === mechanic.id"
              (change)="onSelect(mechanic.id)"
              class="h-4 w-4 accent-[var(--app-accent)]"
            />
          </label>

          <article
            *ngIf="mechanics.length === 0"
            class="rounded-xl border border-dashed border-[var(--app-card-soft-border)] bg-[var(--app-card-soft-bg)] p-4 text-sm text-[var(--auth-text-secondary)]"
          >
            No hay mecanicos disponibles en este momento.
          </article>
        </div>

        <footer class="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
          <button
            type="button"
            class="inline-flex items-center justify-center rounded-full border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
            [disabled]="isSubmitting"
            (click)="onCancel()"
          >
            Cancelar
          </button>
          <button
            type="button"
            class="inline-flex items-center justify-center rounded-full bg-[var(--app-accent)] px-4 py-2 text-sm font-semibold text-[var(--app-accent-text)] transition hover:brightness-105 disabled:cursor-not-allowed disabled:opacity-60"
            [disabled]="isSubmitting || !selectedMechanicId || !quotedPrice"
            (click)="onAssign()"
          >
            {{ isSubmitting ? 'Enviando...' : 'Enviar oferta' }}
          </button>
        </footer>
      </section>
    </app-modal>
  `,
})
export class OfferMechanicAssignmentModalComponent {
  @Input() open = false;
  @Input() mechanics: ShopMechanicData[] = [];
  @Input() selectedMechanicId: string | null = null;
  @Input() quotedPrice = '';
  @Input() isSubmitting = false;

  @Output() openChange = new EventEmitter<boolean>();
  @Output() selectedMechanicIdChange = new EventEmitter<string>();
  @Output() quotedPriceChange = new EventEmitter<string>();
  @Output() assign = new EventEmitter<void>();

  onOpenChange(open: boolean): void {
    this.openChange.emit(open);
  }

  onSelect(mechanicId: string): void {
    this.selectedMechanicIdChange.emit(mechanicId);
  }

  onQuotedPriceChange(event: Event): void {
    const target = event.target as HTMLInputElement | null;
    this.quotedPriceChange.emit(target?.value ?? '');
  }

  onCancel(): void {
    this.openChange.emit(false);
  }

  onAssign(): void {
    this.assign.emit();
  }
}
