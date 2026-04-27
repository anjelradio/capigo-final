import { Injectable, inject } from '@angular/core';

import { SessionStore } from '../../../../../core/store/session.store';
import { UserRepository } from '../../../data/repositories/user.repository';
import type {
  RequestEmailChangeOtpResult,
  UpdateEmailResult,
  UpdatePasswordResult,
  UpdateUserProfileResult,
  VerifyEmailChangeOtpResult,
  UserProfileResult,
} from '../../../data/schemas/user.schema';

@Injectable({ providedIn: 'root' })
export class UserActionsService {
  private readonly sessionStore = inject(SessionStore);
  private readonly userRepository = inject(UserRepository);

  getCurrentProfile(): UserProfileResult {
    const profile = this.userRepository.getCurrentProfile();
    if (!profile) {
      return {
        ok: false,
        errors: ['No hay sesion activa'],
      };
    }

    return {
      ok: true,
      data: profile,
    };
  }

  async updateProfile(data: unknown): Promise<UpdateUserProfileResult> {
    const response = await this.userRepository.updateProfile(data);
    if (!response.ok) {
      return response;
    }

    this.sessionStore.updateUser(response.data);

    return response;
  }

  async updatePassword(data: unknown): Promise<UpdatePasswordResult> {
    return this.userRepository.updatePassword(data);
  }

  async requestEmailChangeOtp(): Promise<RequestEmailChangeOtpResult> {
    return this.userRepository.requestEmailChangeOtp();
  }

  async verifyEmailChangeOtp(data: unknown): Promise<VerifyEmailChangeOtpResult> {
    return this.userRepository.verifyEmailChangeOtp(data);
  }

  async updateEmail(data: unknown): Promise<UpdateEmailResult> {
    const response = await this.userRepository.updateEmail(data);
    if (!response.ok) {
      return response;
    }

    this.sessionStore.updateUser(response.data);
    return response;
  }
}
