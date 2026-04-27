import { Injectable, inject } from '@angular/core';

import { RepairShopRepository } from '../../../data/repositories/repair-shop.repository';

@Injectable({ providedIn: 'root' })
export class AdminRepairShopActionsService {
  private readonly repairShopRepository = inject(RepairShopRepository);

  async listAllShops() {
    return this.repairShopRepository.listAllShopsForAdmin();
  }

  async getShopOverview(shopId: string) {
    return this.repairShopRepository.getShopOverviewForAdmin(shopId);
  }

  async listShopMechanics(shopId: string) {
    return this.repairShopRepository.listShopMechanicsForAdmin(shopId);
  }

  async deleteShopMechanic(shopId: string, mechanicId: string) {
    return this.repairShopRepository.deleteShopMechanicForAdmin(shopId, mechanicId);
  }

  async listRecentServices(shopId: string) {
    return this.repairShopRepository.listRecentServicesForAdmin(shopId);
  }
}
