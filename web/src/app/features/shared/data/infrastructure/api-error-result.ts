import { type ZodError, type ZodType } from 'zod';

import { type ApiError } from '../types/api-result';

type ValidationErrors = Record<string, string[] | undefined>;

function asObject(value: unknown): Record<string, unknown> | null {
  return value && typeof value === 'object' ? (value as Record<string, unknown>) : null;
}

function mapFastApiValidationErrors(data: unknown): ValidationErrors | null {
  const payload = asObject(data);
  if (!payload) {
    return null;
  }

  const detail = payload['detail'];
  if (!Array.isArray(detail)) {
    return null;
  }

  const fieldErrors: ValidationErrors = {};

  for (const entry of detail) {
    const item = asObject(entry);
    if (!item) {
      continue;
    }

    const msg = item['msg'];
    const loc = item['loc'];

    if (typeof msg !== 'string' || !Array.isArray(loc)) {
      continue;
    }

    const path = loc
      .map((segment) => String(segment))
      .filter((segment) => segment !== 'body')
      .join('.');

    const key = path || 'form';
    fieldErrors[key] = [...(fieldErrors[key] ?? []), msg];
  }

  return Object.keys(fieldErrors).length > 0 ? fieldErrors : null;
}

function mapFastApiErrors(data: unknown): string[] | null {
  const payload = asObject(data);
  if (!payload) {
    return null;
  }

  if (typeof payload['detail'] === 'string') {
    return [payload['detail']];
  }

  if (
    Array.isArray(payload['errors']) &&
    payload['errors'].every((item) => typeof item === 'string')
  ) {
    return payload['errors'] as string[];
  }

  if (Array.isArray(payload['detail'])) {
    const messages = payload['detail']
      .map((entry) => {
        const item = asObject(entry);
        if (!item || typeof item['msg'] !== 'string') {
          return null;
        }

        return item['msg'];
      })
      .filter((message): message is string => message !== null);

    if (messages.length > 0) {
      return messages;
    }
  }

  return null;
}

async function parseResponseData(res: Response): Promise<unknown> {
  try {
    return await res.json();
  } catch {
    return null;
  }
}

export function errorResult(message: string): ApiError {
  return {
    ok: false,
    errors: [message],
  };
}

export function mapValidationErrorsToMessages(validationErrors: ValidationErrors): string[] {
  return Object.values(validationErrors).flatMap((messages) => messages ?? []);
}

export function zodValidationErrorResult(error: ZodError): ApiError {
  const validationErrors = error.flatten().fieldErrors;

  return {
    ok: false,
    validationErrors,
    errors: mapValidationErrorsToMessages(validationErrors),
  };
}

export async function serverErrorResult(res: Response, fallbackMessage: string): Promise<ApiError> {
  const responseData = await parseResponseData(res);
  const messages = mapFastApiErrors(responseData);

  if (messages && messages.length > 0) {
    return {
      ok: false,
      errors: messages,
    };
  }

  return errorResult(fallbackMessage);
}

export async function serverValidationErrorResult(
  res: Response,
  schema: ZodType<Record<string, string[]>>,
  fallbackMessage: string,
): Promise<ApiError> {
  const responseData = await parseResponseData(res);
  const parsedResult = schema.safeParse(responseData);

  if (parsedResult.success) {
    return {
      ok: false,
      validationErrors: parsedResult.data,
      errors: mapValidationErrorsToMessages(parsedResult.data),
    };
  }

  const fastApiValidationErrors = mapFastApiValidationErrors(responseData);
  if (fastApiValidationErrors) {
    return {
      ok: false,
      validationErrors: fastApiValidationErrors,
      errors: mapValidationErrorsToMessages(fastApiValidationErrors),
    };
  }

  const messages = mapFastApiErrors(responseData);
  if (messages && messages.length > 0) {
    return {
      ok: false,
      errors: messages,
    };
  }

  return errorResult(fallbackMessage);
}
