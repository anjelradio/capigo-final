import { Injectable } from '@angular/core';
import { Observable, map } from 'rxjs';
import { ToastrService } from 'ngx-toastr';

const DEFAULT_ERROR_MESSAGE = 'Ocurrio un error inesperado';

@Injectable({ providedIn: 'root' })
export class AppToastService {
  constructor(private readonly toastr: ToastrService) {}

  showErrorList(messages?: string[]): void {
    if (!messages || messages.length === 0) {
      this.toastr.error(DEFAULT_ERROR_MESSAGE);
      return;
    }

    const uniqueMessages = [...new Set(messages.filter(Boolean))];
    uniqueMessages.forEach((message) => this.toastr.error(message));
  }

  success(message: string): void {
    this.toastr.success(message);
  }

  error(message: string): void {
    this.toastr.error(message);
  }

  info(message: string): void {
    this.toastr.info(message);
  }

  infoClickable(message: string, title?: string): Observable<void> | null {
    const toastRef = this.toastr.info(message, title, {
      disableTimeOut: false,
      tapToDismiss: true,
      closeButton: true,
      timeOut: 8000,
    });

    if (!toastRef) {
      return null;
    }

    return toastRef.onTap.pipe(map(() => undefined));
  }

  warning(message: string): void {
    this.toastr.warning(message);
  }
}
