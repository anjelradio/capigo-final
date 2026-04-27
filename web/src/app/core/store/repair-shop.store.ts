import { Injectable, signal } from '@angular/core';

import type { RepairShop } from '../../features/repair-shop/domain/entities/repair-shop';

const REPAIR_SHOP_KEY = 'revo.repair-shop.current';

@Injectable({ providedIn: 'root' })
export class RepairShopStore {
  private readonly _shop = signal<RepairShop | null>(null);

  readonly shop = this._shop.asReadonly();

  setShop(shop: RepairShop): void {
    this._shop.set(shop);

    const storage = this.getStorage();
    if (!storage) {
      return;
    }

    storage.setItem(REPAIR_SHOP_KEY, JSON.stringify(shop));
  }

  clearShop(): void {
    this._shop.set(null);

    const storage = this.getStorage();
    if (!storage) {
      return;
    }

    storage.removeItem(REPAIR_SHOP_KEY);
  }

  hydrateShop(): void {
    const storage = this.getStorage();
    if (!storage) {
      return;
    }

    const rawShop = storage.getItem(REPAIR_SHOP_KEY);
    if (!rawShop) {
      this.clearShop();
      return;
    }

    try {
      const shop = JSON.parse(rawShop) as RepairShop;
      this._shop.set(shop);
    } catch {
      this.clearShop();
    }
  }

  private getStorage(): Storage | null {
    if (typeof window === 'undefined') {
      return null;
    }

    return window.localStorage;
  }
}
