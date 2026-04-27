import { CommonModule } from '@angular/common';
import { Component, DestroyRef, computed, inject, signal } from '@angular/core';
import { NavigationEnd, Router } from '@angular/router';
import { filter } from 'rxjs/operators';
import { Bell, LogOut, LucideAngularModule, UserRound } from 'lucide-angular';

import { APP_ROUTES } from '../../../../../core/config/routes';
import { SessionStore } from '../../../../../core/store/session.store';
import { AuthActionsService } from '../../../../auth/presentation/actions/auth/auth-actions.service';
import { HOME_NAV_BY_ROLE, HomeNavItem, HomeNavRole } from '../../config/home-navigation.config';

@Component({
  selector: 'app-home-header',
  standalone: true,
  imports: [CommonModule, LucideAngularModule],
  template: `
    <header
      class="sticky top-0 z-40 border-b border-white/8 bg-[var(--app-bg-base)] px-4 py-3 sm:px-6"
    >
      <div class="mx-auto flex w-full max-w-[1500px] items-center gap-4 px-1 sm:gap-6">
        <div class="flex items-center gap-3">
          <img
            src="/images/logo/logo_header.webp"
            alt="Capigo"
            class="h-9 w-auto object-contain sm:h-12"
          />
          <p class="hidden text-3xl font-semibold uppercase leading-none tracking-tight sm:block">
            <span class="text-[var(--app-accent)]">CAPI</span><span class="text-white">GO</span>
          </p>
        </div>

        <nav
          *ngIf="showNavigation()"
          class="flex items-center gap-1 rounded-full border border-[var(--app-nav-border)] bg-[var(--app-nav-bg)] p-1.5 shadow-sm lg:ml-14 xl:ml-20"
        >
          <button
            *ngFor="let item of activeNavItems(); trackBy: trackByPath"
            type="button"
            (click)="goToPath(item.path)"
            class="inline-flex h-9 w-9 items-center justify-center rounded-full p-0 text-sm font-medium transition lg:h-auto lg:w-auto lg:gap-2 lg:px-5 lg:py-2.5"
            [ngClass]="
              isNavActive(item.path)
                ? 'bg-[var(--app-accent)] text-[var(--app-accent-text)]'
                : 'text-[var(--app-nav-text)] hover:bg-white/12 hover:text-[var(--app-text-on-dark)]'
            "
          >
            <lucide-angular [img]="item.icon" [size]="16" />
            <span class="hidden lg:inline">{{ item.label }}</span>
          </button>
        </nav>

        <div class="ml-auto flex items-center gap-2">
          <button
            type="button"
            class="grid h-10 w-10 place-items-center rounded-full border border-[var(--app-nav-border)] bg-[var(--app-nav-bg)] text-[var(--app-accent)] transition hover:brightness-110"
          >
            <lucide-angular [img]="bellIcon" [size]="18" />
          </button>
          <button
            type="button"
            (click)="logout()"
            [disabled]="isLoggingOut()"
            class="grid h-10 w-10 place-items-center rounded-full border border-[var(--app-nav-border)] bg-[var(--app-nav-bg)] text-[var(--app-accent)] transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-70"
          >
            <lucide-angular [img]="logoutIcon" [size]="18" />
          </button>
          <button
            type="button"
            (click)="goToProfile()"
            class="grid h-10 w-10 place-items-center rounded-full border border-[var(--app-nav-border)] bg-[var(--app-nav-bg)] text-[var(--app-accent)] transition hover:brightness-110"
          >
            <lucide-angular [img]="userIcon" [size]="18" />
          </button>
          <div class="hidden min-w-[190px] text-left sm:block">
            <p class="truncate text-sm font-semibold text-[var(--app-text-on-dark)]">
              {{ connectedUserName() }}
            </p>
            <p class="truncate text-xs text-[var(--app-text-on-dark-muted)]">
              {{ connectedUserEmail() }}
            </p>
          </div>
        </div>
      </div>
    </header>
  `,
})
export class HomeHeaderComponent {
  private readonly authActions = inject(AuthActionsService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly router = inject(Router);
  private readonly sessionStore = inject(SessionStore);

  readonly bellIcon = Bell;
  readonly logoutIcon = LogOut;
  readonly userIcon = UserRound;
  readonly isLoggingOut = signal(false);
  readonly currentPath = signal(this.router.url);

  readonly activeNavItems = computed<HomeNavItem[]>(() => {
    const appRole: HomeNavRole =
      this.sessionStore.user()?.role === 'admin' ? 'superadmin' : 'repairshop';
    return HOME_NAV_BY_ROLE[appRole];
  });

  readonly showNavigation = computed(() => this.sessionStore.user()?.role !== 'admin');

  readonly connectedUserName = computed(() => {
    const user = this.sessionStore.user();

    if (!user) {
      return 'Usuario conectado';
    }

    return `${user.first_name} ${user.last_name}`.trim();
  });

  readonly connectedUserEmail = computed(() => {
    const user = this.sessionStore.user();
    return user?.email ?? 'correo@ejemplo.com';
  });

  constructor() {
    const subscription = this.router.events
      .pipe(filter((event) => event instanceof NavigationEnd))
      .subscribe((event) => {
        this.currentPath.set((event as NavigationEnd).urlAfterRedirects);
      });

    this.destroyRef.onDestroy(() => subscription.unsubscribe());
  }

  trackByPath(_: number, item: HomeNavItem): string {
    return item.path;
  }

  isNavActive(path: string): boolean {
    const current = this.currentPath();
    const normalizedPath = path.endsWith('/') ? path.slice(0, -1) : path;

    if (
      normalizedPath === APP_ROUTES.APP_HOME_OWNER ||
      normalizedPath === APP_ROUTES.APP_HOME_ADMIN
    ) {
      return current === normalizedPath;
    }

    return current === normalizedPath || current.startsWith(`${normalizedPath}/`);
  }

  async goToPath(path: string): Promise<void> {
    if (this.isNavActive(path)) {
      return;
    }

    await this.router.navigateByUrl(path);
  }

  async logout(): Promise<void> {
    if (this.isLoggingOut()) {
      return;
    }

    this.isLoggingOut.set(true);
    try {
      await this.authActions.logout();
    } finally {
      this.isLoggingOut.set(false);
    }
  }

  async goToProfile(): Promise<void> {
    await this.router.navigateByUrl(APP_ROUTES.APP_PROFILE);
  }
}
