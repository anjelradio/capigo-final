import { Component } from '@angular/core';

import { AuthVisualPanelComponent } from '../../components/auth/auth-visual-panel.component';
import { RegisterFormComponent } from '../../components/auth/register-form.component';

@Component({
  selector: 'app-register-page',
  standalone: true,
  imports: [RegisterFormComponent, AuthVisualPanelComponent],
  template: `
    <main
      class="app-auth-bg app-dashboard-bg min-h-screen text-[var(--auth-text-primary)] md:h-screen md:overflow-hidden"
    >
      <section
        class="mx-auto min-h-screen w-full max-w-[1500px] px-4 pb-8 pt-24 sm:px-5 sm:pt-28 md:h-full md:min-h-0 md:px-6 md:py-5 lg:px-8"
      >
        <div
          class="grid min-h-[calc(100vh-8rem)] items-center gap-8 md:h-full md:min-h-0 md:grid-cols-[minmax(320px,420px)_minmax(0,1fr)] md:gap-14 lg:gap-20"
        >
          <article
            class="flex min-h-[calc(100vh-9rem)] flex-col items-center justify-center py-2 md:h-full md:min-h-0 md:items-start md:py-4"
          >
            <div class="flex flex-1 items-center">
              <div class="w-full max-w-md text-center md:text-left">
                <h1
                  class="text-3xl font-semibold tracking-tight text-[var(--auth-text-primary)] sm:text-4xl"
                >
                  Crear una cuenta
                </h1>
                <p class="mt-2 text-sm text-[var(--auth-text-secondary)]">
                  Completa el formulario para comenzar.
                </p>
                <app-register-form />
              </div>
            </div>
          </article>

          <app-auth-visual-panel [imageUrl]="garageImage" alt="Taller mecanico" />
        </div>
      </section>
    </main>
  `,
})
export class RegisterPageComponent {
  protected readonly garageImage =
    'https://images.unsplash.com/photo-1615906655593-ad0386982a0f?q=80&w=687&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D';
}
