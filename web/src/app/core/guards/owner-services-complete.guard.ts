import { inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CanActivateFn, Router } from '@angular/router';
import { firstValueFrom } from 'rxjs';

import { APP_ROUTES } from '../config/routes';
import { API_ENDPOINTS } from '../config/api-endpoints';
import { SessionStore } from '../store/session.store';
import { environment } from '../../../environments/environment';

export const ownerServicesCompleteGuard: CanActivateFn = async () => {
  const router = inject(Router);
  const sessionStore = inject(SessionStore);
  const http = inject(HttpClient);
  const user = sessionStore.user();

  if (!user || user.role !== 'owner') {
    return true;
  }

  try {
    const response = await firstValueFrom(
      http.get<unknown>(`${environment.apiUrl}${API_ENDPOINTS.REPAIR_SHOP.MY_SERVICES}`),
    );

    const serviceCount = Array.isArray(response) ? response.length : 0;
    if (serviceCount > 0) {
      return true;
    }
  } catch {
    return router.createUrlTree([APP_ROUTES.APP_REPAIR_SHOP_SERVICES]);
  }

  if (user.role === 'owner') {
    return router.createUrlTree([APP_ROUTES.APP_REPAIR_SHOP_SERVICES]);
  }

  return true;
};
