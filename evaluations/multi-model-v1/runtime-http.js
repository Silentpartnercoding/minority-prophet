import { createHash, randomUUID, timingSafeEqual } from 'node:crypto';
import { appendFileSync, mkdirSync } from 'node:fs';
import { dirname } from 'node:path';
import { createServer } from 'node:http';
import { performance } from 'node:perf_hooks';

import { hashObject } from './src/lib/hash.js';
import { executeMinorityProphetTool, MP_TOOL_CONTRACT_HASH } from './mp-tool-v2.js';
import { handleProvenanceServiceRoute } from './provenance-service.js';

const MAX_BODY_BYTES = 2_000_000;
const LOOPBACK = new Set(['127.0.0.1', '::1', 'localhost']);

function safeEqual(left, right) {
  if (typeof left !== 'string' || typeof right !== 'string') return false;
  const a = Buffer.from(left);
  const b = Buffer.from(right);
  return a.length === b.length && timingSafeEqual(a, b);
}

function authorized(header, token) {
  return Boolean(token) && safeEqual(header ?? '', `Bearer ${token}`);
}

function send(response, status, value, contentType = 'application/json') {
  const body = contentType === 'application/json' ? `${JSON.stringify(value)}\n` : value;
  response.writeHead(status, {
    'content-type': `${contentType}; charset=utf-8`,
    'cache-control': 'no-store',
    'content-security-policy': "default-src 'none'; frame-ancestors 'none'",
    'x-content-type-options': 'nosniff',
    'x-frame-options': 'DENY'
  });
  response.end(body);
}

async function readJson(request) {
  const chunks = [];
  let size = 0;
  for await (const chunk of request) {
    size += chunk.length;
    if (size > MAX_BODY_BYTES) throw new Error('request_too_large');
    chunks.push(chunk);
  }
  try { return JSON.parse(Buffer.concat(chunks).toString('utf8')); }
  catch { throw new Error('invalid_json'); }
}

function telemetryWriter(path) {
  if (!path) return () => {};
  mkdirSync(dirname(path), { recursive: true });
  return (event) => appendFileSync(path, `${JSON.stringify(event)}\n`, { encoding: 'utf8', mode: 0o600 });
}

export function runtimeReadiness({ host, token, allowInsecureLocal }) {
  const loopback = LOOPBACK.has(host);
  const authenticated = typeof token === 'string' && token.length >= 24;
  const ready = authenticated || (loopback && allowInsecureLocal);
  return {
    ready,
    loopback,
    authenticated,
    reason: ready ? null : 'configure a token of at least 24 characters or explicitly allow insecure loopback'
  };
}

export async function startRuntimeServer({
  host = process.env.MP_ENGINE_HOST ?? '127.0.0.1',
  port = Number(process.env.MP_ENGINE_PORT ?? 8421),
  token = process.env.MP_ENGINE_TOKEN ?? '',
  telemetryPath = process.env.MP_ENGINE_TELEMETRY_PATH ?? '',
  allowInsecureLocal = process.env.MP_ENGINE_ALLOW_INSECURE_LOCAL === '1'
} = {}) {
  const readiness = runtimeReadiness({ host, token, allowInsecureLocal });
  if (!readiness.ready) throw new Error(readiness.reason);
  const bypassAuth = readiness.loopback && allowInsecureLocal;
  const record = telemetryWriter(telemetryPath);
  const metrics = { requests: 0, rejected: 0, analysis: 0, failures: 0 };
  const server = createServer(async (request, response) => {
    const requestId = request.headers['x-request-id']?.toString() ?? randomUUID();
    const started = performance.now();
    metrics.requests += 1;
    try {
      const url = new URL(request.url, `http://${request.headers.host ?? 'localhost'}`);
      if (request.method === 'GET' && url.pathname === '/healthz') {
        send(response, 200, { status: 'ok', service: 'minority-prophet-engine', request_id: requestId });
        return;
      }
      if (request.method === 'GET' && url.pathname === '/readyz') {
        send(response, readiness.ready ? 200 : 503, { ...readiness, service: 'minority-prophet-engine', request_id: requestId });
        return;
      }
      if (request.method === 'GET' && url.pathname === '/metrics') {
        const lines = Object.entries(metrics).map(([name, value]) => `mp_engine_${name}_total ${value}`);
        send(response, 200, `${lines.join('\n')}\n`, 'text/plain');
        return;
      }
      if (url.pathname === '/internal/provenance/compile') {
        const handled = await handleProvenanceServiceRoute(request, response, url, { provenanceToken: token });
        if (handled) {
          record({ schema: 'mp-runtime-event.v1', timestamp: new Date().toISOString(), request_id: requestId,
            event: 'provenance_compile', status: response.statusCode, duration_ms: performance.now() - started });
          return;
        }
      }
      if (request.method !== 'POST' || url.pathname !== '/v1/analyze') {
        send(response, 404, { error: 'not_found', request_id: requestId });
        return;
      }
      if (!bypassAuth && !authorized(request.headers.authorization, token)) {
        metrics.rejected += 1;
        send(response, 401, { error: 'unauthorized', request_id: requestId });
        return;
      }
      const input = await readJson(request);
      const output = executeMinorityProphetTool(input);
      const receipt = {
        schema: 'mp-analysis-receipt.v1',
        request_id: requestId,
        read_only: true,
        grants_protected_action_authority: false,
        contract_hash: MP_TOOL_CONTRACT_HASH,
        input_hash: hashObject(input),
        output
      };
      metrics.analysis += 1;
      send(response, 200, receipt);
      record({ schema: 'mp-runtime-event.v1', timestamp: new Date().toISOString(), request_id: requestId,
        event: 'analysis_completed', input_hash: receipt.input_hash, output_hash: hashObject(output),
        duration_ms: performance.now() - started, grants_protected_action_authority: false });
    } catch (error) {
      metrics.failures += 1;
      const status = error.message === 'request_too_large' ? 413 : error.message === 'invalid_json' ? 400 : 422;
      send(response, status, { error: error.message, request_id: requestId });
      record({ schema: 'mp-runtime-event.v1', timestamp: new Date().toISOString(), request_id: requestId,
        event: 'request_failed', error_code: createHash('sha256').update(error.message).digest('hex').slice(0, 16),
        status, duration_ms: performance.now() - started });
    }
  });
  await new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(port, host, resolve);
  });
  return server;
}
