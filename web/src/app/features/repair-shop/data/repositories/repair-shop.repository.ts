import { Injectable, inject } from '@angular/core';

import { AdminRepairShopApiService } from '../api/admin-repair-shop-api.service';
import { RepairShopApiService } from '../api/repair-shop-api.service';
import { ShopInvitationsApiService } from '../api/shop-invitations-api.service';

@Injectable({ providedIn: 'root' })
export class RepairShopRepository {
  private readonly adminRepairShopApi = inject(AdminRepairShopApiService);
  private readonly repairShopApi = inject(RepairShopApiService);
  private readonly shopInvitationsApi = inject(ShopInvitationsApiService);

  createRepairShop(data: unknown) {
    return this.repairShopApi.createRepairShop(data);
  }

  getMyShop() {
    return this.repairShopApi.getMyShop();
  }

  listServices() {
    return this.repairShopApi.listServices();
  }

  getMyShopServices() {
    return this.repairShopApi.getMyShopServices();
  }

  assignMyShopServices(data: unknown) {
    return this.repairShopApi.assignMyShopServices(data);
  }

  updateMyShopProfile(data: unknown) {
    return this.repairShopApi.updateMyShopProfile(data);
  }

  updateMyShopLocation(data: unknown) {
    return this.repairShopApi.updateMyShopLocation(data);
  }

  listMyShopMechanics(isAvailable = false) {
    return this.repairShopApi.listMyShopMechanics(isAvailable);
  }

  deleteMyShopMechanic(mechanicId: string) {
    return this.repairShopApi.deleteMyShopMechanic(mechanicId);
  }

  createMyShopInvitation(data: unknown) {
    return this.shopInvitationsApi.createMyShopInvitation(data);
  }

  getMyShopInvitation() {
    return this.shopInvitationsApi.getMyShopInvitation();
  }

  deleteMyShopInvitation() {
    return this.shopInvitationsApi.deleteMyShopInvitation();
  }

  listAllShopsForAdmin() {
    return this.adminRepairShopApi.listAllShops();
  }

  getShopOverviewForAdmin(shopId: string) {
    return this.adminRepairShopApi.getShopOverview(shopId);
  }

  listShopMechanicsForAdmin(shopId: string) {
    return this.adminRepairShopApi.listShopMechanics(shopId);
  }

  deleteShopMechanicForAdmin(shopId: string, mechanicId: string) {
    return this.adminRepairShopApi.deleteShopMechanic(shopId, mechanicId);
  }

  listRecentServicesForAdmin(shopId: string) {
    return this.adminRepairShopApi.listRecentServices(shopId);
  }
}
