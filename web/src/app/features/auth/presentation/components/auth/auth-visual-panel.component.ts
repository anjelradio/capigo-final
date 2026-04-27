import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-auth-visual-panel',
  standalone: true,
  template: `
    <section class="hidden h-full items-center justify-center md:flex">
      <img
        [src]="imageUrl"
        [alt]="alt"
        class="h-[78vh] max-h-[740px] w-full rounded-[34px] object-cover shadow-2xl shadow-[var(--auth-image-shadow)]"
      />
    </section>
  `,
})
export class AuthVisualPanelComponent {
  @Input({ required: true }) imageUrl!: string;
  @Input() alt = 'Imagen';
}
