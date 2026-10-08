import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { generateKeyPairSync } from 'node:crypto';
import { afterEach, test } from 'node:test';
import { DatabaseSync } from 'node:sqlite';
import { handleOpenIdAiim } from '../worker/openid-aiim.ts';

const RESOURCE = 'https://mp-interop-referee.tradearmory.workers.dev/mcp';
const OPRM = 'https://mp-interop-referee.tradearmory.workers.dev/.well-known/oauth-protected-resource/mcp';
const ISSUER = 'https://api.descope.com/v1/apps/agentic/P3IEQH7e0pGsj5aPR5PQPZQI6pfA/RS3IQSxDIjEhYYhuVkuey7uly21NB';
const AUTHORIZE = `${ISSUER.replace('/v1/', '/oauth2/v1/')}/authorize`;
const TOKEN = `${ISSUER.replace('/v1/', '/oauth2/v1/')}/token`;
const FERENTIN_RESOURCE = 'https://mock-test.mcp.ferentin.net/v1/ferentin-docs-server';
const FERENTIN_OPRM = `${FERENTIN_RESOURCE}/.well-known/oauth-protected-resource`;
const FERENTIN_ISSUER = 'https://mock-test.auth.ferentin.net';
const FERENTIN_AUTHORIZE = `${FERENTIN_ISSUER}/authorize`;
const FERENTIN_TOKEN = `${FERENTIN_ISSUER}/token`;
const SECRET = 'local-only-synthetic-secret-1234567890';
const originalFetch = globalThis.fetch;

afterEach(() => { globalThis.fetch = originalFetch; });

function json(body, status = 200, headers = {}) {
  return new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json', ...headers } });
}

function metadataResponse(request) {
  if (request.url === RESOURCE && !request.headers.has('authorization')) {
    return json({ error: 'unauthorized' }, 401, { 'www-authenticate': `Bearer resource_metadata="${OPRM}", scope="mcp:tools"` });
  }
  if (request.url === OPRM) {
    return json({ resource: RESOURCE, authorization_servers: [ISSUER], scopes_supported: ['mcp:tools'] });
  }
  if (request.url === `${ISSUER}/.well-known/oauth-authorization-server`) {
    return json({
      issuer: ISSUER,
      authorization_endpoint: AUTHORIZE,
      token_endpoint: TOKEN,
      code_challenge_methods_supported: ['S256'],
      token_endpoint_auth_methods_supported: ['private_key_jwt'],
      client_id_metadata_document_supported: true,
    });
  }
  return null;
}

function ferentinMetadataResponse(request) {
  if (request.url === FERENTIN_RESOURCE && !request.headers.has('authorization')) {
    return json({ error: 'unauthorized' }, 401, { 'www-authenticate': `Bearer resource_metadata="${FERENTIN_OPRM}", scope="openid profile mcp"` });
  }
  if (request.url === FERENTIN_OPRM) {
    return json({ resource: FERENTIN_RESOURCE, authorization_servers: [FERENTIN_ISSUER], scopes_supported: ['openid', 'profile', 'mcp'] });
  }
  if (request.url === `${FERENTIN_ISSUER}/.well-known/oauth-authorization-server`) {
    return json({
      issuer: FERENTIN_ISSUER,
      authorization_endpoint: FERENTIN_AUTHORIZE,
      token_endpoint: FERENTIN_TOKEN,
      code_challenge_methods_supported: ['S256'],
      token_endpoint_auth_methods_supported: ['private_key_jwt'],
      client_id_metadata_document_supported: true,
    });
  }
  return null;
}

function fakeDb({ failAt } = {}) {
  const rows = [];
  const sqlite = new DatabaseSync(':memory:');
  sqlite.exec(readFileSync(new URL('../migrations/0008_openid_aiim_descope_capture.sql', import.meta.url), 'utf8'));
  return {
    rows,
    prepare(sql) {
      assert.match(sql, /INSERT INTO openid_aiim_descope_capture/u);
      const statement = sqlite.prepare(sql);
      return {
        bind(...values) {
          return {
            async run() {
              if (failAt !== undefined && rows.length === failAt) throw new Error('D1 unavailable');
              statement.run(...values);
              rows.push(values);
              return { success: true };
            },
          };
        },
      };
    },
  };
}

