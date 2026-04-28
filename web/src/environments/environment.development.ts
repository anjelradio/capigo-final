import { runtimeApiUrl } from './runtime-env';

export const environment = {
  production: false,
  appName: 'CAPIGO (Dev)',
  apiUrl: runtimeApiUrl ?? 'http://localhost:8000/api',
} as const;
