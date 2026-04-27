import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

import { APP_ROUTES } from '../config/routes';
import { AppToastService } from '../services/app-toast.service';
import { RepairShopStore } from '../store/repair-shop.store';
import { SessionStore } from '../store/session.store';
import { isWebAllowedRole, MECHANIC_WEB_ACCESS_MESSAGE } from '../utils/web-role-access';

export const authGuard: CanActivateFn = () => {
  const sessionStore = inject(SessionStore);
  const repairShopStore = inject(RepairShopStore);
  const router = inject(Router);
  const toast = inject(AppToastService);
  const user = sessionStore.user();

  if (user && isWebAllowedRole(user.role)) {
    return true;
  }

  if (user) {
    sessionStore.clearSession();
    repairShopStore.clearShop();
    toast.error(MECHANIC_WEB_ACCESS_MESSAGE);
  }

  return router.createUrlTree([APP_ROUTES.AUTH_LOGIN]);
};
