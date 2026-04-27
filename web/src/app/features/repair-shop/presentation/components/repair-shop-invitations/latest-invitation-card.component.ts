import { CommonModule } from '@angular/common';
import {
  Component,
  EventEmitter,
  Input,
  OnChanges,
  OnInit,
  Output,
  SimpleChanges,
  computed,
  inject,
  signal,
} from '@angular/core';
import { BadgeCheck, Copy, LucideAngularModule, Trash2 } from 'lucide-angular';

import { AppToastService } from '../../../../../core/services/app-toast.service';
import { PrimaryCardComponent } from '../../../../shared/presentation/components/cards/primary-card.component';
import { CircularProgressLoaderComponent } from '../../../../shared/presentation/components/loaders/circular-progress-loader.component';
import { RepairShopActionsService } from '../../actions/repair-shop/repair-shop-actions.service';

type InvitationSummary = {
  code: string;
  expires_at: string;
  expires_at_label: string;
  status: 'active' | 'expired';
};

@Component({
  selector: 'app-latest-invitation-card',
  standalone: true,
  imports: [CommonModule, PrimaryCardComponent, LucideAngularModule, CircularProgressLoaderComponent],
  template: `
    <app-primary-card
      variant="default"
      backgroundClass="bg-[var(--dashboard-card-soft-sand)]"
      customClass="h-full space-y-4"
    >
      <header class="flex items-center justify-between gap-3">
        <div>
          <h2 class="text-xl font-semibold text-[var(--auth-text-primary)]">
            Ultimo codigo creado
          </h2>
          <p class="mt-1 text-sm text-[var(--auth-text-secondary)]">
            Resumen del ultimo codigo de invitacion generado.
          </p>
        </div>
        <div
          class="grid h-11 w-11 place-items-center rounded-full bg-white/75 text-[var(--dashboard-nav-blue)]"
        >
          <lucide-angular [img]="statusIcon" [size]="20" />
        </div>
      </header>

      <div
        *ngIf="isLoading()"
        class="rounded-2xl border border-white/80 bg-white/80 px-4 py-3 text-sm text-slate-600"
      >
        <div class="flex items-center justify-center py-2">
          <app-circular-progress-loader
            [size]="34"
            label="Cargando invitacion"
            colorClass="border-slate-600"
          />
        </div>
      </div>

      <div
        *ngIf="!isLoading() && !invitationSummary()"
        class="rounded-2xl border border-white/80 bg-white/80 px-4 py-3 text-sm text-slate-600"
      >
        No hay ningun codigo creado aun.
      </div>

      <div
        *ngIf="!isLoading() && invitationSummary()"
        class="rounded-2xl border border-white/80 bg-white/80 px-4 py-3"
      >
        <div class="grid gap-3 sm:grid-cols-[1fr_1fr_0.8fr_auto] sm:items-end">
          <div>
            <p class="text-xs font-medium uppercase tracking-wide text-slate-500">Codigo</p>
            <p class="mt-1 text-sm font-semibold text-slate-700">{{ invitationSummary()?.code }}</p>
          </div>
          <div>
            <p class="text-xs font-medium uppercase tracking-wide text-slate-500">Expira</p>
            <p class="mt-1 text-sm font-semibold text-slate-700">
              {{ invitationSummary()?.expires_at_label }}
            </p>
          </div>
          <div>
            <p class="text-xs font-medium uppercase tracking-wide text-slate-500">Estado</p>
            <p
              class="mt-1 text-sm font-semibold"
              [ngClass]="
                invitationSummary()?.status === 'active' ? 'text-emerald-600' : 'text-amber-700'
              "
            >
              {{ invitationStatusLabel() }}
            </p>
          </div>
          <div class="sm:justify-self-end">
            <p class="text-xs font-medium uppercase tracking-wide text-slate-500">Acciones</p>
            <div class="mt-1 flex items-center gap-2 sm:justify-end">
              <button
                type="button"
                (click)="copyInvitationCode()"
                class="inline-flex h-9 items-center justify-center gap-1 rounded-full border border-[var(--dashboard-nav-blue)]/30 bg-white px-3.5 text-xs font-semibold text-[var(--dashboard-nav-blue)] transition hover:bg-[var(--dashboard-nav-blue)]/10"
              >
                <lucide-angular [img]="copyIcon" [size]="14" />
                Copiar
              </button>
              <button
                type="button"
                (click)="deleteInvitation()"
                [disabled]="isDeleting()"
                class="inline-flex h-9 items-center justify-center gap-1 rounded-full border border-red-300 bg-white px-3.5 text-xs font-semibold text-red-700 transition hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-70"
              >
                <lucide-angular [img]="deleteIcon" [size]="14" />
                Eliminar
              </button>
            </div>
          </div>
        </div>
      </div>
    </app-primary-card>
  `,
})
export class LatestInvitationCardComponent implements OnInit, OnChanges {
  private readonly repairShopActions = inject(RepairShopActionsService);
  private readonly toast = inject(AppToastService);

  @Input() refreshKey = 0;
  @Output() invitationChanged = new EventEmitter<void>();

  readonly statusIcon = BadgeCheck;
  readonly copyIcon = Copy;
  readonly deleteIcon = Trash2;

  readonly isLoading = signal(false);
  readonly isDeleting = signal(false);
  readonly invitationSummary = signal<InvitationSummary | null>(null);

  readonly invitationStatusLabel = computed(() =>
    this.invitationSummary()?.status === 'active' ? 'Activo' : 'Expirado',
  );

  async ngOnInit(): Promise<void> {
    await this.loadInvitationSummary();
  }

  async ngOnChanges(changes: SimpleChanges): Promise<void> {
    if (!changes['refreshKey'] || changes['refreshKey'].firstChange) {
      return;
    }

    await this.loadInvitationSummary();
  }

  async copyInvitationCode(): Promise<void> {
    const invitation = this.invitationSummary();
    if (!invitation) {
      this.toast.error('No hay codigo para copiar');
      return;
    }

    try {
      if (typeof navigator !== 'undefined' && navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(invitation.code);
      } else {
        throw new Error('Clipboard no disponible');
      }

      this.toast.success('Codigo copiado al portapapeles');
    } catch {
      this.toast.error('No se pudo copiar el codigo');
    }
  }

  async deleteInvitation(): Promise<void> {
    if (this.isDeleting()) {
      return;
    }

    this.isDeleting.set(true);
    try {
      const response = await this.repairShopActions.deleteMyShopInvitation();
      if (!response.ok) {
        this.toast.showErrorList(response.errors);
        return;
      }

      this.toast.success('Invitacion eliminada correctamente');
      await this.loadInvitationSummary();
      this.invitationChanged.emit();
    } finally {
      this.isDeleting.set(false);
    }
  }

  private async loadInvitationSummary(): Promise<void> {
    this.isLoading.set(true);
    try {
      const response = await this.repairShopActions.getMyShopInvitation();
      if (!response.ok) {
        this.toast.showErrorList(response.errors);
        return;
      }

      this.invitationSummary.set(response.data);
    } finally {
      this.isLoading.set(false);
    }
  }
}