test('Descope capture migration creates an append-only run and sequence table', () => {
  const sql = readFileSync(new URL('../migrations/0008_openid_aiim_descope_capture.sql', import.meta.url), 'utf8');
  const db = new DatabaseSync(':memory:');
  db.exec(sql);
  db.prepare('INSERT INTO openid_aiim_descope_capture (run_id, seq, at, record_json) VALUES (?, ?, ?, ?)').run('run-1', 0, '2026-10-02T00:00:00.000Z', '{"phase":"tokenless_mcp"}');
  assert.deepEqual({ ...db.prepare('SELECT run_id, seq, record_json FROM openid_aiim_descope_capture').get() }, { run_id: 'run-1', seq: 0, record_json: '{"phase":"tokenless_mcp"}' });
  assert.throws(() => db.prepare('INSERT INTO openid_aiim_descope_capture (run_id, seq, at, record_json) VALUES (?, ?, ?, ?)').run('run-1', 0, '2026-10-02T00:00:01.000Z', '{}'));
  db.close();
});

test('Sites build packages the Descope capture table for production D1', () => {
  const base = new URL('../dist/.openai/drizzle/', import.meta.url);
  const journal = JSON.parse(readFileSync(new URL('meta/_journal.json', base), 'utf8'));
  const db = new DatabaseSync(':memory:');
  for (const { tag } of journal.entries) {
    const sql = readFileSync(new URL(`${tag}.sql`, base), 'utf8');
    db.exec(sql.replaceAll('--> statement-breakpoint', ''));
  }
  const tables = db.prepare("SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'openid_aiim_descope_capture'").all();
  assert.deepEqual(tables.map(({ name }) => name), ['openid_aiim_descope_capture']);
  db.close();
});

test('recording fails before partner traffic when the first D1 write fails', async () => {
  let networkCalls = 0;
  globalThis.fetch = async () => { networkCalls += 1; throw new Error('Partner must not be contacted'); };
  const db = { prepare() { return { bind() { return { async run() { throw new Error('D1 unavailable'); } }; } }; } };
  const response = await handleOpenIdAiim(new Request('https://minorityprophet.org/openid-aiim/start?capture=1'), { MP_AIIM_STATE_SECRET: SECRET, DB: db });
  assert.equal(response.status, 502);
  assert.equal(networkCalls, 0);
});

test('reproduce page exposes the explicit recorded Descope run', async () => {
  const response = await handleOpenIdAiim(new Request('https://minorityprophet.org/openid-aiim/reproduce'));
  const html = await response.text();
  assert.match(html, /\/openid-aiim\/start/u);
  assert.match(html, /Start recorded Descope run/u);
  assert.doesNotMatch(html, /Run without recording/u);
});

test('reproduce page exposes a distinct recorded Ferentin run without a custom URL input', async () => {
  const response = await handleOpenIdAiim(new Request('https://minorityprophet.org/openid-aiim/reproduce'));
  const html = await response.text();
  assert.match(html, /href="\/openid-aiim\/partners\/ferentin\/start"/u);
  assert.match(html, /Start recorded Ferentin run/u);
  assert.doesNotMatch(html, /name="(?:url|resource|issuer)"/u);
});

test('every authorization run requires durable capture before partner traffic', async () => {
  let networkCalls = 0;
  globalThis.fetch = async () => { networkCalls += 1; throw new Error('Partner must not be contacted'); };
  const response = await handleOpenIdAiim(new Request('https://minorityprophet.org/openid-aiim/start'), { MP_AIIM_STATE_SECRET: SECRET });
  assert.equal(response.status, 503);
  assert.equal(networkCalls, 0);
});

