import { Component, effect, inject } from '@angular/core';
import { RouterOutlet } from '@angular/router';

import { RealtimeOffersSocketService } from './features/realtime/presentation/services/realtime-offers-socket.service';
import { RepairShopStore } from './core/store/repair-shop.store';
import { SessionStore } from './core/store/session.store';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet],
  template: '<router-outlet />',
})
export class App {
  private readonly repairShopStore = inject(RepairShopStore);
  private readonly sessionStore = inject(SessionStore);
  private readonly realtimeOffersSocket = inject(RealtimeOffersSocketService);

  constructor() {
    this.sessionStore.hydrateSession();
    this.repairShopStore.hydrateShop();

    effect(() => {
      const user = this.sessionStore.user();
      const token = this.sessionStore.accessToken();

      if (user?.role === 'owner' && token) {
        this.realtimeOffersSocket.connect(token);
        return;
      }

      this.realtimeOffersSocket.disconnect();
    });
  }
}
