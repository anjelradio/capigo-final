import { Injectable, inject } from '@angular/core';
import { Router } from '@angular/router';

import { APP_ROUTES } from '../../../../../core/config/routes';
import { RepairShopStore } from '../../../../../core/store/repair-shop.store';
import { SessionStore } from '../../../../../core/store/session.store';
import { resolveHomeRouteByRole } from '../../../../../core/utils/home-route-by-role';
import {
  isWebAllowedRole,
  MECHANIC_WEB_ACCESS_MESSAGE,
} from '../../../../../core/utils/web-role-access';
import { RepairShopRepository } from '../../../../repair-shop/data/repositories/repair-shop.repository';
import { AuthRepository } from '../../../data/repositories/auth.repository';
import type {
  AuthActionResult,
  AuthLogoutResult,
  RequestPasswordResetOtpResult,
  VerifyPasswordResetOtpResult,
} from '../../../data/schemas/auth.schema';

@Injectable({ providedIn: 'root' })
export class AuthActionsService {
  private readonly router = inject(Router);
  private readonly repairShopStore = inject(RepairShopStore);
  private readonly repairShopRepository = inject(RepairShopRepository);
  private readonly sessionStore = inject(SessionStore);
  private readonly authRepository = inject(AuthRepository);

  async login(data: unknown): Promise<AuthActionResult> {
    const response = await this.authRepository.login(data);

    if (!response.ok) {
      return response;
    }

    if (!isWebAllowedRole(response.data.user.role)) {
      return {
        ok: false,
        errors: [MECHANIC_WEB_ACCESS_MESSAGE],
      };
    }

    this.sessionStore.setSession({
      user: response.data.user,
      accessToken: response.data.accessToken,
    });

    const shopResult = await this.syncOwnerShop(response.data.user.role);
    if (!shopResult.ok) {
      this.sessionStore.clearSession();
      this.repairShopStore.clearShop();
      return shopResult;
    }

    await this.router.navigateByUrl(resolveHomeRouteByRole(response.data.user.role));

    return {
      ok: true,
      data: response.data.user,
    };
  }

  async register(data: unknown): Promise<AuthActionResult> {
    const response = await this.authRepository.register(data);

    if (!response.ok) {
      return response;
    }

    if (!isWebAllowedRole(response.data.user.role)) {
      return {
        ok: false,
        errors: [MECHANIC_WEB_ACCESS_MESSAGE],
      };
    }

    this.sessionStore.setSession({
      user: response.data.user,
      accessToken: response.data.accessToken,
    });

    const shopResult = await this.syncOwnerShop(response.data.user.role);
    if (!shopResult.ok) {
      this.sessionStore.clearSession();
      this.repairShopStore.clearShop();
      return shopResult;
    }

    await this.router.navigateByUrl(resolveHomeRouteByRole(response.data.user.role));

    return {
      ok: true,
      data: response.data.user,
    };
  }

  async logout(): Promise<AuthLogoutResult> {
    const response = await this.authRepository.logout();

    this.sessionStore.clearSession();
    this.repairShopStore.clearShop();
    await this.router.navigateByUrl(APP_ROUTES.AUTH_LOGIN);

    if (!response.ok) {
      return { ok: true };
    }

    return { ok: true };
  }

  async requestPasswordResetOtp(data: unknown): Promise<RequestPasswordResetOtpResult> {
    return this.authRepository.requestPasswordResetOtp(data);
  }

  async verifyPasswordResetOtp(data: unknown): Promise<VerifyPasswordResetOtpResult> {
    return this.authRepository.verifyPasswordResetOtp(data);
  }

  private async syncOwnerShop(role: 'admin' | 'owner' | 'mechanic' | 'client'): Promise<
    | {
        ok: true;
      }
    | {
        ok: false;
        errors: string[];
      }
  > {
    if (role !== 'owner') {
      this.repairShopStore.clearShop();
      return { ok: true };
    }

    const shopResponse = await this.repairShopRepository.getMyShop();
    if (!shopResponse.ok) {
      return {
        ok: false,
        errors: shopResponse.errors,
      };
    }

    this.repairShopStore.setShop(shopResponse.data);
    return { ok: true };
  }
}
