import { Component, EventEmitter, Output } from '@angular/core';
import { KeyRound, LucideAngularModule } from 'lucide-angular';

import { PrimaryCardComponent } from '../../../../shared/presentation/components/cards/primary-card.component';
import { GenerateInvitationTriggerComponent } from './generate-invitation-trigger.component';

@Component({
  selector: 'app-generate-invitation-card',
  standalone: true,
  imports: [PrimaryCardComponent, LucideAngularModule, GenerateInvitationTriggerComponent],
  template: `
    <app-primary-card
      variant="default"
      backgroundClass="bg-[var(--dashboard-card-soft-blue)]"
      customClass="h-full space-y-5"
    >
      <header class="flex items-center justify-between gap-3">
        <div>
          <h2 class="text-xl font-semibold text-[var(--auth-text-primary)]">Generar invitacion</h2>
          <p class="mt-1 text-sm text-[var(--auth-text-secondary)]">
            Crea codigos para vincular mecanicos a tu taller.
          </p>
        </div>
        <div
          class="grid h-11 w-11 place-items-center rounded-full bg-white/75 text-[var(--dashboard-nav-blue)]"
        >
          <lucide-angular [img]="keyIcon" [size]="20" />
        </div>
      </header>

      <app-generate-invitation-trigger (invitationCreated)="invitationCreated.emit()" />
    </app-primary-card>
  `,
})
export class GenerateInvitationCardComponent {
  readonly keyIcon = KeyRound;

  @Output() invitationCreated = new EventEmitter<void>();
}
