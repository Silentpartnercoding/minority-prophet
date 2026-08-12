import { hashObject, sha256 } from './src/lib/hash.js';
export function slug(value) { return String(value).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, ''); }
export function trialKey(value) { return sha256(value); }
export function recordId(prefix, value) { return `${prefix}_${sha256(value).slice(0, 20)}`; }
export function integrityEnvelope(value) { return { hash: hashObject(value), algorithm: 'sha256', canonicalization: 'sorted-json-v1' }; }
