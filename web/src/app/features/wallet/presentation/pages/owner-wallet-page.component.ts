import { Component, inject, signal } from '@angular/core';

import { AppToastService } from '../../../../core/services/app-toast.service';
import { HomeHeaderComponent } from '../../../home/presentation/components/home-header/home-header.component';
import { PageHeadingComponent } from '../../../shared/presentation/components/layout/page-heading.component';
import { WalletRepository } from '../../data/repositories/wallet.repository';
import type { OwnerWalletBalance, OwnerWalletTransaction } from '../../domain/entities/wallet';
import { WalletBalanceCardComponent } from '../components/wallet-balance-card.component';
import { WalletTopupModalComponent } from '../components/wallet-topup-modal.component';
import { WalletTopupCardComponent } from '../components/wallet-topup-card.component';
import { WalletTransactionsListComponent } from '../components/wallet-transactions-list.component';

@Component({
  selector: 'app-owner-wallet-page',
  standalone: true,
  imports: [
    HomeHeaderComponent,
    PageHeadingComponent,
    WalletBalanceCardComponent,
    WalletTopupCardComponent,
    WalletTopupModalComponent,
    WalletTransactionsListComponent,
  ],
  template: `
    <main class="app-dashboard-bg min-h-screen">
      <app-home-header />

      <section class="mx-auto w-full max-w-[1500px] px-4 pb-10 pt-6 sm:px-6">
        <app-page-heading
          title="Saldo"
          subtitle="Aqui podras consultar el saldo y el historial de transacciones de tu taller."
        />

        <section class="mt-6 grid gap-4 lg:grid-cols-2">
          <app-wallet-balance-card
            [balance]="walletBalance()?.balance ?? 0"
            [updatedAt]="walletBalance()?.updatedAt ?? null"
            [isLoading]="isLoadingBalance()"
          />

          <app-wallet-topup-card (topupClick)="openTopupModal()" />
        </section>

        <app-wallet-transactions-list
          [transactions]="transactions()"
          [isLoading]="isLoadingTransactions()"
        />

        <app-wallet-topup-modal
          [open]="isTopupModalOpen()"
          (openChange)="setTopupModalOpen($event)"
          (topupConfirmed)="handleTopupConfirmed()"
        />
      </section>
    </main>
  `,
})
export class OwnerWalletPageComponent {
  private readonly walletRepository = inject(WalletRepository);
  private readonly appToast = inject(AppToastService);

  readonly walletBalance = signal<OwnerWalletBalance | null>(null);
  readonly transactions = signal<OwnerWalletTransaction[]>([]);
  readonly isLoadingBalance = signal(false);
  readonly isLoadingTransactions = signal(false);
  readonly isTopupModalOpen = signal(false);

  constructor() {
    void this.loadData();
  }

  private async loadData(): Promise<void> {
    await Promise.all([this.loadBalance(), this.loadTransactions()]);
  }

  openTopupModal(): void {
    this.isTopupModalOpen.set(true);
  }

  setTopupModalOpen(open: boolean): void {
    this.isTopupModalOpen.set(open);
  }

  async handleTopupConfirmed(): Promise<void> {
    await this.loadData();
  }

  private async loadBalance(): Promise<void> {
    this.isLoadingBalance.set(true);
    const response = await this.walletRepository.getMyWalletBalance();
    this.isLoadingBalance.set(false);

    if (!response.ok) {
      this.appToast.showErrorList(response.errors);
      return;
    }

    this.walletBalance.set(response.data);
  }

  private async loadTransactions(): Promise<void> {
    this.isLoadingTransactions.set(true);
    const response = await this.walletRepository.listMyWalletTransactions();
    this.isLoadingTransactions.set(false);

    if (!response.ok) {
      this.appToast.showErrorList(response.errors);
      return;
    }

    this.transactions.set(response.data);
  }
}
