import { CommonModule, Location } from '@angular/common';
import { Component, computed, inject } from '@angular/core';

import { PageHeadingComponent } from '../../../../../features/shared/presentation/components/layout/page-heading.component';
import { UserRepository } from '../../../data/repositories/user.repository';
import { EmailSettingsCardComponent } from '../../components/profile/email-settings-card.component';
import { PasswordSettingsCardComponent } from '../../components/profile/password-settings-card.component';
import { PersonalInfoCardComponent } from '../../components/profile/personal-info-card.component';

@Component({
  selector: 'app-user-profile-page',
  standalone: true,
  imports: [
    CommonModule,
    PageHeadingComponent,
    PersonalInfoCardComponent,
    EmailSettingsCardComponent,
    PasswordSettingsCardComponent,
  ],
  template: `
    <main class="app-dashboard-bg min-h-screen">
      <section class="mx-auto w-full max-w-[980px] px-4 pb-12 pt-10 sm:px-6">
        <button
          type="button"
          (click)="goBack()"
          class="inline-flex items-center gap-2 rounded-full border border-[var(--dashboard-card-default-border)] bg-white/75 px-4 py-2 text-sm font-medium text-[var(--auth-text-secondary)] transition hover:text-[var(--auth-text-primary)]"
        >
          ← Volver
        </button>

        <div class="mt-6">
          <app-page-heading
            title="Gestiona tu perfil"
            subtitle="Aqui podras revisar y administrar la informacion principal de tu cuenta."
          />
        </div>

        <div class="mt-8 space-y-7">
          <div>
            <app-personal-info-card [profile]="profile()" />
          </div>
          <div>
            <app-email-settings-card [profile]="profile()" />
          </div>
          <div>
            <app-password-settings-card />
          </div>
        </div>
      </section>
    </main>
  `,
})
export class UserProfilePageComponent {
  private readonly location = inject(Location);
  private readonly userRepository = inject(UserRepository);

  readonly profile = computed(() => this.userRepository.getCurrentProfile());

  goBack(): void {
    this.location.back();
  }
}
