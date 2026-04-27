import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';

import { formatUtcDateToLocal } from '../../../../shared/data/infrastructure/date-time';
import type { AdminRepairShopData } from '../../../data/schemas/repair-shop.schema';
import { CircularProgressLoaderComponent } from '../../../../shared/presentation/components/loaders/circular-progress-loader.component';

@Component({
  selector: 'app-admin-repair-shops-list',
  standalone: true,
  imports: [CommonModule, CircularProgressLoaderComponent],
  template: `
    <section class="mt-6 grid gap-4">
      <div *ngIf="isLoading" class="flex items-center justify-center py-8">
        <app-circular-progress-loader [size]="40" label="Cargando talleres" />
      </div>

      <ng-container *ngIf="!isLoading">
        <article
          *ngFor="let shop of shops; trackBy: trackByShopId"
          class="rounded-2xl border border-[var(--app-card-soft-border)] bg-[var(--app-card-bg)] p-5 shadow-sm"
        >
          <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p class="text-xs uppercase tracking-wide text-[var(--auth-text-secondary)]">Taller</p>
              <h4 class="text-lg font-semibold text-[var(--app-text-primary)]">{{ shop.name }}</h4>
              <p class="mt-1 text-sm text-[var(--auth-text-secondary)]">{{ shop.text_address }}</p>
            </div>

            <div class="flex flex-wrap items-center gap-2">
              <span class="inline-flex rounded-full px-3 py-1 text-xs font-semibold" [ngClass]="stateClass(shop.state)">
                {{ shop.state ? 'Activo' : 'Inactivo' }}
              </span>
              <span
                class="inline-flex rounded-full px-3 py-1 text-xs font-semibold"
                [ngClass]="shop.is_available ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-200 text-slate-700'"
              >
                {{ shop.is_available ? 'Disponible' : 'No disponible' }}
              </span>
              <button
                type="button"
                class="inline-flex items-center justify-center rounded-full bg-[var(--app-accent)] px-4 py-2 text-sm font-semibold text-[var(--app-accent-text)] transition hover:brightness-105"
                (click)="viewDetail.emit(shop.id)"
              >
                Ver detalle
              </button>
            </div>
          </div>

          <div class="mt-4 grid gap-2 text-sm text-[var(--auth-text-secondary)] sm:grid-cols-2 lg:grid-cols-3">
            <p><strong class="text-[var(--app-text-primary)]">Propietario:</strong> {{ shop.owner_name }}</p>
            <p><strong class="text-[var(--app-text-primary)]">Correo:</strong> {{ shop.owner_email }}</p>
            <p><strong class="text-[var(--app-text-primary)]">Creado:</strong> {{ formatDate(shop.created_date) }}</p>
            <p *ngIf="!shop.state" class="sm:col-span-2 lg:col-span-3">
              <strong class="text-[var(--app-text-primary)]">Desactivado:</strong>
              {{ formatDate(shop.deleted_date) }}
            </p>
          </div>
        </article>
      </ng-container>

      <article
        *ngIf="!isLoading && shops.length === 0"
        class="rounded-2xl border border-dashed border-[var(--app-card-soft-border)] bg-[var(--app-card-soft-bg)] p-6 text-center text-sm text-[var(--auth-text-secondary)]"
      >
        No hay talleres registrados.
      </article>
    </section>
  `,
})
export class AdminRepairShopsListComponent {
  @Input() shops: AdminRepairShopData[] = [];
  @Input() isLoading = false;

  @Output() viewDetail = new EventEmitter<string>();

  trackByShopId(_: number, shop: AdminRepairShopData): string {
    return shop.id;
  }

  formatDate(value: string | null | undefined): string {
    return formatUtcDateToLocal(value);
  }

  stateClass(state: boolean): string {
    return state ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-200 text-slate-700';
  }
}
