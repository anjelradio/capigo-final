import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';

import { environment } from '../../../environments/environment';
import { AuthTokenService } from '../services/auth-token.service';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authToken = inject(AuthTokenService);
  const isApiRequest = req.url.startsWith(environment.apiUrl);

  if (!isApiRequest) {
    return next(req);
  }

  const token = authToken.getToken();
  if (!token) {
    return next(req);
  }

  const requestWithAuth = req.clone({
    headers: req.headers.set('Authorization', `Bearer ${token}`),
  });

  return next(requestWithAuth);
};
