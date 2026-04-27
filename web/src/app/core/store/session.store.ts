import { Injectable, computed, signal } from '@angular/core';

const SESSION_USER_KEY = 'revo.session.user';
const SESSION_TOKEN_KEY = 'revo.session.token';

export interface SessionUser {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  role: 'admin' | 'owner' | 'mechanic' | 'client';
}

@Injectable({ providedIn: 'root' })
export class SessionStore {
  private readonly _user = signal<SessionUser | null>(null);
  private readonly _accessToken = signal<string | null>(null);
  private readonly _isLoading = signal<boolean>(false);

  readonly user = this._user.asReadonly();
  readonly accessToken = this._accessToken.asReadonly();
  readonly isLoading = this._isLoading.asReadonly();
  readonly isAuthenticated = computed(() => this._user() !== null);

  setSession(payload: { user: SessionUser; accessToken: string }): void {
    this._user.set(payload.user);
    this._accessToken.set(payload.accessToken);

    const storage = this.getStorage();
    if (!storage) {
      return;
    }

    storage.setItem(SESSION_USER_KEY, JSON.stringify(payload.user));
    storage.setItem(SESSION_TOKEN_KEY, payload.accessToken);
  }

  updateUser(user: SessionUser): void {
    this._user.set(user);

    const storage = this.getStorage();
    if (!storage) {
      return;
    }

    storage.setItem(SESSION_USER_KEY, JSON.stringify(user));
  }

  clearSession(): void {
    this._user.set(null);
    this._accessToken.set(null);

    const storage = this.getStorage();
    if (!storage) {
      return;
    }

    storage.removeItem(SESSION_USER_KEY);
    storage.removeItem(SESSION_TOKEN_KEY);
    this.clearCookie('auth_token');
  }

  hydrateSession(): void {
    const storage = this.getStorage();
    if (!storage) {
      return;
    }

    const rawUser = storage.getItem(SESSION_USER_KEY);
    const accessToken = storage.getItem(SESSION_TOKEN_KEY);
    if (!rawUser || !accessToken) {
      this.clearSession();
      return;
    }

    try {
      const user = JSON.parse(rawUser) as SessionUser;
      this._user.set(user);
      this._accessToken.set(accessToken);
    } catch {
      this.clearSession();
    }
  }

  getAccessToken(): string | null {
    return this._accessToken();
  }

  setLoading(value: boolean): void {
    this._isLoading.set(value);
  }

  private getStorage(): Storage | null {
    if (typeof window === 'undefined') {
      return null;
    }

    return window.localStorage;
  }

  private clearCookie(name: string): void {
    if (typeof document === 'undefined') {
      return;
    }

    document.cookie = `${name}=; Max-Age=0; path=/`;
  }
}
