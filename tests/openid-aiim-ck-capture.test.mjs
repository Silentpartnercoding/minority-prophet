import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { generateKeyPairSync } from 'node:crypto';
import { afterEach, test } from 'node:test';
import { DatabaseSync } from 'node:sqlite';
import { handleOpenIdAiimCk } from '../worker/openid-aiim-ck.ts';

const originalFetch = globalThis.fetch;
afterEach(() => { globalThis.fetch = originalFetch; });

test('capture migration creates an append-only run and sequence table', () => {
  const sql = readFileSync(new URL('../migrations/0007_openid_aiim_ck_capture.sql', import.meta.url), 'utf8');
  const db = new DatabaseSync(':memory:');
  db.exec(sql);
  db.prepare('INSERT INTO openid_aiim_ck_capture (run_id, seq, at, record_json) VALUES (?, ?, ?, ?)').run('run-1', 0, '2026-09-28T00:00:00.000Z', '{"phase":"tokenless_mcp"}');
  assert.deepEqual({ ...db.prepare('SELECT run_id, seq, record_json FROM openid_aiim_ck_capture').get() }, { run_id: 'run-1', seq: 0, record_json: '{"phase":"tokenless_mcp"}' });
  assert.throws(() => db.prepare('INSERT INTO openid_aiim_ck_capture (run_id, seq, at, record_json) VALUES (?, ?, ?, ?)').run('run-1', 0, '2026-09-28T00:00:01.000Z', '{}'));
  db.close();
});

test('Sites build packages an executable capture migration for production D1', () => {
  const base = new URL('../dist/.openai/drizzle/', import.meta.url);
  const journal = JSON.parse(readFileSync(new URL('meta/_journal.json', base), 'utf8'));
  assert.ok(journal.entries.length > 0);
  const db = new DatabaseSync(':memory:');
  for (const { tag } of journal.entries) {
    const sql = readFileSync(new URL(`${tag}.sql`, base), 'utf8');
    db.exec(sql.replaceAll('--> statement-breakpoint', ''));
  }
  const tables = db.prepare("SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'openid_aiim_ck_capture'").all();
  assert.deepEqual(tables.map(({ name }) => name), ['openid_aiim_ck_capture']);
  db.close();
});

test('capture storage failure stops before the first partner request', async () => {
  let networkCalls = 0;
  globalThis.fetch = async () => { networkCalls += 1; throw new Error('Partner must not be contacted'); };
  const db = { prepare() { return { bind() { return { async run() { throw new Error('D1 unavailable'); } }; } }; } };
  const response = await handleOpenIdAiimCk(new Request('https://minorityprophet.org/openid-aiim/ck/start?mode=preregistered&capture=1'), { MP_AIIM_STATE_SECRET: 'local-only-synthetic-secret-1234567890', DB: db });
  assert.equal(response.status, 502);
  assert.equal(networkCalls, 0);
});

test('unsuccessful capture write stops before the first partner request', async () => {
  let networkCalls = 0;
  globalThis.fetch = async () => { networkCalls += 1; throw new Error('Partner must not be contacted'); };
  const db = { prepare() { return { bind() { return { async run() { return { success: false }; } }; } }; } };
  const response = await handleOpenIdAiimCk(new Request('https://minorityprophet.org/openid-aiim/ck/start?mode=preregistered&capture=1'), { MP_AIIM_STATE_SECRET: 'local-only-synthetic-secret-1234567890', DB: db });
  assert.equal(response.status, 502);
  assert.equal(networkCalls, 0);
});

test('reproduce page exposes an explicit recorded cold-run path', async () => {
  const response = await handleOpenIdAiimCk(new Request('https://minorityprophet.org/openid-aiim/ck/reproduce'));
  const html = await response.text();
  assert.match(html, /\/openid-aiim\/ck\/start\?mode=preregistered&amp;capture=1/u);
  assert.match(html, /Record cold OAuth run/u);
});

