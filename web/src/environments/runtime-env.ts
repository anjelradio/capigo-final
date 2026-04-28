type RuntimeEnv = {
  API_URL?: string;
};

declare global {
  interface Window {
    __env?: RuntimeEnv;
  }
}

function readRuntimeApiUrl(): string | undefined {
  if (typeof window === 'undefined') {
    return undefined;
  }

  const value = window.__env?.API_URL?.trim();
  if (!value) {
    return undefined;
  }

  return value.replace(/\/+$/, '');
}

export const runtimeApiUrl = readRuntimeApiUrl();
