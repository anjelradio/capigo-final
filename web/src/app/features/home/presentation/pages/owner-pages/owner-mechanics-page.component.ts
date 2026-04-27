import { Component, signal } from '@angular/core';

import { PageHeadingComponent } from '../../../../../features/shared/presentation/components/layout/page-heading.component';
import { GenerateInvitationCardComponent } from '../../../../repair-shop/presentation/components/repair-shop-invitations/generate-invitation-card.component';
import { LatestInvitationCardComponent } from '../../../../repair-shop/presentation/components/repair-shop-invitations/latest-invitation-card.component';
import { ShopMechanicsListCardComponent } from '../../../../repair-shop/presentation/components/shop-mechanics/shop-mechanics-list-card.component';
import { HomeHeaderComponent } from '../../components/home-header/home-header.component';

@Component({
  selector: 'app-owner-mechanics-page',
  standalone: true,
  imports: [
    HomeHeaderComponent,
    PageHeadingComponent,
    GenerateInvitationCardComponent,
    LatestInvitationCardComponent,
    ShopMechanicsListCardComponent,
  ],
  template: `
    <main class="app-dashboard-bg min-h-screen">
      <app-home-header />

      <section class="mx-auto w-full max-w-[1500px] px-4 pb-10 pt-6 sm:px-6">
        <app-page-heading
          title="Mecanicos"
          subtitle="Administra invitaciones y revisa los mecanicos vinculados a tu taller."
        />

        <div class="mt-7 space-y-6">
          <div class="grid items-stretch gap-6 lg:grid-cols-2">
            <app-generate-invitation-card (invitationCreated)="onInvitationChanged()" />

            <app-latest-invitation-card
              [refreshKey]="invitationRefreshKey()"
              (invitationChanged)="onInvitationChanged()"
            />
          </div>

          <app-shop-mechanics-list-card />
        </div>
      </section>
    </main>
  `,
})
export class OwnerMechanicsPageComponent {
  readonly invitationRefreshKey = signal(0);

  onInvitationChanged(): void {
    this.invitationRefreshKey.update((value) => value + 1);
  }
}
