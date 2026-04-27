import { Component } from '@angular/core';

import { PageHeadingComponent } from '../../../../../features/shared/presentation/components/layout/page-heading.component';
import { HomeHeaderComponent } from '../../components/home-header/home-header.component';

@Component({
  selector: 'app-owner-history-page',
  standalone: true,
  imports: [HomeHeaderComponent, PageHeadingComponent],
  template: `
    <main class="app-dashboard-bg min-h-screen">
      <app-home-header />

      <section class="mx-auto w-full max-w-[1500px] px-4 pb-10 pt-6 sm:px-6">
        <app-page-heading
          title="Saldo"
          subtitle="Aqui podras consultar el saldo de tu billetera del taller."
        />
      </section>
    </main>
  `,
})
export class OwnerHistoryPageComponent {}
