import { Injectable, inject } from '@angular/core';

import { SessionStore } from '../../../../core/store/session.store';
import { UserApiService } from '../api/user-api.service';
import type { UserProfile } from '../../domain/entities/user-profile';

@Injectable({ providedIn: 'root' })
export class UserRepository {
  private readonly userApi = inject(UserApiService);
  private readonly sessionStore = inject(SessionStore);

  getCurrentProfile(): UserProfile | null {
    const user = this.sessionStore.user();
    if (!user) {
      return null;
    }

    return {
      id: user.id,
      first_name: user.first_name,
      last_name: user.last_name,
      email: user.email,
      phone: user.phone,
      role: user.role,
    };
  }

  updateProfile(data: unknown) {
    return this.userApi.updateProfile(data);
  }

  updatePassword(data: unknown) {
    return this.userApi.updatePassword(data);
  }

  requestEmailChangeOtp() {
    return this.userApi.requestEmailChangeOtp();
  }

  verifyEmailChangeOtp(data: unknown) {
    return this.userApi.verifyEmailChangeOtp(data);
  }

  updateEmail(data: unknown) {
    return this.userApi.updateEmail(data);
  }
}
