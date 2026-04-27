import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { catchError, throwError } from 'rxjs';

import { parseError } from '../utils/error-parser';

export interface NormalizedHttpError {
  status: number;
  messages: string[];
}

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  return next(req).pipe(
    catchError((error: unknown) => {
      if (error instanceof HttpErrorResponse) {
        const normalized: NormalizedHttpError = {
          status: error.status,
          messages: parseError(error.error),
        };

        return throwError(() => normalized);
      }

      return throwError(
        () =>
          ({
            status: 0,
            messages: ['Error inesperado del cliente'],
          }) as NormalizedHttpError,
      );
    }),
  );
};
