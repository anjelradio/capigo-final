import { Component, EventEmitter, Output } from '@angular/core';

import { PrimaryActionButtonComponent } from '../../../shared/presentation/components/buttons/primary-action-button.component';
import { PrimaryCardComponent } from '../../../shared/presentation/components/cards/primary-card.component';

@Component({
  selector: 'app-wallet-topup-card',
  standalone: true,
  imports: [PrimaryCardComponent, PrimaryActionButtonComponent],
  template: `
    <app-primary-card customClass="h-full">
      <p class="text-xs uppercase tracking-wide text-[var(--auth-text-secondary)]">Recargar saldo</p>

      <h3 class="mt-2 text-xl font-semibold text-[var(--app-text-primary)]">Genera una recarga</h3>

      <p class="mt-2 text-sm text-[var(--auth-text-secondary)]">
        Aqui podras registrar una recarga para aumentar el saldo de la billetera del taller.
      </p>

      <div class="mt-6">
        <app-primary-action-button
          label="Recargar saldo"
          customClass="!h-11 !w-auto !rounded-full !px-5"
          (pressed)="topupClick.emit()"
        />
      </div>
    </app-primary-card>
  `,
})
export class WalletTopupCardComponent {
  @Output() topupClick = new EventEmitter<void>();
}
