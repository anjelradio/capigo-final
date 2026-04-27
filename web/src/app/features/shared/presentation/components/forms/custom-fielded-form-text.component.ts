import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { ControlContainer, FormGroupDirective, ReactiveFormsModule } from '@angular/forms';

@Component({
  selector: 'app-custom-fielded-form-text',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  viewProviders: [{ provide: ControlContainer, useExisting: FormGroupDirective }],
  template: `
    <label class="block space-y-1.5">
      <span class="text-sm font-medium text-[var(--auth-label)]">{{ label }}</span>
      <input
        [attr.type]="type"
        [formControlName]="name"
        [attr.placeholder]="placeholder"
        [attr.autocomplete]="autocomplete || null"
        [attr.inputmode]="inputMode || null"
        [attr.maxlength]="maxLength"
        class="h-12 w-full rounded-[var(--auth-control-radius)] border border-[var(--auth-input-border)] bg-[var(--auth-input-bg)] px-4 text-sm text-[var(--app-text-primary)] outline-none ring-0 transition placeholder:text-[var(--auth-input-placeholder)] focus:border-[var(--auth-input-focus)]"
        [ngClass]="className"
      />
    </label>
  `,
})
export class CustomFieldedFormTextComponent {
  @Input({ required: true }) name = '';
  @Input() label = '';
  @Input() placeholder = '';
  @Input() type: 'text' | 'email' | 'password' | 'tel' | 'number' | 'datetime-local' = 'text';
  @Input() autocomplete = '';
  @Input() inputMode = '';
  @Input() maxLength: number | null = null;
  @Input() className = '';
}
