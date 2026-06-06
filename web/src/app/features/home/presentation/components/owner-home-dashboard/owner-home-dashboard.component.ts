import { CommonModule } from '@angular/common';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { BaseChartDirective } from 'ng2-charts';
import {
  ArcElement,
  BarController,
  BarElement,
  CategoryScale,
  Chart,
  ChartData,
  ChartOptions,
  DoughnutController,
  Legend,
  LinearScale,
  Title,
  Tooltip,
  registerables,
} from 'chart.js';
import { LucideAngularModule, TrendingUp } from 'lucide-angular';

import { SessionStore } from '../../../../../core/store/session.store';
import { CircularProgressLoaderComponent } from '../../../../shared/presentation/components/loaders/circular-progress-loader.component';
import { PageHeadingComponent } from '../../../../shared/presentation/components/layout/page-heading.component';
import { PrimaryCardComponent } from '../../../../shared/presentation/components/cards/primary-card.component';
import { RepairShopDashboardApiService } from '../../../../repair-shop/data/api/repair-shop-dashboard-api.service';
import type {
  RepairShopDashboardBreakdownData,
  RepairShopDashboardData,
} from '../../../../repair-shop/data/schemas/repair-shop-dashboard.schema';
import { OwnerHomeZonesMapComponent } from './owner-home-zones-map.component';

Chart.register(
  ...registerables,
  ArcElement,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
  Title,
  DoughnutController,
  BarController,
);

type KpiCard = {
  title: string;
  value: string;
  helper: string;
  variant: 'default' | 'yellow' | 'aqua' | 'soft-blue' | 'soft-sand';
  badge?: string;
};

