import { Injectable, inject } from '@angular/core';

import { SessionStore } from '../store/session.store';

@Injectable({ providedIn: 'root' })
export class AuthTokenService {
  private readonly sessionStore = inject(SessionStore);

  getToken(): string | null {
    return this.sessionStore.getAccessToken();
  }
}
