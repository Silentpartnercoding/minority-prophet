import { createHash } from 'node:crypto';

export function canonicalize(value) {
  if (Array.isArray(value)) return `[${value.map(canonicalize).join(',')}]`;
  if (value && typeof value === 'object') return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${canonicalize(value[key])}`).join(',')}}`;
  return JSON.stringify(value);
}

export function sha256(value) { return createHash('sha256').update(typeof value === 'string' ? value : canonicalize(value)).digest('hex'); }
export function hashObject(value) { return `sha256:${sha256(value)}`; }
