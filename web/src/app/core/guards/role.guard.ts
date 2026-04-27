import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

import { APP_ROUTES } from '../config/routes';
import { SessionStore } from '../store/session.store';
import { resolveHomeRouteByRole } from '../utils/home-route-by-role';

type UserRole = 'admin' | 'owner' | 'mechanic' | 'client';

export function roleGuard(allowedRoles: UserRole[]): CanActivateFn {
  return () => {
    const sessionStore = inject(SessionStore);
    const router = inject(Router);
    const user = sessionStore.user();

    if (!user) {
      return router.createUrlTree([APP_ROUTES.AUTH_LOGIN]);
    }

    if (allowedRoles.includes(user.role)) {
      return true;
    }

    return router.createUrlTree([resolveHomeRouteByRole(user.role)]);
  };
}
