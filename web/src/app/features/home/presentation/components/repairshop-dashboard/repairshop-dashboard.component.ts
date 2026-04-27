import { CommonModule } from '@angular/common';
import { Component, computed, inject } from '@angular/core';
import {
  Bell,
  CalendarRange,
  CarFront,
  LucideIconData,
  LucideAngularModule,
  Settings2,
  Wrench,
} from 'lucide-angular';

import { SessionStore } from '../../../../../core/store/session.store';
import { PrimaryCardComponent } from '../../../../../features/shared/presentation/components/cards/primary-card.component';
import { PageHeadingComponent } from '../../../../../features/shared/presentation/components/layout/page-heading.component';

type StatCard = {
  title: string;
  value: string;
  icon: LucideIconData;
  variant: 'default' | 'yellow' | 'aqua';
};

@Component({
  selector: 'app-repairshop-dashboard',
  standalone: true,
  imports: [CommonModule, LucideAngularModule, PageHeadingComponent, PrimaryCardComponent],
  template: `
    <main class="mx-auto w-full max-w-[1500px] px-4 pb-10 pt-6 sm:px-6">
      <div class="flex items-start justify-between gap-4">
        <app-page-heading
          [title]="welcomeTitle()"
          subtitle="Estas son las ultimas actualizaciones del taller"
        />
        <button
          type="button"
          class="hidden items-center gap-2 rounded-full border border-[var(--app-nav-border)] bg-[var(--app-nav-bg)] px-4 py-2.5 text-sm font-medium text-[var(--app-text-on-dark)] md:inline-flex"
        >
          <lucide-angular [img]="filterIcon" [size]="16" />
          Filtro
        </button>
      </div>

      <section
        class="mt-7 grid gap-6 xl:min-h-[760px] xl:grid-cols-[minmax(0,1.9fr)_minmax(320px,1fr)]"
      >
        <div class="flex flex-col gap-6 xl:h-full">
          <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <app-primary-card
              *ngFor="let item of statCards"
              [variant]="item.variant"
              borderClass="border-transparent"
              customClass="min-h-[165px]"
            >
              <div class="flex h-full flex-col justify-between">
                <div class="flex items-start justify-between gap-2">
                  <div
                    class="grid h-10 w-10 place-items-center rounded-full bg-[var(--app-card-soft-bg)]"
                  >
                    <lucide-angular [img]="item.icon" [size]="18" />
                  </div>
                  <span class="text-xl leading-none">...</span>
                </div>

                <div>
                  <p class="text-3xl font-semibold tracking-tight">{{ item.value }}</p>
                  <p class="mt-1 text-sm opacity-90">{{ item.title }}</p>
                </div>
              </div>
            </app-primary-card>
          </div>

          <div class="xl:flex-1">
            <app-primary-card variant="aqua" customClass="min-h-[270px] h-full xl:min-h-0">
              <div class="flex h-full flex-col justify-between">
                <p class="text-xl font-medium">Ingresos Totales</p>
                <p class="text-sm text-[var(--app-text-secondary)]">Proximamente</p>
              </div>
            </app-primary-card>
          </div>
        </div>

        <div class="space-y-8">
          <app-primary-card variant="default" customClass="min-h-[220px]">
            <div class="flex h-full flex-col justify-between">
              <div class="flex items-center justify-between gap-2">
                <p class="text-2xl font-semibold tracking-tight">Servicios de Hoy</p>
                <span class="text-sm text-[var(--auth-text-secondary)]">See all</span>
              </div>
              <p class="text-sm text-[var(--auth-text-secondary)]">Proximamente</p>
            </div>
          </app-primary-card>

          <app-primary-card variant="default" customClass="min-h-[220px]">
            <div class="flex h-full flex-col justify-between">
              <p class="text-2xl font-semibold tracking-tight">Servicios por Tipo</p>
              <p class="text-sm text-[var(--auth-text-secondary)]">Proximamente</p>
            </div>
          </app-primary-card>

          <app-primary-card variant="yellow" customClass="min-h-[160px]">
            <div class="flex h-full items-end justify-between">
              <p class="text-2xl font-semibold tracking-tight">Panel de Rendimiento</p>
              <p class="text-sm text-[var(--app-text-secondary)]">Proximamente</p>
            </div>
          </app-primary-card>
        </div>
      </section>
    </main>
  `,
})
export class RepairshopDashboardComponent {
  private readonly sessionStore = inject(SessionStore);

  readonly filterIcon = Settings2;
  readonly statCards: StatCard[] = [
    {
      title: 'Trabajos Completados',
      value: '5,355',
      icon: Wrench,
      variant: 'aqua',
    },
    {
      title: 'Vehiculos Reparados',
      value: '3,847',
      icon: CarFront,
      variant: 'yellow',
    },
    {
      title: 'Bahias de Servicio',
      value: '1,050',
      icon: CalendarRange,
      variant: 'default',
    },
  ];

  readonly welcomeTitle = computed(() => {
    const user = this.sessionStore.user();

    if (!user) {
      return 'Bienvenido de nuevo';
    }

    return `Bienvenido de nuevo, ${user.first_name}`;
  });
}
