import { Component } from '@angular/core';

import { PageHeadingComponent } from '../../../../../features/shared/presentation/components/layout/page-heading.component';
import { ShopInfoCardComponent } from '../../../../repair-shop/presentation/components/repair-shop-settings/shop-info-card.component';
import { ShopLocationCardComponent } from '../../../../repair-shop/presentation/components/repair-shop-settings/shop-location-card.component';
import { ShopServicesCardComponent } from '../../../../repair-shop/presentation/components/repair-shop-settings/shop-services-card.component';
import { HomeHeaderComponent } from '../../components/home-header/home-header.component';

@Component({
  selector: 'app-owner-shop-settings-page',
  standalone: true,
  imports: [
    HomeHeaderComponent,
    PageHeadingComponent,
    ShopInfoCardComponent,
    ShopLocationCardComponent,
    ShopServicesCardComponent,
  ],
  template: `
    <main class="app-dashboard-bg min-h-screen">
      <app-home-header />

      <section class="mx-auto w-full max-w-[1500px] px-4 pb-10 pt-6 sm:px-6">
        <app-page-heading
          title="Configuracion del taller"
          subtitle="Aqui podras gestionar y editar el perfil de tu taller."
        />

        <div class="mt-7 grid gap-6 lg:grid-cols-[0.95fr_1.05fr]">
          <div class="space-y-10">
            <div>
              <app-shop-info-card />
            </div>
            <div>
              <app-shop-location-card />
            </div>
          </div>

          <app-shop-services-card class="block h-full" />
        </div>
      </section>
    </main>
  `,
})
export class OwnerShopSettingsPageComponent {}
