import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';

import { formatUtcDateToLocal } from '../../../shared/data/infrastructure/date-time';
import { CircularProgressLoaderComponent } from '../../../shared/presentation/components/loaders/circular-progress-loader.component';
import { PrimaryCardComponent } from '../../../shared/presentation/components/cards/primary-card.component';

@Component({
  selector: 'app-wallet-balance-card',
  standalone: true,
  imports: [CommonModule, PrimaryCardComponent, CircularProgressLoaderComponent],
  template: `
    <app-primary-card customClass="h-full">
      <p class="text-xs uppercase tracking-wide text-[var(--auth-text-secondary)]">Saldo del taller</p>

      <h3 class="mt-2 text-3xl font-semibold text-[var(--app-text-primary)] sm:text-4xl">
        <span *ngIf="!isLoading">{{ formatAmount(balance) }}</span>
        <app-circular-progress-loader
          *ngIf="isLoading"
          [size]="34"
          label="Cargando saldo"
          colorClass="border-slate-600"
        />
      </h3>

      <p class="mt-3 text-sm text-[var(--auth-text-secondary)]">
        Ultima actualizacion: {{ formatDate(updatedAt) }}
      </p>
    </app-primary-card>
  `,
})
export class WalletBalanceCardComponent {
  @Input() balance = 0;
  @Input() updatedAt: string | null = null;
  @Input() isLoading = false;

  formatAmount(value: number): string {
    return `Bs ${value.toFixed(2)}`;
  }

  formatDate(value: string | null): string {
    return formatUtcDateToLocal(value);
  }
}
