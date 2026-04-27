import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-page-heading',
  standalone: true,
  template: `
    <section>
      <h1 class="text-4xl font-semibold tracking-tight text-[var(--app-text-on-dark)] sm:text-5xl">
        {{ title }}
      </h1>
      <p class="mt-2 text-base text-[var(--app-text-on-dark-muted)]">{{ subtitle }}</p>
    </section>
  `,
})
export class PageHeadingComponent {
  @Input({ required: true }) title!: string;
  @Input() subtitle = '';
}
