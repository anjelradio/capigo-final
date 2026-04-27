import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-not-found-page',
  standalone: true,
  imports: [RouterLink],
  template: `
    <main class="grid min-h-screen place-items-center bg-slate-100 px-4">
      <section
        class="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm"
      >
        <p class="text-sm font-medium text-slate-500">404</p>
        <h1 class="mt-2 text-2xl font-semibold text-slate-900">Pagina no encontrada</h1>
        <p class="mt-2 text-sm text-slate-600">La ruta que buscas no existe o fue movida.</p>
        <a
          routerLink="/auth/login"
          class="mt-6 inline-block rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800"
        >
          Ir al login
        </a>
      </section>
    </main>
  `,
})
export class NotFoundPageComponent {}
