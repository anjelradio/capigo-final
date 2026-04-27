import { Component, EventEmitter, Input, Output, inject, signal } from '@angular/core';

import { AppToastService } from '../../../../../core/services/app-toast.service';
import { FormSubmitButtonComponent } from '../../../../shared/presentation/components/forms/form-submit-button.component';
import { AppModalComponent } from '../../../../shared/presentation/components/modals/app-modal.component';
import { AdminRepairShopActionsService } from '../../actions/repair-shop/admin-repair-shop-actions.service';
import { RepairShopActionsService } from '../../actions/repair-shop/repair-shop-actions.service';

@Component({
  selector: 'app-delete-shop-mechanic-trigger',
  standalone: true,
  imports: [AppModalComponent, FormSubmitButtonComponent],
  template: `
    <button
      type="button"
      class="inline-flex items-center gap-1 rounded-full border border-rose-300 px-3 py-1 text-xs font-semibold text-rose-700 transition hover:bg-rose-50"
      (click)="openModal()"
    >
      <svg viewBox="0 0 24 24" class="h-3.5 w-3.5" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
        <path d="M3 6h18" />
        <path d="M8 6V4h8v2" />
        <path d="M19 6l-1 14H6L5 6" />
        <path d="M10 11v6" />
        <path d="M14 11v6" />
      </svg>
      Eliminar
    </button>

    <app-modal
      [open]="isModalOpen()"
      [showCloseButton]="false"
      [panelClass]="'max-w-md'"
      (openChange)="onModalChange($event)"
    >
      <section class="space-y-5 px-6 py-6">
        <header class="space-y-2">
          <h3 class="text-xl font-semibold text-[var(--app-text-primary)]">Eliminar mecanico</h3>
          <p class="text-sm text-[var(--auth-text-secondary)]">
            Se desvinculara a <strong>{{ mechanicName }}</strong> del taller. Esta accion cambiara su rol a cliente.
          </p>
        </header>

        <div class="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
          <button
            type="button"
            class="h-11 rounded-full border border-[var(--app-card-soft-border)] px-4 text-sm font-medium text-[var(--app-text-primary)] transition hover:bg-[var(--app-card-soft-bg)]"
            [disabled]="isDeleting()"
            (click)="closeModal()"
          >
            Cancelar
          </button>
          <app-form-submit-button
            [type]="'button'"
            [loading]="isDeleting()"
            label="Eliminar"
            loadingLabel="Eliminando..."
            customClass="sm:w-auto sm:min-w-[140px]"
            (click)="confirmDelete()"
          />
        </div>
      </section>
    </app-modal>
  `,
})
export class DeleteShopMechanicTriggerComponent {
  private readonly repairShopActions = inject(RepairShopActionsService);
  private readonly adminRepairShopActions = inject(AdminRepairShopActionsService);
  private readonly appToast = inject(AppToastService);

  @Input({ required: true }) mechanicId!: string;
  @Input({ required: true }) mechanicName!: string;
  @Input() shopId: string | null = null;
  @Input() isAdminContext = false;

  @Output() deleted = new EventEmitter<void>();

  readonly isModalOpen = signal(false);
  readonly isDeleting = signal(false);

  openModal(): void {
    this.isModalOpen.set(true);
  }

  onModalChange(open: boolean): void {
    this.isModalOpen.set(open);
  }

  closeModal(): void {
    if (this.isDeleting()) {
      return;
    }

    this.isModalOpen.set(false);
  }

  async confirmDelete(): Promise<void> {
    if (this.isDeleting()) {
      return;
    }

    this.isDeleting.set(true);
    const response = this.isAdminContext && this.shopId
      ? await this.adminRepairShopActions.deleteShopMechanic(this.shopId, this.mechanicId)
      : await this.repairShopActions.deleteMyShopMechanic(this.mechanicId);
    this.isDeleting.set(false);

    if (!response.ok) {
      this.appToast.showErrorList(response.errors);
      return;
    }

    this.appToast.success('Mecanico desvinculado correctamente');
    this.isModalOpen.set(false);
    this.deleted.emit();
  }
}
