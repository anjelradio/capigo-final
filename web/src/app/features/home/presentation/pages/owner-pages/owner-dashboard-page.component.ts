import { Component } from '@angular/core';

import { HomeHeaderComponent } from '../../components/home-header/home-header.component';
import { RepairshopDashboardComponent } from '../../components/repairshop-dashboard/repairshop-dashboard.component';

@Component({
  selector: 'app-owner-dashboard-page',
  standalone: true,
  imports: [HomeHeaderComponent, RepairshopDashboardComponent],
  template: `
    <main class="app-dashboard-bg min-h-screen">
      <app-home-header />
      <app-repairshop-dashboard />
    </main>
  `,
})
export class OwnerDashboardPageComponent {}
