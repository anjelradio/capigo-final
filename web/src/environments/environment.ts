import { runtimeApiUrl } from './runtime-env';

export const environment = {
  production: true,
  appName: 'CAPIGO',
  apiUrl: runtimeApiUrl ?? 'http://localhost:8000/api',
} as const;
