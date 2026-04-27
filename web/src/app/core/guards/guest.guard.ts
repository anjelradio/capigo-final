import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

import { SessionStore } from '../store/session.store';
import { resolveHomeRouteByRole } from '../utils/home-route-by-role';

export const guestGuard: CanActivateFn = () => {
  const sessionStore = inject(SessionStore);
  const router = inject(Router);

  if (!sessionStore.isAuthenticated()) {
    return true;
  }

  return router.createUrlTree([resolveHomeRouteByRole(sessionStore.user()?.role)]);
};
