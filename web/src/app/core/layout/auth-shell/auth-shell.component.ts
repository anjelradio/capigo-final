import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-auth-shell',
  standalone: true,
  imports: [RouterOutlet],
  template: `
    <header
      class="fixed left-4 top-4 z-40 inline-flex w-fit items-center gap-3 sm:left-5 md:left-6 md:top-5 lg:left-8"
    >
      <img src="/images/logo/logo_header.webp" alt="Capigo" class="h-14 w-auto object-contain" />
      <p class="text-3xl font-semibold uppercase leading-none tracking-tight">
        <span class="text-[var(--app-accent)]">CAPI</span><span class="text-white">GO</span>
      </p>
    </header>
    <router-outlet />
  `,
})
export class AuthShellComponent {}