function fakeDb() {
  const rows = [];
  const sqlite = new DatabaseSync(':memory:');
  sqlite.exec(readFileSync(new URL('../migrations/0007_openid_aiim_ck_capture.sql', import.meta.url), 'utf8'));
  return {
    rows,
    prepare(sql) {
      assert.match(sql, /INSERT INTO openid_aiim_ck_capture/u);
      const statement = sqlite.prepare(sql);
      return {
        bind(...values) {
          return { async run() { statement.run(...values); rows.push(values); return { success: true }; } };
        },
      };
    },
  };
}

function json(body, status = 200, headers = {}) {
  return new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json', ...headers } });
}

test('opt-in cold start records tokenless challenge before discovery and preserves PKCE fields', async () => {
  const calls = [];
  globalThis.fetch = async (input, init = {}) => {
    const request = input instanceof Request ? input : new Request(input, init);
    calls.push({ method: request.method, url: request.url, headers: request.headers, body: await request.text() });
    if (request.url === 'https://mcp.braas.dev/mcp') {
      return json({ error: 'unauthorized' }, 401, { 'www-authenticate': 'Bearer resource_metadata="https://mcp.braas.dev/.well-known/oauth-protected-resource", scope="mcp"' });
    }
    if (request.url === 'https://mcp.braas.dev/.well-known/oauth-protected-resource') {
      return json({ resource: 'https://mcp.braas.dev/mcp', authorization_servers: ['https://as.braas.dev'], scopes_supported: ['mcp'] });
    }
    if (request.url === 'https://as.braas.dev/.well-known/oauth-authorization-server') {
      return json({ issuer: 'https://as.braas.dev', authorization_endpoint: 'https://as.braas.dev/authorize', token_endpoint: 'https://as.braas.dev/token', code_challenge_methods_supported: ['S256'], token_endpoint_auth_methods_supported: ['none', 'private_key_jwt'], token_endpoint_auth_signing_alg_values_supported: ['RS256'], client_id_metadata_document_supported: true });
    }
    throw new Error(`Unexpected network request: ${request.url}`);
  };
  const db = fakeDb();
  const response = await handleOpenIdAiimCk(new Request('https://minorityprophet.org/openid-aiim/ck/start?mode=preregistered&capture=1'), { MP_AIIM_STATE_SECRET: 'local-only-synthetic-secret-1234567890', DB: db });
  assert.equal(response.status, 302);
  assert.deepEqual(calls.map(({ method, url }) => `${method} ${url}`), [
    'POST https://mcp.braas.dev/mcp',
    'GET https://mcp.braas.dev/.well-known/oauth-protected-resource',
    'GET https://as.braas.dev/.well-known/oauth-authorization-server',
  ]);
  assert.equal(calls[0].headers.has('authorization'), false);
  const authorizationUrl = new URL(response.headers.get('location'));
  assert.equal(authorizationUrl.searchParams.get('code_challenge_method'), 'S256');
  assert.ok(authorizationUrl.searchParams.get('code_challenge'));
  const records = db.rows.map(([, , , body]) => JSON.parse(body));
  assert.deepEqual(records.map(({ phase }) => phase), ['capture_start', 'tokenless_mcp', 'oprm', 'authorization_server_metadata', 'authorization_redirect']);
  assert.equal(records[1].response.status, 401);
  assert.match(records[1].response.headers['www-authenticate'], /resource_metadata=/u);
  assert.equal(new URL(records[4].request.url).searchParams.get('code_challenge_method'), 'S256');
  assert.equal(new URL(records[4].request.url).searchParams.get('state'), '<redacted>');
});

