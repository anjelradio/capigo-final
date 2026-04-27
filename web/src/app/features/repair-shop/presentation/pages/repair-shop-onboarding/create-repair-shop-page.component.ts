import { Component } from '@angular/core';

import { PrimaryCardComponent } from '../../../../../features/shared/presentation/components/cards/primary-card.component';
import { CreateRepairShopFormComponent } from '../../components/repair-shop-onboarding/create-repair-shop-form.component';
import { RepairShopOnboardingHeaderComponent } from '../../components/repair-shop-onboarding/repair-shop-onboarding-header.component';

@Component({
  selector: 'app-create-repair-shop-page',
  standalone: true,
  imports: [
    RepairShopOnboardingHeaderComponent,
    PrimaryCardComponent,
    CreateRepairShopFormComponent,
  ],
  template: `
    <main class="relative min-h-screen overflow-hidden">
      <div
        class="absolute inset-0 bg-cover bg-center"
        style="background-image: url('https://plus.unsplash.com/premium_photo-1677009835876-4a29ddc4cc2c?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D')"
      ></div>
      <div class="absolute inset-0 bg-slate-950/62"></div>

      <div class="relative z-10 flex min-h-screen flex-col">
        <app-repair-shop-onboarding-header />

        <section class="mx-auto flex w-full max-w-[1500px] flex-1 items-center px-4 pb-8 sm:px-6">
          <div class="grid w-full gap-8 lg:grid-cols-[0.8fr_1.2fr] lg:gap-12">
            <div class="self-center text-white">
              <p class="text-xs font-semibold uppercase tracking-[0.32em] text-white/75">
                Bienvenido a CAPIGO
              </p>
              <h1 class="mt-4 text-4xl font-semibold tracking-tight sm:text-5xl">
                Registra tu taller y empieza a crecer
              </h1>
              <p class="mt-4 max-w-[35ch] text-base leading-relaxed text-white/85 sm:text-lg">
                Centraliza tus servicios, organiza tu operacion y conecta con mas clientes desde una
                sola plataforma.
              </p>
            </div>

            <app-primary-card
              variant="default"
              backgroundClass="bg-white/90 backdrop-blur-sm"
              borderClass="border border-white/65"
              customClass="w-full max-w-2xl justify-self-end p-8 sm:p-10"
            >
              <h2 class="text-2xl font-semibold tracking-tight text-[var(--auth-text-primary)]">
                Registrar tu taller
              </h2>

              <app-create-repair-shop-form />
            </app-primary-card>
          </div>
        </section>
      </div>
    </main>
  `,
})
export class CreateRepairShopPageComponent {}