test('recorded start captures the tokenless challenge, metadata, and PKCE redirect', async () => {
  const calls = [];
  globalThis.fetch = async (input, init = {}) => {
    const request = input instanceof Request ? input : new Request(input, init);
    calls.push(`${request.method} ${request.url}`);
    const response = metadataResponse(request);
    if (response) {
      response.headers.set('x-request-id', `request-${calls.length}`);
      response.headers.set('traceparent', `00-${'1'.repeat(32)}-${'2'.repeat(16)}-01`);
      return response;
    }
    throw new Error(`Unexpected network request: ${request.url}`);
  };
  const db = fakeDb();
  const response = await handleOpenIdAiim(new Request('https://minorityprophet.org/openid-aiim/start?capture=1'), { MP_AIIM_STATE_SECRET: SECRET, DB: db });
  assert.equal(response.status, 302);
  assert.deepEqual(calls, [`POST ${RESOURCE}`, `GET ${OPRM}`, `GET ${ISSUER}/.well-known/oauth-authorization-server`]);
  const authorizationUrl = new URL(response.headers.get('location'));
  assert.equal(authorizationUrl.searchParams.get('code_challenge_method'), 'S256');
  assert.ok(authorizationUrl.searchParams.get('code_challenge'));
  const records = db.rows.map(([, , , body]) => JSON.parse(body));
  assert.deepEqual(records.map(({ phase }) => phase), ['capture_start', 'tokenless_mcp', 'oprm', 'authorization_server_metadata', 'authorization_redirect']);
  assert.equal(records[1].response.status, 401);
  assert.match(records[1].started_at, /^\d{4}-\d{2}-\d{2}T/u);
  assert.match(records[1].completed_at, /^\d{4}-\d{2}-\d{2}T/u);
  assert.ok(Date.parse(records[1].completed_at) >= Date.parse(records[1].started_at));
  assert.deepEqual(records[1].correlation_ids, {
    'traceparent': `00-${'1'.repeat(32)}-${'2'.repeat(16)}-01`,
    'x-request-id': 'request-1',
  });
  assert.match(records[1].response.headers['www-authenticate'], /resource_metadata=/u);
  assert.equal(new URL(records[4].request.url).searchParams.get('code_challenge_method'), 'S256');
  assert.equal(new URL(records[4].request.url).searchParams.get('state'), '<redacted>');
});

