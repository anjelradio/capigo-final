export function normalizeUtcDateInput(value: string): string {
  const trimmedValue = value.trim();
  if (trimmedValue === '') {
    return value;
  }

  const hasTimezone = /(?:[zZ]|[+-]\d{2}:\d{2})$/.test(trimmedValue);
  return hasTimezone ? trimmedValue : `${trimmedValue}Z`;
}

export function formatUtcDateToLocal(
  value: string | null | undefined,
  fallback = 'No disponible',
): string {
  if (!value) {
    return fallback;
  }

  const date = new Date(normalizeUtcDateInput(value));
  return Number.isNaN(date.getTime()) ? fallback : date.toLocaleString();
}

export function parseLocalDateTimeInputToUtcIso(value: string): string | null {
  const trimmedValue = value.trim();
  if (trimmedValue === '') {
    return null;
  }

  const date = new Date(trimmedValue);
  if (Number.isNaN(date.getTime())) {
    return null;
  }

  return date.toISOString();
}

export function toDatetimeLocalInputValue(date: Date): string {
  const localDate = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
  return localDate.toISOString().slice(0, 16);
}
