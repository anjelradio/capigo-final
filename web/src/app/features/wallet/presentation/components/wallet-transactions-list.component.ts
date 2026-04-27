import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';

import { formatUtcDateToLocal } from '../../../shared/data/infrastructure/date-time';
import { CircularProgressLoaderComponent } from '../../../shared/presentation/components/loaders/circular-progress-loader.component';
import type { OwnerWalletTransaction } from '../../domain/entities/wallet';

@Component({
  selector: 'app-wallet-transactions-list',
  standalone: true,
  imports: [CommonModule, CircularProgressLoaderComponent],
  template: `
    <section class="mt-8 grid gap-4">
      <div class="flex items-center justify-between">
        <h3 class="text-base font-semibold uppercase tracking-wide text-[var(--app-accent)]">
          Transacciones
        </h3>
      </div>

      <div *ngIf="isLoading" class="flex items-center justify-center py-8">
        <app-circular-progress-loader [size]="40" label="Cargando transacciones" />
      </div>

      <ng-container *ngIf="!isLoading">
        <article
          *ngFor="let tx of transactions; trackBy: trackByTransactionId"
          class="rounded-2xl border border-[var(--app-card-soft-border)] bg-[var(--app-card-bg)] p-5 shadow-sm"
        >
          <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h4 class="mt-1 text-base font-semibold text-[var(--app-text-primary)]">
                {{ tx.description || 'Transaccion sin descripcion' }}
              </h4>
              <p class="mt-1 text-xs text-[var(--auth-text-secondary)]">{{ mapTypeDescription(tx.type) }}</p>
            </div>

            <div class="flex flex-wrap items-center gap-2">
              <span class="inline-flex rounded-full px-3 py-1 text-xs font-semibold" [ngClass]="typeClass(tx.type)">
                {{ mapTypeLabel(tx.type) }}
              </span>
              <span class="inline-flex rounded-full px-3 py-1 text-xs font-semibold" [ngClass]="statusClass(tx.status)">
                {{ mapStatusLabel(tx.status) }}
              </span>
            </div>
          </div>

          <p class="mt-3 text-xs text-[var(--auth-text-secondary)]">Estado: {{ mapStatusDescription(tx.status) }}</p>

          <div class="mt-4 grid gap-2 text-sm text-[var(--auth-text-secondary)] sm:grid-cols-2 lg:grid-cols-5">
            <p>
              <strong class="text-[var(--app-text-primary)]">Monto:</strong>
              <span [ngClass]="amountClass(tx)">{{ formatSignedAmount(tx) }}</span>
            </p>
            <p>
              <strong class="text-[var(--app-text-primary)]">Variacion:</strong>
              <span [ngClass]="balanceChangeClass(tx)">{{ formatBalanceChange(tx) }}</span>
            </p>
            <p>
              <strong class="text-[var(--app-text-primary)]">Antes:</strong> {{ formatAmount(tx.balanceBefore) }}
            </p>
            <p>
              <strong class="text-[var(--app-text-primary)]">Despues:</strong> {{ formatAmount(tx.balanceAfter) }}
            </p>
            <p>
              <strong class="text-[var(--app-text-primary)]">Fecha:</strong> {{ formatDate(tx.createdAt) }}
            </p>
            <p class="sm:col-span-2 lg:col-span-5">
              <strong class="text-[var(--app-text-primary)]">ID:</strong> {{ tx.id }}
            </p>
          </div>
        </article>
      </ng-container>

      <article
        *ngIf="!isLoading && transactions.length === 0"
        class="rounded-2xl border border-dashed border-[var(--app-card-soft-border)] bg-[var(--app-card-soft-bg)] p-6 text-center text-sm text-[var(--auth-text-secondary)]"
      >
        Aun no hay transacciones registradas en la billetera.
      </article>
    </section>
  `,
})
export class WalletTransactionsListComponent {
  @Input() transactions: OwnerWalletTransaction[] = [];
  @Input() isLoading = false;

  trackByTransactionId(_: number, tx: OwnerWalletTransaction): string {
    return tx.id;
  }

  formatAmount(value: number): string {
    return `Bs ${value.toFixed(2)}`;
  }

  formatDate(value: string): string {
    return formatUtcDateToLocal(value);
  }

