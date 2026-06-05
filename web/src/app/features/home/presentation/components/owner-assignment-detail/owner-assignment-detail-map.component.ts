import { CommonModule } from '@angular/common';
import { AfterViewInit, Component, ElementRef, Input, OnChanges, OnDestroy, SimpleChanges, ViewChild } from '@angular/core';
import * as L from 'leaflet';

const incidentIcon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const shopIcon = L.divIcon({
  className: 'shop-marker',
  html: '<div style="width:14px;height:14px;border-radius:9999px;background:#64748b;border:2px solid white;box-shadow:0 0 0 2px rgba(100,116,139,0.25);"></div>',
  iconSize: [14, 14],
  iconAnchor: [7, 7],
});

const mechanicIcon = L.divIcon({
  className: 'mechanic-marker',
  html: '<div style="width:14px;height:14px;border-radius:9999px;background:#0ea5e9;border:2px solid white;box-shadow:0 0 0 2px rgba(14,165,233,0.25);"></div>',
  iconSize: [14, 14],
  iconAnchor: [7, 7],
});

@Component({
  selector: 'app-owner-assignment-detail-map',
  standalone: true,
  imports: [CommonModule],
  template: `<div #mapContainer class="h-full w-full"></div>`,
})
export class OwnerAssignmentDetailMapComponent implements AfterViewInit, OnChanges, OnDestroy {
  @Input() incidentLatitude: number | null = null;
  @Input() incidentLongitude: number | null = null;
  @Input() shopLatitude: number | null = null;
  @Input() shopLongitude: number | null = null;
  @Input() mechanicLatitude: number | null = null;
  @Input() mechanicLongitude: number | null = null;

  @ViewChild('mapContainer', { static: true })
  private mapContainerRef!: ElementRef<HTMLDivElement>;

  private map: L.Map | null = null;
  private incidentMarker: L.Marker | null = null;
  private shopMarker: L.Marker | null = null;
  private mechanicMarker: L.Marker | null = null;
  private hasCenteredMap = false;

  ngAfterViewInit(): void {
    this.map = L.map(this.mapContainerRef.nativeElement, {
      zoomControl: false,
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

    this.refreshMarkers();
    this.scheduleInvalidate();
  }

  ngOnChanges(_: SimpleChanges): void {
    this.refreshMarkers();
  }

  ngOnDestroy(): void {
    this.map?.remove();
    this.map = null;
  }

  private refreshMarkers(): void {
    if (!this.map) return;

    if (this.incidentLatitude !== null && this.incidentLongitude !== null) {
      const incidentPoint: L.LatLngTuple = [this.incidentLatitude, this.incidentLongitude];
      if (!this.incidentMarker) {
        this.incidentMarker = L.marker(incidentPoint, { icon: incidentIcon }).addTo(this.map);
      } else {
        this.incidentMarker.setLatLng(incidentPoint);
      }
      this.incidentMarker.bindPopup('Ubicacion del incidente');

      if (!this.hasCenteredMap) {
        this.map.setView(incidentPoint, 15);
        this.hasCenteredMap = true;
      }
    }

    if (this.shopLatitude !== null && this.shopLongitude !== null) {
      const shopPoint: L.LatLngTuple = [this.shopLatitude, this.shopLongitude];
      if (!this.shopMarker) {
        this.shopMarker = L.marker(shopPoint, { icon: shopIcon }).addTo(this.map);
      } else {
        this.shopMarker.setLatLng(shopPoint);
      }
      this.shopMarker.bindPopup('Ubicacion del taller');
    } else if (this.shopMarker) {
      this.map.removeLayer(this.shopMarker);
      this.shopMarker = null;
    }

    if (this.mechanicLatitude !== null && this.mechanicLongitude !== null) {
      const mechanicPoint: L.LatLngTuple = [this.mechanicLatitude, this.mechanicLongitude];
      if (!this.mechanicMarker) {
        this.mechanicMarker = L.marker(mechanicPoint, { icon: mechanicIcon }).addTo(this.map);
      } else {
        this.mechanicMarker.setLatLng(mechanicPoint);
      }
      this.mechanicMarker.bindPopup('Ubicacion del mecanico');
    } else if (this.mechanicMarker) {
      this.map.removeLayer(this.mechanicMarker);
      this.mechanicMarker = null;
    }
  }

  private scheduleInvalidate(): void {
    setTimeout(() => this.map?.invalidateSize(), 0);
    setTimeout(() => this.map?.invalidateSize(), 120);
  }
}