@Component({
  selector: 'app-owner-home-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    LucideAngularModule,
    PageHeadingComponent,
    PrimaryCardComponent,
    CircularProgressLoaderComponent,
    BaseChartDirective,
    OwnerHomeZonesMapComponent,
  ],
  template: `
    <main class="mx-auto w-full max-w-[1500px] px-4 pb-10 pt-6 sm:px-6">
      <div class="flex items-start justify-between gap-4">
        <app-page-heading
          [title]="welcomeTitle()"
          subtitle="Resumen operativo del taller con indicadores y graficos principales"
        />
        <div class="hidden rounded-full border border-[var(--app-nav-border)] bg-[var(--app-nav-bg)] px-4 py-2 text-xs font-semibold uppercase tracking-wide text-[var(--app-text-on-dark)] md:inline-flex">
          Periodo: {{ periodDays }} dias
        </div>
      </div>

      <section *ngIf="isLoading()" class="flex items-center justify-center py-16">
        <app-circular-progress-loader [size]="42" label="Cargando dashboard del taller" />
      </section>

      <section
        *ngIf="!isLoading() && errorMessage()"
        class="mt-6 rounded-3xl border border-red-200 bg-red-50 px-5 py-4 text-sm font-medium text-red-700"
      >
        {{ errorMessage() }}
      </section>

      <ng-container *ngIf="!isLoading() && dashboard() as data">
        <section class="mt-7 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <app-primary-card
            *ngFor="let item of kpiCards()"
            [variant]="item.variant"
            borderClass="border-transparent"
            customClass="min-h-[150px]"
          >
            <div class="flex h-full flex-col justify-between gap-4">
              <div class="flex items-start justify-between gap-3">
                <span class="text-[11px] font-semibold uppercase tracking-[0.18em] opacity-80">
                  {{ item.title }}
                </span>
                <span *ngIf="item.badge" class="rounded-full bg-white/10 px-3 py-1 text-[11px] font-semibold uppercase tracking-wide">
                  {{ item.badge }}
                </span>
              </div>

              <div>
                <p class="text-3xl font-semibold tracking-tight sm:text-[2.15rem]">{{ item.value }}</p>
                <p class="mt-2 text-sm font-medium opacity-90">{{ item.helper }}</p>
              </div>
            </div>
          </app-primary-card>
        </section>

        <section class="mt-6 grid gap-6 xl:grid-cols-[minmax(0,0.6fr)_minmax(0,0.4fr)]">
          <app-primary-card variant="yellow" customClass="min-h-[440px]">
            <div class="flex h-full flex-col gap-4">
              <div class="flex items-start justify-between gap-4">
                <div>
                  <p class="text-lg font-semibold">Zonas con mas servicios</p>
                  <p class="text-sm text-[var(--app-accent-text)]/80">Mapa de burbujas por coordenadas</p>
                </div>
                <div class="rounded-full bg-white/15 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-[var(--app-accent-text)]">
                  Leaflet
                </div>
              </div>

              <div *ngIf="hasZonesData(); else emptyZonesMap" class="flex-1">
                <app-owner-home-zones-map [zones]="dashboard()?.zones_by_services ?? []" />
              </div>

              <ng-template #emptyZonesMap>
                <div class="grid flex-1 place-items-center rounded-[26px] border border-dashed border-[var(--app-accent-text)]/20 bg-white/10 px-6 py-10 text-center">
                  <div>
                    <div class="text-lg font-semibold text-[var(--app-accent-text)]">Sin zonas registradas</div>
                    <p class="mt-2 text-sm text-[var(--app-accent-text)]/80">
                      Cuando existan servicios completados en el periodo, aqui veras las zonas con mas actividad.
                    </p>
                  </div>
                </div>
              </ng-template>
            </div>
          </app-primary-card>

          <app-primary-card variant="default" customClass="min-h-[440px]">
            <div class="flex h-full flex-col gap-4">
              <div class="flex items-start justify-between gap-4">
                <div>
                  <p class="text-lg font-semibold">Servicios que mas ofrece el taller</p>
                  <p class="text-sm opacity-80">Distribucion por servicio real del catalogo del taller</p>
                </div>
                <div class="rounded-full bg-white/10 px-3 py-1 text-xs font-semibold uppercase tracking-wide">
                  Donut
                </div>
              </div>

              <div *ngIf="hasServicesByTypeData(); else emptyServicesChart" class="flex flex-1 items-center justify-center">
                <div class="h-[300px] w-full max-w-[360px]">
                  <canvas
                    baseChart
                    [type]="doughnutChartType"
                    [data]="servicesByTypeChartData()!"
                    [options]="doughnutChartOptions"
                  ></canvas>
                </div>
              </div>

              <ng-template #emptyServicesChart>
                <div class="grid flex-1 place-items-center rounded-[26px] border border-dashed border-white/15 bg-black/10 px-6 py-10 text-center">
                  <div>
                    <div class="text-lg font-semibold">Sin datos suficientes</div>
                    <p class="mt-2 text-sm opacity-80">
                      Aun no hay servicios completados en el periodo para mostrar este grafico.
                    </p>
                  </div>
                </div>
              </ng-template>
            </div>
          </app-primary-card>
        </section>

        <section class="mt-6 grid gap-6 lg:grid-cols-3">
          <app-primary-card variant="default" customClass="min-h-[170px]">
            <div class="flex h-full flex-col justify-between gap-4">
              <div class="flex items-start justify-between gap-3">
                <div>
                  <p class="text-lg font-semibold">Tiempo promedio de resolucion</p>
                  <p class="text-sm opacity-80">Desde que el tecnico llega hasta que se cierra el servicio</p>
                </div>
                <lucide-angular [img]="summaryIcon" [size]="18" />
              </div>

              <div>
                <p class="text-3xl font-semibold tracking-tight">{{ formatDurationMinutes(data.kpis.average_resolution_minutes) }}</p>
                <p class="mt-2 text-sm opacity-85">
                  Promedio de servicios completados en el periodo
                </p>
              </div>
            </div>
          </app-primary-card>

          <app-primary-card variant="default" customClass="min-h-[170px]">
            <div class="flex h-full flex-col justify-between gap-4">
              <div class="flex items-start justify-between gap-3">
                <div>
                  <p class="text-lg font-semibold">Ticket promedio</p>
                  <p class="text-sm text-[var(--app-text-secondary)]">Ingreso medio por servicio completado</p>
                </div>
                <lucide-angular [img]="summaryIcon" [size]="18" />
              </div>

              <div>
                <p class="text-3xl font-semibold tracking-tight">{{ formatMoney(data.kpis.average_ticket_value) }}</p>
                <p class="mt-2 text-sm text-[var(--app-text-secondary)]">
                  Basado en los servicios cerrados y cobrados
                </p>
              </div>
            </div>
          </app-primary-card>

          <app-primary-card variant="default" customClass="min-h-[170px]">
            <div class="flex h-full flex-col justify-between gap-4">
              <div class="flex items-start justify-between gap-3">
                <div>
                  <p class="text-lg font-semibold">Top mecanico</p>
                  <p class="text-sm text-[var(--app-text-secondary)]">Mayor cantidad de servicios completados</p>
                </div>
                <lucide-angular [img]="summaryIcon" [size]="18" />
              </div>

              <div>
                <p class="text-xl font-semibold tracking-tight">{{ data.kpis.top_mechanic_name || 'Sin datos' }}</p>
                <p class="mt-2 text-sm text-[var(--app-text-secondary)]">
                  {{ formatCount(data.kpis.top_mechanic_completed) }} servicios completados
                </p>
              </div>
            </div>
          </app-primary-card>
        </section>
      </ng-container>
    </main>
  `,
})
export class OwnerHomeDashboardComponent implements OnInit {
  private readonly dashboardApi = inject(RepairShopDashboardApiService);
  private readonly sessionStore = inject(SessionStore);

