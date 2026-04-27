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

const DEFAULT_CENTER: L.LatLngTuple = [-17.7833, -63.1821];

const markerIcon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

@Component({
  selector: 'app-location-picker-map',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div
      class="overflow-hidden rounded-3xl border border-[var(--app-card-soft-border)] bg-[var(--app-card-soft-bg)]"
    >
      <div #mapContainer class="h-80 w-full lg:h-[26rem]"></div>
    </div>
    <p class="mt-2 text-left text-xs text-[var(--auth-text-secondary)]">
      Lat: {{ selectedLatitude }} | Lng: {{ selectedLongitude }}
    </p>
  `,
})
export class LocationPickerMapComponent implements AfterViewInit, OnChanges, OnDestroy {
  @Input() open = false;
  @Input() latitude: number | null = null;
  @Input() longitude: number | null = null;
  @Output() locationChange = new EventEmitter<{ latitude: number; longitude: number }>();

  @ViewChild('mapContainer', { static: true })
  private mapContainerRef!: ElementRef<HTMLDivElement>;

  private map: L.Map | null = null;
  private marker: L.Marker | null = null;

  selectedLatitude = Number(DEFAULT_CENTER[0].toFixed(6));
  selectedLongitude = Number(DEFAULT_CENTER[1].toFixed(6));

  ngAfterViewInit(): void {
    const initialLat = this.latitude ?? DEFAULT_CENTER[0];
    const initialLng = this.longitude ?? DEFAULT_CENTER[1];
    this.setSelected(initialLat, initialLng, false);

    this.map = L.map(this.mapContainerRef.nativeElement, { zoomControl: true }).setView(
      [initialLat, initialLng],
      13,
    );

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap contributors',
    }).addTo(this.map);

    this.marker = L.marker([initialLat, initialLng], {
      draggable: true,
      icon: markerIcon,
    }).addTo(this.map);

    this.map.on('click', (event: L.LeafletMouseEvent) => {
      this.moveMarker(event.latlng.lat, event.latlng.lng);
    });

    this.marker.on('dragend', () => {
      const latLng = this.marker?.getLatLng();
      if (!latLng) {
        return;
      }

      this.setSelected(latLng.lat, latLng.lng, true);
    });

    this.scheduleInvalidate();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['open']?.currentValue === true) {
      this.scheduleInvalidate();
    }

    const changedLatitude = changes['latitude'];
    const changedLongitude = changes['longitude'];
    if (!this.map || (!changedLatitude && !changedLongitude)) {
      return;
    }

    const lat = this.latitude ?? this.selectedLatitude;
    const lng = this.longitude ?? this.selectedLongitude;
    this.moveMarker(lat, lng, false);
  }

  ngOnDestroy(): void {
    this.map?.remove();
    this.map = null;
    this.marker = null;
  }

  private moveMarker(latitude: number, longitude: number, emit = true): void {
    if (!this.marker || !this.map) {
      return;
    }

    this.marker.setLatLng([latitude, longitude]);
    this.map.panTo([latitude, longitude]);
    this.setSelected(latitude, longitude, emit);
  }

  private scheduleInvalidate(): void {
    setTimeout(() => this.map?.invalidateSize(), 0);
    setTimeout(() => this.map?.invalidateSize(), 120);
    setTimeout(() => this.map?.invalidateSize(), 320);
  }

  private setSelected(latitude: number, longitude: number, emit = true): void {
    this.selectedLatitude = Number(latitude.toFixed(6));
    this.selectedLongitude = Number(longitude.toFixed(6));

    if (emit) {
      this.locationChange.emit({
        latitude: this.selectedLatitude,
        longitude: this.selectedLongitude,
      });
    }
  }
}
