import { CommonModule } from '@angular/common';
import {
  AfterViewInit,
  Component,
  ElementRef,
  EventEmitter,
  Input,
  OnChanges,
  OnDestroy,
  Output,
  SimpleChanges,
  ViewChild,
} from '@angular/core';
import * as L from 'leaflet';

import type { OwnerOfferDetail } from '../../domain/entities/owner-offer';
import { OfferEvidenceCarouselComponent } from './offer-evidence-carousel.component';
import { AppModalComponent } from '../../../shared/presentation/components/modals/app-modal.component';
import { CircularProgressLoaderComponent } from '../../../shared/presentation/components/loaders/circular-progress-loader.component';

const markerIcon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

@Component({
  selector: 'app-owner-offer-detail-modal',
  standalone: true,
  imports: [
    CommonModule,
    AppModalComponent,
    OfferEvidenceCarouselComponent,
    CircularProgressLoaderComponent,
  ],
  template: `
    <app-modal
      [open]="open"
      [panelClass]="'max-w-3xl'"
      (openChange)="onOpenChange($event)"
    >
      <section *ngIf="isLoading" class="flex min-h-[380px] items-center justify-center px-6 py-6">
        <app-circular-progress-loader
          [size]="42"
          label="Cargando detalle"
          colorClass="border-slate-600"
        />
      </section>

      <section *ngIf="!isLoading" class="space-y-4 px-6 py-6">
        <header class="space-y-1">
          <p class="text-xs font-semibold uppercase tracking-wide text-[var(--auth-text-secondary)]">
            Oferta en tiempo real
          </p>
          <h3 class="text-2xl font-semibold text-[var(--app-text-primary)]">
            {{ detail?.problemName || 'Incidente clasificado' }}
          </h3>
          <p class="text-sm text-[var(--auth-text-secondary)]">
            {{ detail?.incidentDescription || 'Sin descripcion enviada por el cliente.' }}
          </p>
        </header>

        <div class="grid gap-3 sm:grid-cols-2">
          <article class="rounded-2xl border border-[var(--app-card-soft-border)] bg-[var(--app-card-soft-bg)] p-4">
            <p class="text-xs uppercase text-[var(--auth-text-secondary)]">Distancia</p>
            <p class="mt-1 text-lg font-semibold text-[var(--app-text-primary)]">
              {{ formatDistance(detail?.distanceKm) }}
            </p>
          </article>

          <article class="rounded-2xl border border-[var(--app-card-soft-border)] bg-[var(--app-card-soft-bg)] p-4">
            <p class="text-xs uppercase text-[var(--auth-text-secondary)]">Costo de traslado</p>
            <p class="mt-1 text-lg font-semibold text-[var(--app-text-primary)]">
              {{ formatPrice(detail?.deliveryPrice) }}
            </p>
          </article>
        </div>

        <app-offer-evidence-carousel [images]="detail?.evidenceUrls ?? []" />

        <div class="overflow-hidden rounded-2xl border border-[var(--app-card-soft-border)]">
          <div #mapContainer class="h-72 w-full"></div>
        </div>

        <footer
          *ngIf="showActions && !isLoading"
          class="flex flex-col-reverse gap-2 pt-1 sm:flex-row sm:justify-end"
        >
          <button
            type="button"
            class="inline-flex items-center justify-center rounded-full border border-rose-300 px-4 py-2 text-sm font-semibold text-rose-700 transition hover:bg-rose-50 disabled:cursor-not-allowed disabled:opacity-60"
            [disabled]="isSubmitting"
            (click)="onRejectClick()"
          >
            Rechazar
          </button>
          <button
            type="button"
            class="inline-flex items-center justify-center rounded-full bg-[var(--app-accent)] px-4 py-2 text-sm font-semibold text-[var(--app-accent-text)] transition hover:brightness-105 disabled:cursor-not-allowed disabled:opacity-60"
            [disabled]="isSubmitting"
            (click)="onAcceptClick()"
          >
            {{ isSubmitting ? 'Procesando...' : 'Aceptar' }}
          </button>
        </footer>
      </section>
    </app-modal>
  `,
})
export class OwnerOfferDetailModalComponent implements AfterViewInit, OnChanges, OnDestroy {
  @Input() open = false;
  @Input() detail: OwnerOfferDetail | null = null;
  @Input() isLoading = false;
  @Input() onClose: (() => void) | null = null;
  @Input() isSubmitting = false;
  @Input() showActions = true;

  @Output() accept = new EventEmitter<void>();
  @Output() reject = new EventEmitter<void>();

  @ViewChild('mapContainer')
  private mapContainerRef?: ElementRef<HTMLDivElement>;

  private map: L.Map | null = null;
  private marker: L.Marker | null = null;

  ngAfterViewInit(): void {
    this.ensureMapInitialized();
    this.refreshMap();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['open']) {
      const isOpen = changes['open'].currentValue === true;
      if (!isOpen) {
        this.destroyMap();
        return;
      }
    }

    if (changes['detail'] || changes['open'] || changes['isLoading']) {
      this.ensureMapInitialized();
      this.refreshMap();
    }
  }

  ngOnDestroy(): void {
    this.destroyMap();
  }

  onOpenChange(open: boolean): void {
    if (!open) {
      this.onClose?.();
    }
  }

  formatDistance(distanceKm?: number | null): string {
    if (distanceKm === null || distanceKm === undefined) {
      return 'No disponible';
    }
    return `${distanceKm.toFixed(2)} km`;
  }

  formatPrice(price?: number | null): string {
    if (price === null || price === undefined) {
      return 'No disponible';
    }
    return `Bs ${price.toFixed(2)}`;
  }

  onAcceptClick(): void {
    this.accept.emit();
  }

  onRejectClick(): void {
    this.reject.emit();
  }

  private refreshMap(): void {
    if (!this.map || !this.detail) {
      return;
    }

    const point: L.LatLngTuple = [this.detail.incidentLatitude, this.detail.incidentLongitude];
    if (!this.marker) {
      this.marker = L.marker(point, { icon: markerIcon }).addTo(this.map);
    } else {
      this.marker.setLatLng(point);
    }

    this.map.setView(point, 14);
    this.scheduleInvalidate();
  }

  private ensureMapInitialized(): void {
    if (!this.open || this.isLoading) {
      return;
    }

    const container = this.mapContainerRef?.nativeElement;
    if (!container) {
      setTimeout(() => {
        this.ensureMapInitialized();
        this.refreshMap();
      }, 0);
      return;
    }

    if (this.map && this.map.getContainer() !== container) {
      this.destroyMap();
    }

    if (this.map) {
      this.scheduleInvalidate();
      return;
    }

    this.map = L.map(container, {
      zoomControl: true,
      dragging: true,
      scrollWheelZoom: true,
      doubleClickZoom: true,
      touchZoom: true,
      keyboard: false,
    }).setView([-17.7833, -63.1821], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap contributors',
    }).addTo(this.map);

    this.scheduleInvalidate();
  }

  private destroyMap(): void {
    this.map?.remove();
    this.map = null;
    this.marker = null;
  }

  private scheduleInvalidate(): void {
    setTimeout(() => this.map?.invalidateSize(), 0);
    setTimeout(() => this.map?.invalidateSize(), 120);
    setTimeout(() => this.map?.invalidateSize(), 280);
  }
}