test('one Descope run records token exchange and MCP calls while redacting every live credential', async () => {
  const { privateKey } = generateKeyPairSync('rsa', { modulusLength: 2048, privateKeyEncoding: { type: 'pkcs8', format: 'pem' }, publicKeyEncoding: { type: 'spki', format: 'pem' } });
  const db = fakeDb();
  globalThis.fetch = async (input, init = {}) => {
    const request = input instanceof Request ? input : new Request(input, init);
    const metadata = metadataResponse(request);
    if (metadata) return metadata;
    const body = await request.text();
    if (request.url === TOKEN) return json({ access_token: 'TEST_ACCESS_TOKEN', token_type: 'Bearer', scope: 'mcp:tools' });
    if (request.url === RESOURCE && request.headers.get('authorization') === 'Bearer TEST_ACCESS_TOKEN') {
      const method = JSON.parse(body).method;
      if (method === 'initialize') return new Response('event: message\ndata: {"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2026-07-28","capabilities":{}}}\n\n', { headers: { 'content-type': 'text/event-stream', 'Mcp-Session-Id': 'TEST_SESSION_ID' } });
      if (method === 'notifications/initialized') return new Response(null, { status: 202 });
      if (method === 'tools/list') return json({ jsonrpc: '2.0', id: 2, result: { tools: [{ name: 'example_tool', title: 'Example' }] } });
    }
    throw new Error(`Unexpected network request: ${request.url}`);
  };
  const env = { MP_AIIM_STATE_SECRET: SECRET, MP_AIIM_CLIENT_PRIVATE_KEY: privateKey, DB: db };
  const start = await handleOpenIdAiim(new Request('https://minorityprophet.org/openid-aiim/start?capture=1'), env);
  const state = new URL(start.headers.get('location')).searchParams.get('state');
  const cookie = start.headers.get('set-cookie').split(';')[0];
  const callback = await handleOpenIdAiim(new Request(`https://minorityprophet.org/openid-aiim/callback?code=TEST_AUTH_CODE&state=${state}&iss=${encodeURIComponent(ISSUER)}`, { headers: { cookie } }), env);
  assert.equal(callback.status, 200);
  const records = db.rows.map(([, , , body]) => JSON.parse(body));
  assert.equal(new Set(db.rows.map(([runId]) => runId)).size, 1);
  assert.deepEqual(db.rows.map(([, seq]) => seq), records.map((_, seq) => seq));
  assert.deepEqual(records.map(({ phase }) => phase), [
    'capture_start', 'tokenless_mcp', 'oprm', 'authorization_server_metadata', 'authorization_redirect',
    'authorization_callback', 'token_exchange', 'mcp_initialize', 'mcp_initialized_notification', 'tools_list',
    'capture_complete',
  ]);
  assert.deepEqual(records.at(-1), {
    schema: 'minority-prophet.openid-aiim-capture.v1',
    phase: 'capture_complete',
    at: records.at(-1).at,
    run_id: db.rows.at(-1)[0],
    evidence_record_count: 11,
    outcome: 'success',
    required_phases: [
      'capture_start', 'tokenless_mcp', 'oprm', 'authorization_server_metadata', 'authorization_redirect',
      'authorization_callback', 'token_exchange', 'mcp_initialize', 'mcp_initialized_notification', 'tools_list',
    ],
    tool_invocation_performed: false,
  });
  const token = records.find(({ phase }) => phase === 'token_exchange');
  const form = new URLSearchParams(token.request.body);
  assert.equal(form.get('code'), '<redacted>');
  assert.equal(form.get('code_verifier'), '<redacted>');
  assert.equal(form.get('client_assertion'), '<redacted>');
  assert.equal(form.get('client_assertion_type'), 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer');
  assert.deepEqual(token.assertion.header, { alg: 'RS256', kid: 'f35c5d1f-b07b-4525-9587-c0f21295a972' });
  assert.deepEqual({ iss: token.assertion.claims.iss, sub: token.assertion.claims.sub, aud: token.assertion.claims.aud }, { iss: 'https://minorityprophet.org/openid-aiim/client.json', sub: 'https://minorityprophet.org/openid-aiim/client.json', aud: TOKEN });
  assert.equal(typeof token.assertion.claims.exp, 'number');
  assert.equal(JSON.parse(token.response.body).access_token, '<redacted>');
  assert.equal(records.find(({ phase }) => phase === 'mcp_initialize').request.headers.authorization, '<redacted>');
  const persisted = JSON.stringify(records);
  for (const secret of ['TEST_AUTH_CODE', 'TEST_ACCESS_TOKEN', 'TEST_SESSION_ID', 'BEGIN PRIVATE KEY']) assert.equal(persisted.includes(secret), false);
});

test('a failed evidence write after token exchange aborts before any authenticated MCP request', async () => {
  const { privateKey } = generateKeyPairSync('rsa', { modulusLength: 2048, privateKeyEncoding: { type: 'pkcs8', format: 'pem' }, publicKeyEncoding: { type: 'spki', format: 'pem' } });
  const db = fakeDb({ failAt: 6 });
  let authenticatedMcpCalls = 0;
  globalThis.fetch = async (input, init = {}) => {
    const request = input instanceof Request ? input : new Request(input, init);
    const metadata = metadataResponse(request);
    if (metadata) return metadata;
    if (request.url === TOKEN) return json({ access_token: 'TEST_ACCESS_TOKEN', token_type: 'Bearer' });
    if (request.url === RESOURCE && request.headers.has('authorization')) authenticatedMcpCalls += 1;
    throw new Error(`Unexpected network request: ${request.url}`);
  };
  const env = { MP_AIIM_STATE_SECRET: SECRET, MP_AIIM_CLIENT_PRIVATE_KEY: privateKey, DB: db };
  const start = await handleOpenIdAiim(new Request('https://minorityprophet.org/openid-aiim/start?capture=1'), env);
  const state = new URL(start.headers.get('location')).searchParams.get('state');
  const cookie = start.headers.get('set-cookie').split(';')[0];
  const callback = await handleOpenIdAiim(new Request(`https://minorityprophet.org/openid-aiim/callback?code=TEST_AUTH_CODE&state=${state}`, { headers: { cookie } }), env);
  assert.equal(callback.status, 502);
  assert.equal(authenticatedMcpCalls, 0);
});

test('an OAuth error callback is durably captured instead of requiring a blind rerun', async () => {
  const { privateKey } = generateKeyPairSync('rsa', { modulusLength: 2048, privateKeyEncoding: { type: 'pkcs8', format: 'pem' }, publicKeyEncoding: { type: 'spki', format: 'pem' } });
  const db = fakeDb();
  globalThis.fetch = async (input, init = {}) => {
    const request = input instanceof Request ? input : new Request(input, init);
    const metadata = metadataResponse(request);
    if (metadata) return metadata;
    throw new Error(`Unexpected network request: ${request.url}`);
  };
  const env = { MP_AIIM_STATE_SECRET: SECRET, MP_AIIM_CLIENT_PRIVATE_KEY: privateKey, DB: db };
  const start = await handleOpenIdAiim(new Request('https://minorityprophet.org/openid-aiim/start'), env);
  const state = new URL(start.headers.get('location')).searchParams.get('state');
  const cookie = start.headers.get('set-cookie').split(';')[0];
  const callback = await handleOpenIdAiim(new Request(`https://minorityprophet.org/openid-aiim/callback?error=access_denied&error_description=operator_declined&state=${state}&iss=${encodeURIComponent(ISSUER)}`, { headers: { cookie } }), env);
  assert.equal(callback.status, 400);
  const records = db.rows.map(([, , , body]) => JSON.parse(body));
  assert.equal(records.at(-1).phase, 'authorization_callback');
  const callbackUrl = new URL(records.at(-1).request.url);
  assert.equal(callbackUrl.searchParams.get('error'), 'access_denied');
  assert.equal(callbackUrl.searchParams.get('state'), '<redacted>');
});

test('Ferentin start is a fixed captured profile discovered only through approved origins', async () => {
  const calls = [];
  globalThis.fetch = async (input, init = {}) => {
    const request = input instanceof Request ? input : new Request(input, init);
    calls.push(`${request.method} ${request.url}`);
    const response = ferentinMetadataResponse(request);
    if (response) return response;
    throw new Error(`Unexpected network request: ${request.url}`);
  };
  const db = fakeDb();
  const response = await handleOpenIdAiim(new Request('https://minorityprophet.org/openid-aiim/partners/ferentin/start'), { MP_AIIM_STATE_SECRET: SECRET, DB: db });
  assert.equal(response.status, 302);
  assert.deepEqual(calls, [
    `POST ${FERENTIN_RESOURCE}`,
    `GET ${FERENTIN_OPRM}`,
    `GET ${FERENTIN_ISSUER}/.well-known/oauth-authorization-server`,
  ]);
  const authorizationUrl = new URL(response.headers.get('location'));
  assert.equal(authorizationUrl.origin + authorizationUrl.pathname, FERENTIN_AUTHORIZE);
  assert.equal(authorizationUrl.searchParams.get('client_id'), 'https://minorityprophet.org/openid-aiim/client.json');
  assert.equal(authorizationUrl.searchParams.get('resource'), FERENTIN_RESOURCE);
  assert.equal(authorizationUrl.searchParams.get('scope'), 'openid profile mcp');
  const records = db.rows.map(([, , , body]) => JSON.parse(body));
  assert.deepEqual(records.map(({ phase }) => phase), ['capture_start', 'tokenless_mcp', 'oprm', 'authorization_server_metadata', 'authorization_redirect']);
  assert.equal(records[0].profile, 'ferentin');
  assert.equal(new URL(records[4].request.url).origin, 'https://mock-test.auth.ferentin.net');
});

test('Ferentin capture accepts a valid JSON challenge when the response omits its media type', async () => {
  globalThis.fetch = async (input, init = {}) => {
    const request = input instanceof Request ? input : new Request(input, init);
    if (request.url === FERENTIN_RESOURCE && !request.headers.has('authorization')) {
      const body = new TextEncoder().encode(JSON.stringify({ jsonrpc: '2.0', error: { code: -32001, message: 'Authentication required: Not Authenticated' } }));
      return new Response(body, { status: 401, headers: { 'www-authenticate': `Bearer resource_metadata="${FERENTIN_OPRM}", scope="openid profile mcp"` } });
    }
    const response = ferentinMetadataResponse(request);
    if (response) return response;
    throw new Error(`Unexpected network request: ${request.url}`);
  };
  const db = fakeDb();
  const response = await handleOpenIdAiim(new Request('https://minorityprophet.org/openid-aiim/partners/ferentin/start'), { MP_AIIM_STATE_SECRET: SECRET, DB: db });
  assert.equal(response.status, 302);
  const records = db.rows.map(([, , , body]) => JSON.parse(body));
  assert.deepEqual(records.map(({ phase }) => phase), ['capture_start', 'tokenless_mcp', 'oprm', 'authorization_server_metadata', 'authorization_redirect']);
  assert.deepEqual(JSON.parse(records[1].response.body), { jsonrpc: '2.0', error: { code: '<redacted>', message: 'Authentication required: Not Authenticated' } });
});

test('Ferentin callback uses the captured fixed profile and completes one redacted client run', async () => {
  const { privateKey } = generateKeyPairSync('rsa', { modulusLength: 2048, privateKeyEncoding: { type: 'pkcs8', format: 'pem' }, publicKeyEncoding: { type: 'spki', format: 'pem' } });
  const db = fakeDb();
  const calls = [];
  globalThis.fetch = async (input, init = {}) => {
    const request = input instanceof Request ? input : new Request(input, init);
    calls.push(`${request.method} ${request.url}`);
    const metadata = ferentinMetadataResponse(request);
    if (metadata) return metadata;
    const body = await request.text();
    if (request.url === FERENTIN_TOKEN) return json({ access_token: 'FERENTIN_ACCESS_TOKEN', token_type: 'Bearer', scope: 'openid profile mcp' });
    if (request.url === FERENTIN_RESOURCE && request.headers.get('authorization') === 'Bearer FERENTIN_ACCESS_TOKEN') {
      const method = JSON.parse(body).method;
      if (method === 'initialize') return json({ jsonrpc: '2.0', id: 1, result: { protocolVersion: '2026-07-28', capabilities: {} } }, 200, { 'Mcp-Session-Id': 'FERENTIN_SESSION' });
      if (method === 'notifications/initialized') return new Response(null, { status: 202 });
      if (method === 'tools/list') return json({ jsonrpc: '2.0', id: 2, result: { tools: [{ name: 'ferentin_docs', title: 'Ferentin Docs' }] } });
    }
    throw new Error(`Unexpected network request: ${request.url}`);
  };
  const env = { MP_AIIM_STATE_SECRET: SECRET, MP_AIIM_CLIENT_PRIVATE_KEY: privateKey, DB: db };
  const start = await handleOpenIdAiim(new Request('https://minorityprophet.org/openid-aiim/partners/ferentin/start'), env);
  const state = new URL(start.headers.get('location')).searchParams.get('state');
  const cookie = start.headers.get('set-cookie').split(';')[0];
  const callback = await handleOpenIdAiim(new Request(`https://minorityprophet.org/openid-aiim/callback?code=FERENTIN_AUTH_CODE&state=${state}&iss=${encodeURIComponent(FERENTIN_ISSUER)}`, { headers: { cookie } }), env);
  assert.equal(callback.status, 200);
  assert.ok(calls.includes(`POST ${FERENTIN_TOKEN}`));
  assert.equal(calls.filter((entry) => entry === `POST ${FERENTIN_RESOURCE}`).length, 4);
  const records = db.rows.map(([, , , body]) => JSON.parse(body));
  const token = records.find(({ phase }) => phase === 'token_exchange');
  assert.equal(token.assertion.claims.aud, FERENTIN_TOKEN);
  assert.equal(new URL(token.request.url).origin, 'https://mock-test.auth.ferentin.net');
  assert.equal(records.at(-1).phase, 'capture_complete');
  assert.equal(JSON.stringify(records).includes('FERENTIN_ACCESS_TOKEN'), false);
  const html = await callback.text();
  assert.match(html, /profile.*ferentin/us);
});

test('Ferentin discovery refuses an unapproved OPRM origin before fetching it', async () => {
  const calls = [];
  globalThis.fetch = async (input, init = {}) => {
    const request = input instanceof Request ? input : new Request(input, init);
    calls.push(`${request.method} ${request.url}`);
    if (request.url === FERENTIN_RESOURCE) {
      return json({ error: 'unauthorized' }, 401, { 'www-authenticate': 'Bearer resource_metadata="https://attacker.invalid/oprm"' });
    }
    return json({ resource: FERENTIN_RESOURCE, authorization_servers: [FERENTIN_ISSUER], scopes_supported: ['mcp:tools'] });
  };
  const response = await handleOpenIdAiim(new Request('https://minorityprophet.org/openid-aiim/partners/ferentin/start'), { MP_AIIM_STATE_SECRET: SECRET, DB: fakeDb() });
  assert.equal(response.status, 502);
  assert.deepEqual(calls, [`POST ${FERENTIN_RESOURCE}`]);
});
