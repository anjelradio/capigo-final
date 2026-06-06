import { CommonModule } from '@angular/common';
import {
  AfterViewInit,
  Component,
  ElementRef,
  Input,
  OnChanges,
  OnDestroy,
  SimpleChanges,
  ViewChild,
} from '@angular/core';
import * as L from 'leaflet';

import type { RepairShopDashboardZoneData } from '../../../../repair-shop/data/schemas/repair-shop-dashboard.schema';

@Component({
  selector: 'app-owner-home-zones-map',
  standalone: true,
  imports: [CommonModule],
  template: `<div #mapContainer class="h-full min-h-[320px] w-full rounded-[22px]"></div>`,
})
export class OwnerHomeZonesMapComponent implements AfterViewInit, OnChanges, OnDestroy {
  @Input() zones: RepairShopDashboardZoneData[] = [];

  @ViewChild('mapContainer', { static: true })
  private mapContainerRef!: ElementRef<HTMLDivElement>;

  private map: L.Map | null = null;
  private zonesLayer: L.LayerGroup | null = null;

  ngAfterViewInit(): void {
    this.map = L.map(this.mapContainerRef.nativeElement, {
      zoomControl: true,
      dragging: true,
      scrollWheelZoom: true,
      doubleClickZoom: true,
      touchZoom: true,
      keyboard: false,
    }).setView([-17.7833, -63.1821], 12);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap contributors',
    }).addTo(this.map);

    this.zonesLayer = L.layerGroup().addTo(this.map);
    this.renderZones();
    setTimeout(() => this.map?.invalidateSize(), 0);
  }

  ngOnChanges(_: SimpleChanges): void {
    this.renderZones();
  }

  ngOnDestroy(): void {
    this.map?.remove();
    this.map = null;
    this.zonesLayer = null;
  }

  private renderZones(): void {
    if (!this.map || !this.zonesLayer) {
      return;
    }

    this.zonesLayer.clearLayers();
    const points: L.LatLngTuple[] = [];

    this.zones
      .filter((zone) => zone.latitude !== null && zone.longitude !== null)
      .forEach((zone) => {
        const latitude = Number(zone.latitude);
        const longitude = Number(zone.longitude);
        const point: L.LatLngTuple = [latitude, longitude];
        points.push(point);

        const marker = L.circleMarker(point, {
          radius: Math.min(8 + zone.count * 1.8, 24),
          color: '#1F6EA8',
          weight: 2,
          fillColor: '#1F6EA8',
          fillOpacity: 0.22,
        });

        marker.bindPopup(
          `<strong>${zone.label}</strong><br/>Casos: ${zone.count}<br/>${zone.percentage}% del periodo`,
        );
        marker.addTo(this.zonesLayer as L.LayerGroup);
      });

    if (points.length === 1) {
      this.map.setView(points[0], 13);
      return;
    }

    if (points.length > 1) {
      this.map.fitBounds(L.latLngBounds(points), { padding: [28, 28] });
      return;
    }

    this.map.setView([-17.7833, -63.1821], 12);
  }
}