test('one captured run keeps token exchange and authenticated MCP wire fields while redacting live values', async () => {
  const db = fakeDb();
  const calls = [];
  globalThis.fetch = async (input, init = {}) => {
    const request = input instanceof Request ? input : new Request(input, init);
    const body = await request.text();
    calls.push({ url: request.url, method: request.method, authorization: request.headers.get('authorization'), body });
    if (request.url === 'https://mcp.braas.dev/mcp' && !request.headers.has('authorization')) {
      return json({ error: 'unauthorized' }, 401, { 'www-authenticate': 'Bearer resource_metadata="https://mcp.braas.dev/.well-known/oauth-protected-resource", scope="mcp"' });
    }
    if (request.url === 'https://mcp.braas.dev/.well-known/oauth-protected-resource') {
      return json({ resource: 'https://mcp.braas.dev/mcp', authorization_servers: ['https://as.braas.dev'], scopes_supported: ['mcp'] });
    }
    if (request.url === 'https://as.braas.dev/.well-known/oauth-authorization-server') {
      return json({ issuer: 'https://as.braas.dev', authorization_endpoint: 'https://as.braas.dev/authorize', token_endpoint: 'https://as.braas.dev/token', code_challenge_methods_supported: ['S256'], token_endpoint_auth_methods_supported: ['none', 'private_key_jwt'], token_endpoint_auth_signing_alg_values_supported: ['RS256'], client_id_metadata_document_supported: true });
    }
    if (request.url === 'https://as.braas.dev/token') {
      assert.match(body, /code_verifier=/u);
      return json({ access_token: 'TEST_ACCESS_TOKEN', token_type: 'Bearer', scope: 'mcp' });
    }
    if (request.url === 'https://mcp.braas.dev/mcp') {
      assert.equal(request.headers.get('authorization'), 'Bearer TEST_ACCESS_TOKEN');
      const method = JSON.parse(body).method;
      if (method === 'initialize') return new Response('event: message\ndata: {"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2025-06-18","capabilities":{}}}\n\n', { status: 200, headers: { 'content-type': 'text/event-stream', 'Mcp-Session-Id': 'TEST_SESSION_ID' } });
      if (method === 'notifications/initialized') return new Response(null, { status: 202 });
      if (method === 'tools/list') return json({ jsonrpc: '2.0', id: 2, result: { tools: [{ name: 'first_contact_ping' }, { name: 'file_read' }] } });
      if (method === 'tools/call') return json({ jsonrpc: '2.0', id: 3, result: { content: [{ type: 'text', text: 'pong' }], isError: false } });
    }
    throw new Error(`Unexpected network request: ${request.url}`);
  };
  const env = { MP_AIIM_STATE_SECRET: 'local-only-synthetic-secret-1234567890', DB: db };
  const start = await handleOpenIdAiimCk(new Request('https://minorityprophet.org/openid-aiim/ck/start?mode=preregistered&capture=1'), env);
  assert.equal(start.status, 302);
  const state = new URL(start.headers.get('location')).searchParams.get('state');
  const cookie = start.headers.get('set-cookie').split(';')[0];
  const callback = await handleOpenIdAiimCk(new Request(`https://minorityprophet.org/openid-aiim/callback?code=TEST_AUTH_CODE&state=${state}&iss=https%3A%2F%2Fas.braas.dev`, { headers: { cookie } }), env);
  assert.equal(callback.status, 200);
  assert.match(await callback.text(), /CK interoperability path completed/u);
  const records = db.rows.map(([, , , body]) => JSON.parse(body));
  assert.equal(new Set(db.rows.map(([runId]) => runId)).size, 1);
  assert.deepEqual(db.rows.map(([, seq]) => seq), records.map((_, seq) => seq));
  assert.deepEqual(records.map(({ phase }) => phase), [
    'capture_start', 'tokenless_mcp', 'oprm', 'authorization_server_metadata', 'authorization_redirect',
    'authorization_callback', 'token_exchange', 'mcp_initialize', 'mcp_initialized_notification', 'tools_list', 'tools_call',
  ]);
  assert.equal(new URL(records[5].request.url).searchParams.get('code'), '<redacted>');
  assert.equal(new URLSearchParams(records[6].request.body).get('code_verifier'), '<redacted>');
  assert.equal(new URLSearchParams(records[6].request.body).get('code'), '<redacted>');
  assert.equal(JSON.parse(records[6].response.body).access_token, '<redacted>');
  assert.equal(records[7].request.headers.authorization, '<redacted>');
  assert.match(records[7].response.body, /data: \{"jsonrpc"/u);
  assert.equal(records[10].request.headers.authorization, '<redacted>');
  assert.ok(calls.some(({ url, authorization }) => url === 'https://mcp.braas.dev/mcp' && authorization === 'Bearer TEST_ACCESS_TOKEN'));
  const persisted = JSON.stringify(records);
  for (const secret of ['TEST_AUTH_CODE', 'TEST_ACCESS_TOKEN', 'TEST_SESSION_ID']) assert.equal(persisted.includes(secret), false);
});

test('CIMD token capture keeps decoded assertion evidence but not the signed assertion', async () => {
  const { privateKey } = generateKeyPairSync('rsa', { modulusLength: 2048, privateKeyEncoding: { type: 'pkcs8', format: 'pem' }, publicKeyEncoding: { type: 'spki', format: 'pem' } });
  const db = fakeDb();
  globalThis.fetch = async (input, init = {}) => {
    const request = input instanceof Request ? input : new Request(input, init);
    if (request.url === 'https://mcp.braas.dev/mcp') return json({ error: 'unauthorized' }, 401, { 'www-authenticate': 'Bearer resource_metadata="https://mcp.braas.dev/.well-known/oauth-protected-resource", scope="mcp"' });
    if (request.url === 'https://mcp.braas.dev/.well-known/oauth-protected-resource') return json({ resource: 'https://mcp.braas.dev/mcp', authorization_servers: ['https://as.braas.dev'], scopes_supported: ['mcp'] });
    if (request.url === 'https://as.braas.dev/.well-known/oauth-authorization-server') return json({ issuer: 'https://as.braas.dev', authorization_endpoint: 'https://as.braas.dev/authorize', token_endpoint: 'https://as.braas.dev/token', code_challenge_methods_supported: ['S256'], token_endpoint_auth_methods_supported: ['none', 'private_key_jwt'], token_endpoint_auth_signing_alg_values_supported: ['RS256'], client_id_metadata_document_supported: true });
    if (request.url === 'https://as.braas.dev/token') return json({ error: 'synthetic_stop' }, 400);
    throw new Error(`Unexpected network request: ${request.url}`);
  };
  const env = { MP_AIIM_STATE_SECRET: 'local-only-synthetic-secret-1234567890', MP_AIIM_CLIENT_PRIVATE_KEY: privateKey, DB: db };
  const start = await handleOpenIdAiimCk(new Request('https://minorityprophet.org/openid-aiim/ck/start?mode=cimd&capture=1'), env);
  const state = new URL(start.headers.get('location')).searchParams.get('state');
  const cookie = start.headers.get('set-cookie').split(';')[0];
  await handleOpenIdAiimCk(new Request(`https://minorityprophet.org/openid-aiim/callback?code=SYNTHETIC_CODE&state=${state}`, { headers: { cookie } }), env);
  const records = db.rows.map(([, , , body]) => JSON.parse(body));
  const token = records.find(({ phase }) => phase === 'token_exchange');
  assert.ok(token);
  const form = new URLSearchParams(token.request.body);
  assert.equal(form.get('client_assertion_type'), 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer');
  assert.equal(form.get('client_assertion'), '<redacted>');
  assert.deepEqual(token.assertion.header, { alg: 'RS256', kid: 'f35c5d1f-b07b-4525-9587-c0f21295a972' });
  assert.equal(token.assertion.claims.iss, 'https://minorityprophet.org/openid-aiim/client.json');
  assert.equal(token.assertion.claims.sub, 'https://minorityprophet.org/openid-aiim/client.json');
  assert.equal(token.assertion.claims.aud, 'https://as.braas.dev/token');
  assert.equal(typeof token.assertion.claims.exp, 'number');
  assert.equal(JSON.stringify(records).includes('BEGIN PRIVATE KEY'), false);
});
