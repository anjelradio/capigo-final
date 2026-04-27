import { Injectable, inject } from '@angular/core';

import { AuthApiService } from '../api/auth-api.service';

@Injectable({ providedIn: 'root' })
export class AuthRepository {
  private readonly authApi = inject(AuthApiService);

  login(data: unknown) {
    return this.authApi.login(data);
  }

  register(data: unknown) {
    return this.authApi.register(data);
  }

  logout() {
    return this.authApi.logout();
  }

  requestPasswordResetOtp(data: unknown) {
    return this.authApi.requestPasswordResetOtp(data);
  }

  verifyPasswordResetOtp(data: unknown) {
    return this.authApi.verifyPasswordResetOtp(data);
  }
}
