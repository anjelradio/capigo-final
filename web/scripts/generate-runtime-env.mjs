import { writeFileSync } from 'node:fs';

const rawApiUrl = (process.env.API_URL ?? '').trim();

if (!rawApiUrl) {
  console.error('Missing API_URL environment variable.');
  process.exit(1);
}

const normalizedApiUrl = rawApiUrl.replace(/\/+$/, '');
const escapedApiUrl = normalizedApiUrl.replace(/\\/g, '\\\\').replace(/'/g, "\\'");
const targetFile = new URL('../public/env.js', import.meta.url);

writeFileSync(
  targetFile,
  `window.__env = {\n  API_URL: '${escapedApiUrl}',\n};\n`,
  'utf8',
);

console.log('Generated public/env.js from API_URL');
