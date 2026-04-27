export function parseError(error: unknown): string[] {
  if (!error || typeof error !== 'object') {
    return ['Error desconocido'];
  }

  const detail = (error as { detail?: unknown }).detail;

  if (typeof detail === 'string') {
    return [detail];
  }

  if (Array.isArray(detail)) {
    return detail
      .map((entry) => {
        if (entry && typeof entry === 'object' && 'msg' in entry) {
          const msg = (entry as { msg?: unknown }).msg;
          return typeof msg === 'string' ? msg : null;
        }
        return null;
      })
      .filter((msg): msg is string => msg !== null);
  }

  return ['Error desconocido'];
}