  formatSignedAmount(tx: OwnerWalletTransaction): string {
    const signedAmount = this.signedAmount(tx);
    if (signedAmount === 0) {
      return `Bs ${signedAmount.toFixed(2)}`;
    }

    const sign = signedAmount > 0 ? '+' : '-';
    return `${sign}Bs ${Math.abs(signedAmount).toFixed(2)}`;
  }

  amountClass(tx: OwnerWalletTransaction): string {
    const signedAmount = this.signedAmount(tx);
    if (signedAmount > 0) {
      return 'text-emerald-700 font-semibold';
    }
    if (signedAmount < 0) {
      return 'text-rose-700 font-semibold';
    }
    return 'text-slate-700 font-semibold';
  }

  formatBalanceChange(tx: OwnerWalletTransaction): string {
    const change = tx.balanceAfter - tx.balanceBefore;
    if (change === 0) {
      return `Bs ${change.toFixed(2)}`;
    }

    const sign = change > 0 ? '+' : '-';
    return `${sign}Bs ${Math.abs(change).toFixed(2)}`;
  }

  balanceChangeClass(tx: OwnerWalletTransaction): string {
    const change = tx.balanceAfter - tx.balanceBefore;
    if (change > 0) {
      return 'text-emerald-700 font-semibold';
    }
    if (change < 0) {
      return 'text-rose-700 font-semibold';
    }
    return 'text-slate-700 font-semibold';
  }

  mapTypeLabel(type: string): string {
    if (type === 'topup') {
      return 'Recarga';
    }
    if (type === 'debit_service') {
      return 'Debito por servicio';
    }
    if (type === 'refund') {
      return 'Reembolso';
    }
    if (type === 'adjustment') {
      return 'Ajuste';
    }
    return type;
  }

  mapTypeDescription(type: string): string {
    if (type === 'topup') {
      return 'Ingreso de fondos mediante recarga a la billetera.';
    }
    if (type === 'debit_service') {
      return 'Cobro aplicado por servicios realizados desde la plataforma.';
    }
    if (type === 'refund') {
      return 'Devolucion de fondos aplicada nuevamente al saldo.';
    }
    if (type === 'adjustment') {
      return 'Ajuste administrativo del saldo de la billetera.';
    }
    return 'Movimiento registrado en la billetera del taller.';
  }

  typeClass(type: string): string {
    if (type === 'topup') {
      return 'bg-sky-100 text-sky-800';
    }
    if (type === 'debit_service') {
      return 'bg-amber-100 text-amber-900';
    }
    if (type === 'refund') {
      return 'bg-emerald-100 text-emerald-800';
    }
    if (type === 'adjustment') {
      return 'bg-slate-200 text-slate-800';
    }
    return 'bg-slate-100 text-slate-700';
  }

  mapStatusLabel(status: string): string {
    if (status === 'posted') {
      return 'Registrada';
    }
    if (status === 'pending') {
      return 'Pendiente';
    }
    if (status === 'failed') {
      return 'Fallida';
    }
    if (status === 'reversed') {
      return 'Revertida';
    }
    return status;
  }

  mapStatusDescription(status: string): string {
    if (status === 'posted') {
      return 'Movimiento confirmado y reflejado en el saldo.';
    }
    if (status === 'pending') {
      return 'Movimiento creado, aun pendiente de confirmacion.';
    }
    if (status === 'failed') {
      return 'El movimiento fallo y no impacto en el saldo.';
    }
    if (status === 'reversed') {
      return 'Movimiento revertido luego de haberse registrado.';
    }
    return 'Estado no reconocido para esta transaccion.';
  }

  statusClass(status: string): string {
    if (status === 'posted') {
      return 'bg-emerald-100 text-emerald-800';
    }
    if (status === 'pending') {
      return 'bg-amber-100 text-amber-900';
    }
    if (status === 'failed' || status === 'reversed') {
      return 'bg-rose-100 text-rose-800';
    }
    return 'bg-slate-100 text-slate-700';
  }

  private signedAmount(tx: OwnerWalletTransaction): number {
    if (tx.type === 'debit_service') {
      return -Math.abs(tx.amount);
    }
    if (tx.type === 'topup' || tx.type === 'refund') {
      return Math.abs(tx.amount);
    }

    const change = tx.balanceAfter - tx.balanceBefore;
    if (change === 0) {
      return tx.amount;
    }
    return change;
  }
}