  readonly periodDays = 30;
  readonly isLoading = signal(true);
  readonly dashboard = signal<RepairShopDashboardData | null>(null);
  readonly errorMessage = signal('');

  readonly summaryIcon = TrendingUp;
  readonly doughnutChartType: 'doughnut' = 'doughnut';

  readonly doughnutChartOptions: ChartOptions<'doughnut'> = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '68%',
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          boxWidth: 12,
          usePointStyle: true,
          pointStyle: 'circle',
        },
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const label = context.label ?? '';
            const value = Number(context.raw ?? 0);
            return `${label}: ${this.formatCount(value)}`;
          },
        },
      },
    },
  };

  readonly welcomeTitle = computed(() => {
    const user = this.sessionStore.user();
    return user ? `Inicio del taller, ${user.first_name}` : 'Inicio del taller';
  });

  readonly kpiCards = computed<KpiCard[]>(() => {
    const kpis = this.dashboard()?.kpis;

    return [
      {
        title: 'Solicitudes recibidas',
        value: this.formatCount(kpis?.requests_received ?? 0),
        helper: 'Solicitudes asignadas al taller en el periodo',
        variant: 'default',
      },
      {
        title: 'Tasa de aceptacion',
        value: this.formatPercent(kpis?.acceptance_rate ?? 0),
        helper: `${this.formatCount(kpis?.accepted_services ?? 0)} servicios aceptados`,
        variant: 'default',
      },
      {
        title: 'Tasa de cancelacion',
        value: this.formatPercent(kpis?.cancellation_rate ?? 0),
        helper: `${this.formatCount(kpis?.cancelled_cases ?? 0)} casos cancelados`,
        variant: 'default',
      },
      {
        title: 'Ingresos del periodo',
        value: this.formatMoney(kpis?.revenue_total ?? 0),
        helper: 'Cobros confirmados durante el periodo',
        variant: 'yellow',
        badge: `Periodo ${this.periodDays} dias`,
      },
    ];
  });

  readonly hasServicesByTypeData = computed(() => (this.dashboard()?.services_by_type.length ?? 0) > 0);
  readonly hasZonesData = computed(() => (this.dashboard()?.zones_by_services.length ?? 0) > 0);

  readonly servicesByTypeChartData = computed<ChartData<'doughnut'> | null>(() => {
    const items: RepairShopDashboardBreakdownData[] = this.dashboard()?.services_by_type ?? [];
    if (!items.length) {
      return null;
    }

    return {
      labels: items.map((item: RepairShopDashboardBreakdownData) => item.label),
      datasets: [
        {
          data: items.map((item: RepairShopDashboardBreakdownData) => item.count),
          backgroundColor: ['#3B82F6', '#10B981', '#F59E0B', '#EC4899', '#8B5CF6', '#14B8A6'],
          borderWidth: 0,
          hoverOffset: 10,
        },
      ],
    };
  });

  async ngOnInit(): Promise<void> {
    await this.loadDashboard();
  }

  async loadDashboard(): Promise<void> {
    this.isLoading.set(true);
    this.errorMessage.set('');

    const result = await this.dashboardApi.getMyDashboard(this.periodDays);
    if (!result.ok) {
      this.dashboard.set(null);
      this.errorMessage.set(result.errors[0] ?? 'No fue posible cargar el dashboard del taller.');
      this.isLoading.set(false);
      return;
    }

    this.dashboard.set(result.data);
    this.isLoading.set(false);
  }

  formatCount(value: number): string {
    return new Intl.NumberFormat('es-BO').format(Math.trunc(value));
  }

  formatPercent(value: number): string {
    return `${new Intl.NumberFormat('es-BO', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 1,
    }).format(value)}%`;
  }

  formatMoney(value: number): string {
    return `Bs ${new Intl.NumberFormat('es-BO', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value)}`;
  }

  formatDurationMinutes(value: number): string {
    if (!Number.isFinite(value) || value <= 0) {
      return 'Sin datos';
    }

    const totalMinutes = Math.round(value);
    const hours = Math.floor(totalMinutes / 60);
    const minutes = totalMinutes % 60;

    if (hours <= 0) {
      return `${minutes} min`;
    }

    return minutes > 0 ? `${hours} h ${minutes} min` : `${hours} h`;
  }

}
