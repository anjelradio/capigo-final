import { Injectable, inject } from '@angular/core';
import { Router } from '@angular/router';

import { APP_ROUTES } from '../../../../../core/config/routes';
import { RepairShopStore } from '../../../../../core/store/repair-shop.store';
import { SessionStore } from '../../../../../core/store/session.store';
import type {
  ApiMaybeResult,
  ApiResult,
  ApiStatusResult,
} from '../../../../shared/data/types/api-result';
import { RepairShopRepository } from '../../../data/repositories/repair-shop.repository';
import type {
  RepairShopData,
  RepairShopResponseData,
  ServiceData,
  ShopInvitationData,
  ShopMechanicData,
} from '../../../data/schemas/repair-shop.schema';

@Injectable({ providedIn: 'root' })
export class RepairShopActionsService {
  private readonly repairShopRepository = inject(RepairShopRepository);
  private readonly sessionStore = inject(SessionStore);
  private readonly repairShopStore = inject(RepairShopStore);
  private readonly router = inject(Router);

  async createRepairShop(data: unknown): Promise<ApiResult<RepairShopResponseData>> {
    const response = await this.repairShopRepository.createRepairShop(data);
    if (!response.ok) {
      return response;
    }

    const accessToken = this.sessionStore.getAccessToken();
    if (!accessToken) {
      return {
        ok: false,
        errors: ['No hay sesion activa'],
      };
    }

    this.sessionStore.setSession({
      user: response.data.user,
      accessToken,
    });
    this.repairShopStore.setShop(response.data.shop);
    await this.router.navigateByUrl(APP_ROUTES.APP_REPAIR_SHOP_SERVICES);

    return response;
  }

  async getMyShop(): Promise<ApiResult<RepairShopData>> {
    return this.repairShopRepository.getMyShop();
  }

  async listServices(): Promise<ApiResult<ServiceData[]>> {
    return this.repairShopRepository.listServices();
  }

  async getMyShopServices(): Promise<ApiResult<ServiceData[]>> {
    return this.repairShopRepository.getMyShopServices();
  }

  async assignMyShopServices(
    data: unknown,
    options: { navigateOnSuccess?: boolean } = {},
  ): Promise<ApiResult<RepairShopData>> {
    const response = await this.repairShopRepository.assignMyShopServices(data);
    if (!response.ok) {
      return response;
    }

    this.repairShopStore.setShop(response.data);
    const navigateOnSuccess = options.navigateOnSuccess ?? true;
    if (navigateOnSuccess) {
      await this.router.navigateByUrl(APP_ROUTES.APP_HOME_OWNER);
    }

    return response;
  }

  async updateMyShopProfile(data: unknown): Promise<ApiResult<RepairShopData>> {
    const response = await this.repairShopRepository.updateMyShopProfile(data);
    if (!response.ok) {
      return response;
    }

    this.repairShopStore.setShop(response.data);
    return response;
  }

  async updateMyShopLocation(data: unknown): Promise<ApiResult<RepairShopData>> {
    const response = await this.repairShopRepository.updateMyShopLocation(data);
    if (!response.ok) {
      return response;
    }

    this.repairShopStore.setShop(response.data);
    return response;
  }

  async createMyShopInvitation(data: unknown): Promise<ApiStatusResult> {
    return this.repairShopRepository.createMyShopInvitation(data);
  }

  async getMyShopInvitation(): Promise<ApiMaybeResult<ShopInvitationData>> {
    return this.repairShopRepository.getMyShopInvitation();
  }

  async deleteMyShopInvitation(): Promise<ApiStatusResult> {
    return this.repairShopRepository.deleteMyShopInvitation();
  }

  async listMyShopMechanics(isAvailable = false): Promise<ApiResult<ShopMechanicData[]>> {
    return this.repairShopRepository.listMyShopMechanics(isAvailable);
  }

  async deleteMyShopMechanic(mechanicId: string): Promise<ApiStatusResult> {
    return this.repairShopRepository.deleteMyShopMechanic(mechanicId);
  }
}
