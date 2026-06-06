import { Component } from '@angular/core';

import { HomeHeaderComponent } from '../../components/home-header/home-header.component';
import { OwnerHomeDashboardComponent } from '../../components/owner-home-dashboard/owner-home-dashboard.component';

@Component({
  selector: 'app-owner-home-page',
  standalone: true,
  imports: [HomeHeaderComponent, OwnerHomeDashboardComponent],
  template: `
    <main class="app-dashboard-bg min-h-screen">
      <app-home-header />
      <app-owner-home-dashboard />
    </main>
  `,
})
export class OwnerHomePageComponent {}
