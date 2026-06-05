import { CommonModule } from '@angular/common';
import { Component, EventEmitter, HostListener, Input, Output } from '@angular/core';

@Component({
  selector: 'app-modal',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div
      *ngIf="open"
      class="fixed inset-0 z-[2000] flex items-center justify-center bg-black/35 px-4"
      (click)="onBackdropClick($event)"
    >
      <section
        class="relative w-full max-w-lg rounded-2xl border border-[var(--dashboard-card-default-border)] bg-[var(--app-card-bg)] shadow-2xl"
        [ngClass]="panelClass"
      >
        <button
          *ngIf="showCloseButton"
          type="button"
          aria-label="Cerrar modal"
          class="absolute right-4 top-4 grid h-8 w-8 place-items-center rounded-full text-[var(--app-text-secondary)] transition hover:bg-[var(--app-card-soft-bg)]"
          (click)="close()"
        >
          ×
        </button>

        <ng-content />
      </section>
    </div>
  `,
})
export class AppModalComponent {
  @Input() open = false;
  @Input() panelClass = '';
  @Input() showCloseButton = true;

  @Output() openChange = new EventEmitter<boolean>();

  @HostListener('document:keydown.escape')
  onEscape(): void {
    if (!this.open) {
      return;
    }

    this.close();
  }

  onBackdropClick(event: MouseEvent): void {
    if (event.target === event.currentTarget) {
      this.close();
    }
  }

  close(): void {
    this.openChange.emit(false);
  }
}
