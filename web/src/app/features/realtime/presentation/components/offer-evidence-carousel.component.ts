import { CommonModule } from '@angular/common';
import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';

@Component({
  selector: 'app-offer-evidence-carousel',
  standalone: true,
  imports: [CommonModule],
  template: `
    <section class="space-y-2">
      <header>
        <p class="text-xs uppercase text-[var(--auth-text-secondary)]">Evidencias</p>
      </header>

      <ng-container *ngIf="images.length > 0; else emptyEvidence">
        <div class="relative overflow-hidden rounded-2xl border border-[var(--app-card-soft-border)] bg-black/5">
          <img
            [src]="images[currentIndex]"
            [alt]="'Evidencia ' + (currentIndex + 1)"
            class="h-72 w-full object-cover"
            loading="lazy"
          />

          <button
            type="button"
            class="absolute left-3 top-1/2 inline-flex h-9 w-9 -translate-y-1/2 items-center justify-center rounded-full bg-white/90 text-lg font-bold text-slate-700 shadow transition hover:bg-white"
            (click)="previous()"
            [disabled]="images.length <= 1"
            aria-label="Imagen anterior"
          >
            ‹
          </button>

          <button
            type="button"
            class="absolute right-3 top-1/2 inline-flex h-9 w-9 -translate-y-1/2 items-center justify-center rounded-full bg-white/90 text-lg font-bold text-slate-700 shadow transition hover:bg-white"
            (click)="next()"
            [disabled]="images.length <= 1"
            aria-label="Imagen siguiente"
          >
            ›
          </button>
        </div>

        <div class="flex items-center justify-center gap-1">
          <button
            type="button"
            *ngFor="let image of images; let i = index"
            class="h-2 w-2 rounded-full"
            [ngClass]="i === currentIndex ? 'bg-[var(--app-accent)]' : 'bg-slate-300'"
            (click)="goTo(i)"
            [attr.aria-label]="'Ir a imagen ' + (i + 1)"
          ></button>
        </div>
      </ng-container>

      <ng-template #emptyEvidence>
        <article
          class="rounded-2xl border border-dashed border-[var(--app-card-soft-border)] bg-[var(--app-card-soft-bg)] p-4 text-sm text-[var(--auth-text-secondary)]"
        >
          El cliente no adjunto imagenes en esta solicitud.
        </article>
      </ng-template>
    </section>
  `,
})
export class OfferEvidenceCarouselComponent implements OnChanges {
  @Input() images: string[] = [];

  currentIndex = 0;

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['images']) {
      this.currentIndex = 0;
    }
  }

  previous(): void {
    if (this.images.length <= 1) {
      return;
    }

    this.currentIndex =
      this.currentIndex === 0 ? this.images.length - 1 : this.currentIndex - 1;
  }

  next(): void {
    if (this.images.length <= 1) {
      return;
    }

    this.currentIndex = (this.currentIndex + 1) % this.images.length;
  }

  goTo(index: number): void {
    this.currentIndex = index;
  }
}
