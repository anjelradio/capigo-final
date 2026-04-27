import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

import { AppToastService } from '../../../../core/services/app-toast.service';
import { formatUtcDateToLocal } from '../../../shared/data/infrastructure/date-time';
import type { OwnerWalletTopupQr } from '../../domain/entities/wallet';
import { WalletRepository } from '../../data/repositories/wallet.repository';
import { PrimaryActionButtonComponent } from '../../../shared/presentation/components/buttons/primary-action-button.component';
import { AppModalComponent } from '../../../shared/presentation/components/modals/app-modal.component';

@Component({
  selector: 'app-wallet-topup-modal',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    AppModalComponent,
    PrimaryActionButtonComponent,
  ],
  template: `
    <app-modal [open]="open" [panelClass]="'max-w-2xl'" (openChange)="onOpenChange($event)">
      <section class="space-y-5 px-6 py-6">
        <header>
          <p class="text-xs uppercase tracking-wide text-[var(--auth-text-secondary)]">Recargar saldo</p>
          <h3 class="mt-1 text-2xl font-semibold text-[var(--app-text-primary)]">Generar QR de recarga</h3>
          <p class="mt-2 text-sm text-[var(--auth-text-secondary)]">
            Define el monto a recargar y genera un QR demo con referencia interna.
          </p>
        </header>

        <form
          *ngIf="!topupQr()"
          [formGroup]="topupForm"
          (submit)="$event.preventDefault(); generateQr()"
          class="space-y-4"
        >
          <label class="grid gap-1">
            <span class="text-sm font-medium text-[var(--app-text-primary)]">Monto a recargar (Bs)</span>
            <input
              type="number"
              min="0.01"
              step="0.01"
              formControlName="amount"
              placeholder="Ej. 120.50"
              class="h-12 rounded-[var(--auth-control-radius)] border border-[var(--dashboard-card-default-border)] bg-white px-4 text-[var(--app-text-primary)] outline-none transition focus:border-[var(--app-accent)]"
            />
          </label>

          <p
            *ngIf="topupForm.controls.amount.invalid && topupForm.controls.amount.touched"
            class="text-sm text-rose-600"
          >
            Ingresa un monto valido mayor a 0.
          </p>

          <div class="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <button
              type="button"
              class="inline-flex items-center justify-center rounded-full border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
              [disabled]="isGeneratingQr()"
              (click)="close()"
            >
              Cancelar
            </button>
            <app-primary-action-button
              [label]="isGeneratingQr() ? 'Generando...' : 'Generar QR'"
              [disabled]="isGeneratingQr() || topupForm.invalid"
              customClass="!h-10 !w-auto !rounded-full !px-5"
              (pressed)="generateQr()"
            />
          </div>
        </form>

        <section *ngIf="topupQr() as qr" class="space-y-4">
          <div class="grid gap-3 sm:grid-cols-2">
            <article class="rounded-xl border border-[var(--app-card-soft-border)] bg-[var(--app-card-soft-bg)] p-4">
              <p class="text-xs uppercase tracking-wide text-[var(--auth-text-secondary)]">Monto</p>
              <p class="mt-1 text-lg font-semibold text-[var(--app-text-primary)]">{{ formatAmount(qr.amount) }}</p>
            </article>

            <article class="rounded-xl border border-[var(--app-card-soft-border)] bg-[var(--app-card-soft-bg)] p-4">
              <p class="text-xs uppercase tracking-wide text-[var(--auth-text-secondary)]">Referencia</p>
              <p class="mt-1 text-sm font-semibold text-[var(--app-text-primary)] break-all">{{ qr.internalReference }}</p>
            </article>
          </div>

          <div class="grid place-items-center rounded-2xl border border-[var(--app-card-soft-border)] bg-white p-5">
            <img [src]="qr.qrImageUrl" alt="QR de recarga" class="h-56 w-56" />
            <p class="mt-3 text-xs text-[var(--auth-text-secondary)]">ID transaccion: {{ qr.transactionId }}</p>
            <p class="text-xs text-[var(--auth-text-secondary)]">Generado: {{ formatDate(qr.generatedAt) }}</p>
          </div>

          <div class="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
            La recarga se encuentra pendiente. Presiona "Confirmar recarga" para simular su acreditacion.
          </div>

          <div class="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <button
              type="button"
              class="inline-flex items-center justify-center rounded-full border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
              [disabled]="isConfirmingTopup()"
              (click)="resetTopup()"
            >
              Nueva recarga
            </button>
            <app-primary-action-button
              [label]="isConfirmingTopup() ? 'Confirmando...' : 'Confirmar recarga'"
              [disabled]="isConfirmingTopup()"
              customClass="!h-10 !w-auto !rounded-full !px-5"
              (pressed)="confirmTopup()"
            />
          </div>
        </section>
      </section>
    </app-modal>
  `,
})
export class WalletTopupModalComponent {
  private readonly fb = inject(FormBuilder);
  private readonly walletRepository = inject(WalletRepository);
  private readonly appToast = inject(AppToastService);

  @Input() open = false;

  @Output() openChange = new EventEmitter<boolean>();
  @Output() topupConfirmed = new EventEmitter<void>();

  readonly topupForm = this.fb.nonNullable.group({
    amount: [0, [Validators.required, Validators.min(0.01)]],
  });

  readonly topupQr = signal<OwnerWalletTopupQr | null>(null);
  readonly isGeneratingQr = signal(false);
  readonly isConfirmingTopup = signal(false);

  onOpenChange(nextOpen: boolean): void {
    this.openChange.emit(nextOpen);
    if (!nextOpen) {
      this.resetState();
    }
  }

  close(): void {
    this.onOpenChange(false);
  }

  async generateQr(): Promise<void> {
    if (this.isGeneratingQr()) {
      return;
    }

    this.topupForm.controls.amount.markAsTouched();
    if (this.topupForm.invalid) {
      return;
    }

    const amountValue = this.topupForm.controls.amount.getRawValue();
    this.isGeneratingQr.set(true);
    const response = await this.walletRepository.createMyTopupQr(Number(amountValue));
    this.isGeneratingQr.set(false);

    if (!response.ok) {
      this.appToast.showErrorList(response.errors);
      return;
    }

    this.topupQr.set(response.data);
  }

  async confirmTopup(): Promise<void> {
    const qr = this.topupQr();
    if (!qr || this.isConfirmingTopup()) {
      return;
    }

    this.isConfirmingTopup.set(true);
    const response = await this.walletRepository.confirmMyTopup(qr.transactionId);
    this.isConfirmingTopup.set(false);

    if (!response.ok) {
      this.appToast.showErrorList(response.errors);
      return;
    }

    this.appToast.success(
      `Recarga confirmada. Nuevo saldo: ${this.formatAmount(response.data.newBalance)}`,
    );
    this.close();
    this.topupConfirmed.emit();
  }

  resetTopup(): void {
    this.topupQr.set(null);
    this.topupForm.reset({ amount: 0 });
  }

  formatAmount(value: number): string {
    return `Bs ${value.toFixed(2)}`;
  }

  formatDate(value: string): string {
    return formatUtcDateToLocal(value);
  }

  private resetState(): void {
    this.topupQr.set(null);
    this.topupForm.reset({ amount: 0 });
    this.isGeneratingQr.set(false);
    this.isConfirmingTopup.set(false);
  }
}
