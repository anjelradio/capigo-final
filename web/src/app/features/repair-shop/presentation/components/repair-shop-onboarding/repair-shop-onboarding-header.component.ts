import { CommonModule } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { LogOut, LucideAngularModule, UserRound } from 'lucide-angular';

import { APP_ROUTES } from '../../../../../core/config/routes';
import { SessionStore } from '../../../../../core/store/session.store';
import { AuthActionsService } from '../../../../auth/presentation/actions/auth/auth-actions.service';

@Component({
  selector: 'app-repair-shop-onboarding-header',
  standalone: true,
  imports: [CommonModule, LucideAngularModule],
  template: `
    <header
      class="sticky top-0 z-40 border-b border-white/12 bg-[var(--app-bg-base)] px-4 py-3 sm:px-6"
    >
      <div class="mx-auto flex w-full max-w-[1500px] items-center gap-4 px-1 sm:gap-6">
        <div class="flex items-center gap-3">
          <img
            src="/images/logo/logo_header.webp"
            alt="Capigo"
            class="h-12 w-auto object-contain"
          />
          <p class="text-3xl font-semibold uppercase leading-none tracking-tight">
            <span class="text-[var(--app-accent)]">CAPI</span><span class="text-white">GO</span>
          </p>
        </div>

        <div class="ml-auto flex items-center gap-2">
          <button
            type="button"
            (click)="logout()"
            [disabled]="isLoggingOut()"
            class="grid h-10 w-10 place-items-center rounded-full border border-white/35 bg-white/12 text-white transition hover:bg-white/20 disabled:cursor-not-allowed disabled:opacity-70"
          >
            <lucide-angular [img]="logoutIcon" [size]="18" />
          </button>
          <button
            type="button"
            (click)="goToProfile()"
            class="grid h-10 w-10 place-items-center rounded-full border border-white/35 bg-white/12 text-white transition hover:bg-white/20"
          >
            <lucide-angular [img]="userIcon" [size]="18" />
          </button>
          <div class="hidden min-w-[190px] text-left sm:block">
            <p class="truncate text-sm font-semibold text-white">
              {{ connectedUserName() }}
            </p>
            <p class="truncate text-xs text-white/80">
              {{ connectedUserEmail() }}
            </p>
          </div>
        </div>
      </div>
    </header>
  `,
})
export class RepairShopOnboardingHeaderComponent {
  private readonly authActions = inject(AuthActionsService);
  private readonly router = inject(Router);
  private readonly sessionStore = inject(SessionStore);

  readonly logoutIcon = LogOut;
  readonly userIcon = UserRound;
  readonly isLoggingOut = signal(false);

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
