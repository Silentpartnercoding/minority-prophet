const RESOURCE = "https://mp-interop-referee.tradearmory.workers.dev/mcp";
const RESOURCE_METADATA = "https://mp-interop-referee.tradearmory.workers.dev/.well-known/oauth-protected-resource/mcp";
const EXPECTED_ISSUER = "https://api.descope.com/v1/apps/agentic/P3IEQH7e0pGsj5aPR5PQPZQI6pfA/RS3IQSxDIjEhYYhuVkuey7uly21NB";
const AUTHORIZATION_ENDPOINT = "https://api.descope.com/oauth2/v1/apps/agentic/P3IEQH7e0pGsj5aPR5PQPZQI6pfA/RS3IQSxDIjEhYYhuVkuey7uly21NB/authorize";
const TOKEN_ENDPOINT = "https://api.descope.com/oauth2/v1/apps/agentic/P3IEQH7e0pGsj5aPR5PQPZQI6pfA/RS3IQSxDIjEhYYhuVkuey7uly21NB/token";
const CLIENT_ID = "https://minorityprophet.org/openid-aiim/client.json";
const JWKS_URI = "https://minorityprophet.org/openid-aiim/jwks.json";
const CLIENT_KEY_ID = "f35c5d1f-b07b-4525-9587-c0f21295a972";
const REDIRECT_URI = "https://minorityprophet.org/openid-aiim/callback";
const REQUESTED_SCOPE = "mcp:tools";
const COOKIE_NAME = "mp_aiim_oauth";
const MCP_VERSION = "2026-07-28";
const SUPPORTED_MCP_VERSIONS = new Set(["2026-07-28", "2025-11-25", "2025-06-18"]);
const FLOW_TTL_MS = 10 * 60 * 1000;

interface AiimEnv {
  MP_AIIM_STATE_SECRET?: string;
  MP_AIIM_CLIENT_PRIVATE_KEY?: string;
  DB?: D1Database;
}

function stateSecret(env?: AiimEnv): string | undefined {
  return env?.MP_AIIM_STATE_SECRET ?? process.env.MP_AIIM_STATE_SECRET;
}

function clientPrivateKey(env?: AiimEnv): string | undefined {
  return env?.MP_AIIM_CLIENT_PRIVATE_KEY ?? process.env.MP_AIIM_CLIENT_PRIVATE_KEY;
}

const CLIENT_PUBLIC_JWK = {
  kty: "RSA",
  n: "0zEN2inprOGQFnM6TJnhDNUj0T1tXcbC7h6n-ZbAw5Vu3xDk9bjZt00GIfeYVCwYPpPVP7beCvErx8Wf_rgKc0WhGkoW0PbfTJjD2FNx3tS6BicZps_qkyu7T3q82o75q3YhZCeTbR06-_MSfMpuhrOxy4Romdn5UdWRL5GbIRddlOKQ7B7jZOJpZNTq1u6VlhDPiKkmTkg2GxdUkY4B88tJ8jd4vUyjJvuEsd7EAk29kIJBtLP3bqGT043yvGQD86PqvZFsUkzoMbRtP3t0KeoGWd2XDmv29662OQu32qcBa7FNmmxS0x4ouaoq7CHIgGdJDJLMiLLbp7s6IWNmhQ",
  e: "AQAB",
  use: "sig",
  alg: "RS256",
  kid: CLIENT_KEY_ID,
};

interface FlowState {
  state: string;
  verifier: string;
  issuedAt: number;
  issuer: string;
  captureRunId?: string;
  captureNextSeq?: number;
}

interface CaptureContext {
  db: D1Database;
  runId: string;
  nextSeq: number;
}

interface CaptureRecord {
  phase: string;
  at: string;
  [key: string]: unknown;
}

interface OAuthMetadata {
  issuer?: string;
  authorization_endpoint?: string;
  token_endpoint?: string;
  code_challenge_methods_supported?: string[];
  token_endpoint_auth_methods_supported?: string[];
  client_id_metadata_document_supported?: boolean;
  scopes_supported?: string[];
}

interface ProtectedResourceMetadata {
  resource?: string;
  authorization_servers?: string[];
  scopes_supported?: string[];
}

interface McpEnvelope {
  result?: Record<string, unknown>;
  error?: unknown;
}

const jsonHeaders = {
  "cache-control": "public, max-age=300",
  "content-type": "application/json; charset=utf-8",
  "x-content-type-options": "nosniff",
};

function b64url(bytes: Uint8Array): string {
  let binary = "";
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary).replaceAll("+", "-").replaceAll("/", "_").replace(/=+$/u, "");
}

function decodeB64url(value: string): Uint8Array {
  const padded = value.replaceAll("-", "+").replaceAll("_", "/").padEnd(Math.ceil(value.length / 4) * 4, "=");
  const binary = atob(padded);
  return Uint8Array.from(binary, (character) => character.charCodeAt(0));
}

function arrayBuffer(bytes: Uint8Array): ArrayBuffer {
  const copy = new Uint8Array(bytes.byteLength);
  copy.set(bytes);
  return copy.buffer;
}

function randomValue(byteLength = 32): string {
  return b64url(crypto.getRandomValues(new Uint8Array(byteLength)));
}

async function sha256(value: string): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(value));
  return b64url(new Uint8Array(digest));
}

function pemBody(pem: string): ArrayBuffer {
  const base64 = pem.replace(/-----BEGIN PRIVATE KEY-----|-----END PRIVATE KEY-----|\s/gu, "");
  const binary = atob(base64);
  return arrayBuffer(Uint8Array.from(binary, (character) => character.charCodeAt(0)));
}

async function privateKey(pem: string): Promise<CryptoKey> {
  return crypto.subtle.importKey(
    "pkcs8",
    pemBody(pem),
    { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" },
    false,
    ["sign"],
  );
}

async function clientAssertion(pem: string): Promise<string> {
  const issuedAt = Math.floor(Date.now() / 1000);
  const header = b64url(new TextEncoder().encode(JSON.stringify({ alg: "RS256", kid: CLIENT_KEY_ID, typ: "JWT" })));
  const payload = b64url(new TextEncoder().encode(JSON.stringify({
    iss: CLIENT_ID,
    sub: CLIENT_ID,
    aud: TOKEN_ENDPOINT,
    iat: issuedAt,
    exp: issuedAt + 300,
    jti: crypto.randomUUID(),
  })));
  const signingInput = `${header}.${payload}`;
  const signature = await crypto.subtle.sign("RSASSA-PKCS1-v1_5", await privateKey(pem), new TextEncoder().encode(signingInput));
  return `${signingInput}.${b64url(new Uint8Array(signature))}`;
}

async function signingKey(secret: string): Promise<CryptoKey> {
  return crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign", "verify"],
  );
}

async function encodeFlow(flow: FlowState, secret: string): Promise<string> {
  const payload = b64url(new TextEncoder().encode(JSON.stringify(flow)));
  const signature = await crypto.subtle.sign("HMAC", await signingKey(secret), new TextEncoder().encode(payload));
  return `${payload}.${b64url(new Uint8Array(signature))}`;
}

async function decodeFlow(value: string, secret: string): Promise<FlowState | null> {
  const [payload, signature, extra] = value.split(".");
  if (!payload || !signature || extra) return null;
  const valid = await crypto.subtle.verify(
    "HMAC",
    await signingKey(secret),
    arrayBuffer(decodeB64url(signature)),
    new TextEncoder().encode(payload),
  );
  if (!valid) return null;
  try {
    const parsed = JSON.parse(new TextDecoder().decode(decodeB64url(payload))) as FlowState;
    if (!parsed.state || !parsed.verifier || !Number.isFinite(parsed.issuedAt) || !parsed.issuer) return null;
    return parsed;
  } catch {
    return null;
  }
}

function readCookie(request: Request, name: string): string | null {
  const cookie = request.headers.get("cookie") ?? "";
  for (const part of cookie.split(";")) {
    const separator = part.indexOf("=");
    if (separator < 0) continue;
    if (part.slice(0, separator).trim() === name) return part.slice(separator + 1).trim();
  }
  return null;
}

function flowCookie(value: string): string {
  return `${COOKIE_NAME}=${value}; Path=/openid-aiim; Max-Age=600; HttpOnly; Secure; SameSite=Lax`;
}

function clearFlowCookie(): string {
  return `${COOKIE_NAME}=; Path=/openid-aiim; Max-Age=0; HttpOnly; Secure; SameSite=Lax`;
}

function escapeHtml(value: string): string {
  return value.replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");
}

function page(title: string, content: string, status = 200, headers: HeadersInit = {}): Response {
  return new Response(`<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>${escapeHtml(title)} — Minority Prophet</title>
<style>
:root{color-scheme:light;--ink:#111510;--paper:#f1f0e8;--acid:#d8ff42;--orange:#ff6534;--muted:#66695f;--line:#cbcbbf}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font-family:Arial,sans-serif}.shell{max-width:960px;margin:0 auto;padding:56px 24px 96px}.kicker{font:700 11px/1.4 monospace;letter-spacing:.14em;text-transform:uppercase;color:var(--orange)}h1{max-width:820px;margin:18px 0 24px;font:400 clamp(45px,7vw,78px)/.95 Georgia,serif;letter-spacing:-.045em}.lede{max-width:760px;color:#4f534a;font:18px/1.55 Georgia,serif}.card{margin-top:28px;padding:24px;border:1px solid var(--ink);background:#fff}.card.dark{background:var(--ink);color:#fff}.label{font:700 10px monospace;text-transform:uppercase;letter-spacing:.1em;color:var(--muted)}.dark .label{color:var(--acid)}dl{display:grid;grid-template-columns:190px 1fr;margin:18px 0 0}dt,dd{margin:0;padding:10px 0;border-top:1px solid var(--line);font:12px/1.5 monospace;overflow-wrap:anywhere}dt{color:var(--muted)}button,.button{display:inline-block;margin-top:22px;padding:16px 20px;border:0;background:var(--ink);color:#fff;font:700 11px monospace;text-transform:uppercase;letter-spacing:.08em;cursor:pointer}.button.secondary{background:transparent;color:var(--ink);border:1px solid var(--ink);margin-left:8px}pre{overflow:auto;white-space:pre-wrap;overflow-wrap:anywhere;margin:16px 0 0;padding:18px;background:#171b15;color:#e8eadf;font:12px/1.6 monospace}.boundary{margin-top:22px;color:var(--muted);font:11px/1.55 monospace}a{text-decoration:none;color:inherit}@media(max-width:620px){dl{grid-template-columns:1fr}dt{padding-bottom:2px}dd{padding-top:2px;border-top:0}.button.secondary{margin-left:0}}
</style></head><body><main class="shell">${content}</main></body></html>`, {
    status,
    headers: {
      "cache-control": "no-store",
      "content-security-policy": "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'",
      "content-type": "text/html; charset=utf-8",
      "referrer-policy": "no-referrer",
      "x-content-type-options": "nosniff",
      "x-frame-options": "DENY",
      "x-robots-tag": "noindex, nofollow",
      ...headers,
    },
  });
}

function reportPage(title: string, report: Record<string, unknown>, status = 200): Response {
  return page(title, `<p class="kicker">OpenID AIIM · exploratory interoperability lane</p><h1>${escapeHtml(title)}</h1>
<p class="lede">This is a bounded diagnostic record. It is not a canonical Minority Prophet research result and it does not claim authorization or safety.</p>
<section class="card dark"><p class="label">Redacted run report</p><pre>${escapeHtml(JSON.stringify(report, null, 2))}</pre></section>
<p class="boundary">No access token, authorization code, PKCE verifier, cookie value, or Descope tool output is displayed or retained. No tool was invoked.</p>
<a class="button secondary" href="/openid-aiim/reproduce">Back to reproduction page</a>`, status, { "set-cookie": clearFlowCookie() });
}

const REDACTED = "<redacted>";
const SECRET_FIELDS = new Set(["access_token", "refresh_token", "id_token", "code", "code_verifier", "client_assertion", "client_secret", "state", "password"]);
const SECRET_HEADERS = new Set(["authorization", "proxy-authorization", "cookie", "set-cookie", "mcp-session-id"]);
const MAX_CAPTURE_BODY_BYTES = 64 * 1024;

function redactUrl(value: string): string {
  const url = new URL(value);
  for (const key of url.searchParams.keys()) if (SECRET_FIELDS.has(key.toLowerCase())) url.searchParams.set(key, REDACTED);
  return url.toString();
}

function redactHeaders(headers: Headers): Record<string, string> {
  const result: Record<string, string> = {};
  for (const [key, value] of headers) {
    result[key] = SECRET_HEADERS.has(key.toLowerCase()) ? REDACTED : key.toLowerCase() === "location" ? redactUrl(value) : value;
  }
  return result;
}

function redactJson(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(redactJson);
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, SECRET_FIELDS.has(key.toLowerCase()) ? REDACTED : redactJson(item)]));
  }
  return value;
}

async function boundedText(body: ReadableStream<Uint8Array> | null): Promise<string> {
  const reader = body?.getReader();
  if (!reader) return "";
  const chunks: Uint8Array[] = [];
  let size = 0;
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      size += value.byteLength;
      if (size > MAX_CAPTURE_BODY_BYTES) throw new Error("Descope capture body exceeded 64 KiB; run aborted before retaining an incomplete trace");
      chunks.push(value);
    }
  } finally {
    reader.releaseLock();
  }
  const bytes = new Uint8Array(size);
  let offset = 0;
  for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.byteLength; }
  return new TextDecoder().decode(bytes);
}

function redactBody(body: string, contentType: string | null): string {
  if (!body) return body;
  if (contentType?.includes("application/x-www-form-urlencoded")) {
    const params = new URLSearchParams(body);
    for (const key of params.keys()) if (SECRET_FIELDS.has(key.toLowerCase())) params.set(key, REDACTED);
    return params.toString();
  }
  if (contentType?.includes("json")) return JSON.stringify(redactJson(JSON.parse(body)));
  if (contentType?.includes("text/event-stream")) {
    return body.split(/(\r?\n)/u).map((part) => {
      if (!part.startsWith("data:")) return part;
      const payload = part.slice(5).trim();
      return payload === "[DONE]" ? part : `data: ${JSON.stringify(redactJson(JSON.parse(payload)))}`;
    }).join("");
  }
  throw new Error("Descope capture refused an unrecognized body format");
}

async function saveCapture(trace: CaptureContext, record: CaptureRecord): Promise<void> {
  const result = await trace.db.prepare("INSERT INTO openid_aiim_descope_capture (run_id, seq, at, record_json) VALUES (?, ?, ?, ?)")
    .bind(trace.runId, trace.nextSeq++, record.at, JSON.stringify(record)).run();
  if (!result.success) throw new Error("Descope capture storage did not confirm the evidence write");
}

async function captureExchange(
  trace: CaptureContext,
  phase: string,
  request: Pick<Request, "url" | "method" | "headers" | "body">,
  response: Response | null,
  extra?: Record<string, unknown>,
): Promise<void> {
  const requestBody = redactBody(await boundedText(request.body), request.headers.get("content-type"));
  const responseBody = response ? redactBody(await boundedText(response.clone().body), response.headers.get("content-type")) : null;
  await saveCapture(trace, {
    phase,
    at: new Date().toISOString(),
    request: { method: request.method, url: redactUrl(request.url), headers: redactHeaders(request.headers), body: requestBody },
    response: response ? { status: response.status, headers: redactHeaders(response.headers), body: responseBody } : null,
    ...extra,
  });
}

async function capturedFetch(url: string, init: RequestInit, trace: CaptureContext | undefined, phase: string, extra?: Record<string, unknown>): Promise<Response> {
  const request = new Request(url, init);
  const captureRequest = trace ? request.clone() : undefined;
  const response = await fetch(request);
  if (trace && captureRequest) await captureExchange(trace, phase, captureRequest, response, extra);
  return response;
}

async function fetchJson<T>(url: string, trace?: CaptureContext, phase = "metadata"): Promise<{ response: Response; data: T }> {
  const response = await capturedFetch(url, {
    headers: { accept: "application/json" },
    redirect: "manual",
    signal: AbortSignal.timeout(10_000),
  }, trace, phase);
  if (response.status >= 300 && response.status < 400) throw new Error(`${url} attempted to redirect`);
  if (!response.ok) throw new Error(`${url} returned HTTP ${response.status}`);
  return { response, data: await response.json() as T };
}

async function validateDiscovery(trace?: CaptureContext): Promise<{
  protectedResource: ProtectedResourceMetadata;
  authorizationServer: OAuthMetadata;
}> {
  if (trace) {
    const challenge = await capturedFetch(RESOURCE, {
      method: "POST",
      headers: { accept: "application/json, text/event-stream", "content-type": "application/json" },
      body: JSON.stringify({ jsonrpc: "2.0", id: 0, method: "initialize", params: { protocolVersion: MCP_VERSION, capabilities: {}, clientInfo: { name: "minority-prophet-openid-aiim", version: "1.0.0" } } }),
      redirect: "manual",
      signal: AbortSignal.timeout(15_000),
    }, trace, "tokenless_mcp");
    const challengeHeader = challenge.headers.get("www-authenticate") ?? "";
    const metadataUrl = /resource_metadata="([^"]+)"/u.exec(challengeHeader)?.[1];
    if (challenge.status !== 401 || metadataUrl !== RESOURCE_METADATA) throw new Error("Tokenless MCP challenge did not advertise the expected OPRM URL");
  }
  const { data: protectedResource } = await fetchJson<ProtectedResourceMetadata>(RESOURCE_METADATA, trace, "oprm");
  if (protectedResource.resource !== RESOURCE) throw new Error("Protected resource identifier does not match the MCP endpoint");
  if (!protectedResource.authorization_servers?.includes(EXPECTED_ISSUER)) throw new Error("Expected authorization server is not advertised");
  if (!protectedResource.scopes_supported?.includes(REQUESTED_SCOPE)) throw new Error("The read-only scope is not advertised");

  const { data: authorizationServer } = await fetchJson<OAuthMetadata>(`${EXPECTED_ISSUER}/.well-known/oauth-authorization-server`, trace, "authorization_server_metadata");
  if (authorizationServer.issuer !== EXPECTED_ISSUER) throw new Error("Authorization-server issuer mismatch");
  if (authorizationServer.authorization_endpoint !== AUTHORIZATION_ENDPOINT) throw new Error("Unexpected authorization endpoint");
  if (authorizationServer.token_endpoint !== TOKEN_ENDPOINT) throw new Error("Unexpected token endpoint");
  if (authorizationServer.client_id_metadata_document_supported !== true) throw new Error("Authorization server does not advertise CIMD");
  if (!authorizationServer.code_challenge_methods_supported?.includes("S256")) throw new Error("Authorization server does not advertise PKCE S256");
  if (!authorizationServer.token_endpoint_auth_methods_supported?.includes("private_key_jwt")) throw new Error("Authorization server does not advertise private_key_jwt");
  return { protectedResource, authorizationServer };
}

function clientMetadata(): Record<string, unknown> {
  return {
    client_id: CLIENT_ID,
    client_name: "Minority Prophet OpenID AIIM Test Client",
    client_uri: "https://minorityprophet.org",
    redirect_uris: [REDIRECT_URI],
    grant_types: ["authorization_code"],
    response_types: ["code"],
    token_endpoint_auth_method: "private_key_jwt",
    token_endpoint_auth_signing_alg: "RS256",
    jwks_uri: JWKS_URI,
  };
}

function reproducePage(): Response {
  return page("Reproduce the Descope CIMD test", `<p class="kicker">OpenID AIIM · read-only test surface</p>
<h1>One stable client. One exact rerun.</h1>
<p class="lede">This page runs a standards-shaped confidential-client authorization attempt against the Minority Prophet MCP server protected by Descope. It requests only <code>${REQUESTED_SCOPE}</code>. If authorization succeeds, it proves the client's identity with <code>private_key_jwt</code>, initializes MCP, and lists tool names; it never calls a tool.</p>
<section class="card"><p class="label">Fixed inputs</p><dl>
<dt>MCP resource</dt><dd>${RESOURCE}</dd><dt>Client ID / metadata</dt><dd><a href="${CLIENT_ID}">${CLIENT_ID}</a></dd>
<dt>Public JWKS</dt><dd><a href="${JWKS_URI}">${JWKS_URI}</a></dd><dt>Callback</dt><dd>${REDIRECT_URI}</dd>
<dt>OAuth shape</dt><dd>Authorization Code + PKCE S256 · confidential client · private_key_jwt (RS256)</dd>
<dt>Requested scope</dt><dd>${REQUESTED_SCOPE}</dd><dt>MCP action ceiling</dt><dd>initialize → notifications/initialized → tools/list only</dd>
</dl><a class="button" href="/openid-aiim/start?capture=1">Record Descope run →</a>
<a class="button secondary" href="/openid-aiim/start">Run without recording</a>
<a class="button secondary" href="/openid-aiim/diagnostics.json">View live discovery checks</a></section>
<p class="boundary">Recorded runs use private durable storage and stop if any evidence write fails. The private signing key remains a hosted secret; only the matching public key is published. The fixed client ID above lets the Descope operator find the matching validator request. Boundary: this is an exploratory interoperability probe, not a canonical result. Successful listing shows tool names and titles only, and no MCP tool call is permitted by this harness.</p>`);
}

async function diagnostics(): Promise<Response> {
  const checkedAt = new Date().toISOString();
  try {
    const { protectedResource, authorizationServer } = await validateDiscovery();
    return Response.json({
      schema: "minority-prophet.openid-aiim-diagnostics.v1",
      lane: "exploratory-interoperability",
      checked_at: checkedAt,
      checks: {
        protected_resource_reachable: true,
        resource_exact_match: protectedResource.resource === RESOURCE,
        expected_issuer_advertised: protectedResource.authorization_servers?.includes(EXPECTED_ISSUER) === true,
        read_scope_advertised: protectedResource.scopes_supported?.includes(REQUESTED_SCOPE) === true,
        authorization_server_reachable: true,
        issuer_exact_match: authorizationServer.issuer === EXPECTED_ISSUER,
        cimd_advertised: authorizationServer.client_id_metadata_document_supported === true,
        pkce_s256_advertised: authorizationServer.code_challenge_methods_supported?.includes("S256") === true,
        private_key_jwt_advertised: authorizationServer.token_endpoint_auth_methods_supported?.includes("private_key_jwt") === true,
        public_jwks_configured: true,
      },
      fixed_inputs: { resource: RESOURCE, client_id: CLIENT_ID, jwks_uri: JWKS_URI, redirect_uri: REDIRECT_URI, scope: REQUESTED_SCOPE },
      authority_granted: false,
      tool_invocation_performed: false,
    }, { headers: { ...jsonHeaders, "cache-control": "no-store", "x-robots-tag": "noindex, nofollow" } });
  } catch (error) {
    return Response.json({
      schema: "minority-prophet.openid-aiim-diagnostics.v1",
      lane: "exploratory-interoperability",
      checked_at: checkedAt,
      ok: false,
      error: error instanceof Error ? error.message : "Discovery validation failed",
      authority_granted: false,
      tool_invocation_performed: false,
    }, { status: 502, headers: { ...jsonHeaders, "cache-control": "no-store", "x-robots-tag": "noindex, nofollow" } });
  }
}

async function startAuthorization(request: Request, env?: AiimEnv): Promise<Response> {
  const secret = stateSecret(env);
  if (!secret || secret.length < 32) {
    return reportPage("Test surface is not configured", { step: "local_configuration", ok: false, error: "State-signing secret is unavailable" }, 503);
  }
  const capture = new URL(request.url).searchParams.get("capture") === "1";
  if (capture && !env?.DB) {
    return reportPage("Descope capture is not configured", { step: "local_configuration", ok: false, error: "Durable capture binding is unavailable" }, 503);
  }
  if (capture && readCookie(request, COOKIE_NAME)) {
    return reportPage("Descope cold start rejected", { step: "cold_start", ok: false, error: "An earlier Descope flow cookie is present" }, 409);
  }
  const trace: CaptureContext | undefined = capture && env?.DB ? { db: env.DB, runId: crypto.randomUUID(), nextSeq: 0 } : undefined;
  try {
    if (trace) await saveCapture(trace, { phase: "capture_start", at: new Date().toISOString(), cold_start: { flow_cookie_present: false, token_cache: "none", metadata_cache: "none" } });
    await validateDiscovery(trace);
    const verifier = randomValue(48);
    const state = randomValue(32);
    const authorizationUrl = new URL(AUTHORIZATION_ENDPOINT);
    authorizationUrl.search = new URLSearchParams({
      response_type: "code",
      client_id: CLIENT_ID,
      redirect_uri: REDIRECT_URI,
      scope: REQUESTED_SCOPE,
      state,
      code_challenge: await sha256(verifier),
      code_challenge_method: "S256",
      resource: RESOURCE,
    }).toString();
    if (trace) await captureExchange(trace, "authorization_redirect", new Request(authorizationUrl), null);
    const cookie = await encodeFlow({ state, verifier, issuedAt: Date.now(), issuer: EXPECTED_ISSUER, captureRunId: trace?.runId, captureNextSeq: trace?.nextSeq }, secret);
    return new Response(null, {
      status: 302,
      headers: {
        "cache-control": "no-store",
        location: authorizationUrl.toString(),
        "referrer-policy": "no-referrer",
        "set-cookie": flowCookie(cookie),
        "x-robots-tag": "noindex, nofollow",
      },
    });
  } catch (error) {
    return reportPage("Discovery preflight failed", {
      step: "discovery_preflight",
      ok: false,
      error: error instanceof Error ? error.message : "Discovery preflight failed",
      token_issued: false,
      tool_invocation_performed: false,
    }, 502);
  }
}

async function parseMcpEnvelope(response: Response): Promise<McpEnvelope> {
  const body = await response.text();
  if (!body) return {};
  const contentType = response.headers.get("content-type") ?? "";
  if (contentType.includes("text/event-stream")) {
    const data = body.split(/\r?\n/u).filter((line) => line.startsWith("data:"))
      .map((line) => line.slice(5).trim()).filter(Boolean).at(-1);
    if (!data) throw new Error("MCP event stream contained no JSON data event");
    return JSON.parse(data) as McpEnvelope;
  }
  return JSON.parse(body) as McpEnvelope;
}

async function mcpPost(
  accessToken: string,
  body: Record<string, unknown>,
  sessionId?: string,
  protocolVersion?: string,
  trace?: CaptureContext,
  phase = "mcp",
): Promise<Response> {
  const headers: Record<string, string> = {
    accept: "application/json, text/event-stream",
    authorization: `Bearer ${accessToken}`,
    "content-type": "application/json",
  };
  if (sessionId) headers["Mcp-Session-Id"] = sessionId;
  if (protocolVersion) headers["MCP-Protocol-Version"] = protocolVersion;
  const response = await capturedFetch(RESOURCE, { method: "POST", headers, body: JSON.stringify(body), redirect: "manual", signal: AbortSignal.timeout(15_000) }, trace, phase);
  if (response.status >= 300 && response.status < 400) throw new Error("MCP endpoint attempted to redirect a bearer-token request");
  return response;
}

async function callback(request: Request, env?: AiimEnv): Promise<Response> {
  const provisionalRunId = crypto.randomUUID();
  const completedAt = new Date().toISOString();
  const secret = stateSecret(env);
  if (!secret || secret.length < 32) {
    return reportPage("Callback rejected", { run_id: provisionalRunId, completed_at: completedAt, step: "local_configuration", ok: false, error: "State-signing secret is unavailable" }, 503);
  }
  const url = new URL(request.url);
  const encodedFlow = readCookie(request, COOKIE_NAME);
  const flow = encodedFlow ? await decodeFlow(encodedFlow, secret) : null;
  if (!flow || Date.now() - flow.issuedAt > FLOW_TTL_MS || Date.now() < flow.issuedAt - 30_000) {
    return reportPage("Callback rejected", { run_id: provisionalRunId, completed_at: completedAt, step: "state_validation", ok: false, error: "Missing, invalid, or expired signed flow state" }, 400);
  }
  const runId = flow.captureRunId ?? provisionalRunId;
  if (flow.captureRunId && (!env?.DB || !Number.isInteger(flow.captureNextSeq))) {
    return reportPage("Descope capture is not configured", { run_id: runId, completed_at: completedAt, step: "local_configuration", ok: false, error: "Durable capture binding or sequence is unavailable" }, 503);
  }
  const trace: CaptureContext | undefined = flow.captureRunId && env?.DB ? { db: env.DB, runId, nextSeq: flow.captureNextSeq! } : undefined;
  const signingPem = clientPrivateKey(env);
  if (!signingPem?.includes("-----BEGIN PRIVATE KEY-----")) {
    return reportPage("Callback rejected", { run_id: runId, completed_at: completedAt, step: "local_configuration", ok: false, error: "Client signing key is unavailable" }, 503);
  }
  if (url.searchParams.get("state") !== flow.state) {
    return reportPage("Callback rejected", { run_id: runId, completed_at: completedAt, step: "state_validation", ok: false, error: "OAuth state mismatch" }, 400);
  }
  if (flow.issuer !== EXPECTED_ISSUER) {
    return reportPage("Callback rejected", { run_id: runId, completed_at: completedAt, step: "issuer_validation", ok: false, error: "Recorded issuer mismatch" }, 400);
  }
  const responseIssuer = url.searchParams.get("iss");
  if (responseIssuer && responseIssuer !== flow.issuer) {
    return reportPage("Callback rejected", { run_id: runId, completed_at: completedAt, step: "issuer_validation", ok: false, error: "Authorization response issuer mismatch" }, 400);
  }
  const authorizationError = url.searchParams.get("error");
  if (authorizationError) {
    return reportPage("Authorization server returned an error", {
      run_id: runId,
      completed_at: completedAt,
      step: "authorization",
      ok: false,
      oauth_error: authorizationError,
      oauth_error_description: url.searchParams.get("error_description"),
      response_issuer: responseIssuer ?? "not_returned",
      token_issued: false,
      tool_invocation_performed: false,
    }, 400);
  }
  const code = url.searchParams.get("code");
  if (!code) {
    return reportPage("Callback rejected", { run_id: runId, completed_at: completedAt, step: "authorization", ok: false, error: "No authorization code or OAuth error was returned" }, 400);
  }

  try {
    if (trace) await captureExchange(trace, "authorization_callback", request, null);
    const assertion = await clientAssertion(signingPem);
    const [assertionHeader, assertionClaims] = assertion.split(".");
    const decodedHeader = JSON.parse(new TextDecoder().decode(decodeB64url(assertionHeader))) as Record<string, unknown>;
    const decodedClaims = JSON.parse(new TextDecoder().decode(decodeB64url(assertionClaims))) as Record<string, unknown>;
    const assertionEvidence = {
      assertion: {
        header: { alg: decodedHeader.alg, kid: decodedHeader.kid },
        claims: { iss: decodedClaims.iss, sub: decodedClaims.sub, aud: decodedClaims.aud, exp: decodedClaims.exp },
      },
    };
    const tokenResponse = await capturedFetch(TOKEN_ENDPOINT, {
      method: "POST",
      headers: { accept: "application/json", "content-type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        grant_type: "authorization_code",
        code,
        client_id: CLIENT_ID,
        redirect_uri: REDIRECT_URI,
        code_verifier: flow.verifier,
        resource: RESOURCE,
        client_assertion_type: "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
        client_assertion: assertion,
      }),
      redirect: "manual",
      signal: AbortSignal.timeout(15_000),
    }, trace, "token_exchange", assertionEvidence);
    if (tokenResponse.status >= 300 && tokenResponse.status < 400) throw new Error("Token endpoint attempted to redirect the authorization-code exchange");
    const tokenBody = await tokenResponse.json() as Record<string, unknown>;
    if (!tokenResponse.ok || typeof tokenBody.access_token !== "string") {
      return reportPage("Token exchange failed", {
        run_id: runId,
        completed_at: completedAt,
        step: "token_exchange",
        ok: false,
        http_status: tokenResponse.status,
        oauth_error: tokenBody.error ?? "missing_access_token",
        oauth_error_description: tokenBody.error_description ?? null,
        response_issuer: responseIssuer ?? "not_returned",
        token_issued: false,
        tool_invocation_performed: false,
      }, 502);
    }
    const accessToken = tokenBody.access_token;
    const initializeResponse = await mcpPost(accessToken, {
      jsonrpc: "2.0",
      id: 1,
      method: "initialize",
      params: {
        protocolVersion: MCP_VERSION,
        capabilities: {},
        clientInfo: { name: "minority-prophet-openid-aiim", title: "Minority Prophet OpenID AIIM Test Client", version: "1.0.0" },
      },
    }, undefined, undefined, trace, "mcp_initialize");
    const initializeBody = await parseMcpEnvelope(initializeResponse);
    if (!initializeResponse.ok || initializeBody.error || !initializeBody.result) {
      return reportPage("MCP initialization failed", {
        run_id: runId,
        completed_at: completedAt,
        step: "mcp_initialize",
        ok: false,
        http_status: initializeResponse.status,
        json_rpc_error: initializeBody.error ?? null,
        token_issued: true,
        token_retained: false,
        tool_invocation_performed: false,
      }, 502);
    }
    const sessionId = initializeResponse.headers.get("Mcp-Session-Id") ?? undefined;
    const negotiatedVersion = typeof initializeBody.result.protocolVersion === "string" ? initializeBody.result.protocolVersion : MCP_VERSION;
    if (!SUPPORTED_MCP_VERSIONS.has(negotiatedVersion)) {
      return reportPage("MCP protocol negotiation failed", {
        run_id: runId,
        completed_at: completedAt,
        step: "mcp_protocol_negotiation",
        ok: false,
        offered_protocol_version: MCP_VERSION,
        returned_protocol_version: negotiatedVersion,
        supported_protocol_versions: [...SUPPORTED_MCP_VERSIONS],
        token_issued: true,
        token_retained: false,
        tool_invocation_performed: false,
      }, 502);
    }
    const initializedResponse = await mcpPost(accessToken, {
      jsonrpc: "2.0",
      method: "notifications/initialized",
    }, sessionId, negotiatedVersion, trace, "mcp_initialized_notification");
    if (!initializedResponse.ok) {
      return reportPage("MCP initialized notification failed", {
        run_id: runId,
        completed_at: completedAt,
        step: "mcp_initialized_notification",
        ok: false,
        http_status: initializedResponse.status,
        negotiated_protocol_version: negotiatedVersion,
        token_issued: true,
        token_retained: false,
        tool_invocation_performed: false,
      }, 502);
    }
    const toolsResponse = await mcpPost(accessToken, { jsonrpc: "2.0", id: 2, method: "tools/list", params: {} }, sessionId, negotiatedVersion, trace, "tools_list");
    const toolsBody = await parseMcpEnvelope(toolsResponse);
    if (!toolsResponse.ok || toolsBody.error || !toolsBody.result) {
      return reportPage("MCP tools listing failed", {
        run_id: runId,
        completed_at: completedAt,
        step: "tools_list",
        ok: false,
        http_status: toolsResponse.status,
        json_rpc_error: toolsBody.error ?? null,
        negotiated_protocol_version: negotiatedVersion,
        token_issued: true,
        token_retained: false,
        tool_invocation_performed: false,
      }, 502);
    }
    const tools = Array.isArray(toolsBody.result.tools) ? toolsBody.result.tools : [];
    const safeTools = tools.slice(0, 100).map((tool) => {
      const candidate = tool as Record<string, unknown>;
      return {
        name: typeof candidate.name === "string" ? candidate.name : null,
        title: typeof candidate.title === "string" ? candidate.title : null,
      };
    });
    return reportPage("Read-only CIMD test completed", {
      schema: "minority-prophet.openid-aiim-run.v1",
      lane: "exploratory-interoperability",
      run_id: runId,
      completed_at: completedAt,
      ok: true,
      resource: RESOURCE,
      client_id: CLIENT_ID,
      redirect_uri: REDIRECT_URI,
      requested_scope: REQUESTED_SCOPE,
      token_endpoint_auth_method: "private_key_jwt",
      client_assertion_signing_alg: "RS256",
      response_issuer: responseIssuer ?? "not_returned",
      negotiated_protocol_version: negotiatedVersion,
      mcp_session_id_returned: Boolean(sessionId),
      tools_listed: safeTools,
      token_issued: true,
      token_retained: false,
      tool_invocation_performed: false,
      authority_granted_by_this_report: false,
    });
  } catch (error) {
    return reportPage("CIMD test failed", {
      run_id: runId,
      completed_at: completedAt,
      step: "network_or_response_processing",
      ok: false,
      error: error instanceof Error ? error.message : "Unexpected test failure",
      credentials_retained: false,
      tool_invocation_performed: false,
    }, 502);
  }
}

export async function handleOpenIdAiim(request: Request, env?: AiimEnv): Promise<Response | null> {
  const url = new URL(request.url);
  if (url.pathname === "/openid-aiim/client.json" && request.method === "GET") {
    return new Response(JSON.stringify(clientMetadata()), { headers: jsonHeaders });
  }
  if (url.pathname === "/openid-aiim/jwks.json" && request.method === "GET") {
    return new Response(JSON.stringify({ keys: [CLIENT_PUBLIC_JWK] }), { headers: jsonHeaders });
  }
  if (url.pathname === "/openid-aiim/reproduce" && request.method === "GET") return reproducePage();
  if (url.pathname === "/openid-aiim/diagnostics.json" && request.method === "GET") return diagnostics();
  if (url.pathname === "/openid-aiim/start" && request.method === "GET") return startAuthorization(request, env);
  if (url.pathname === "/openid-aiim/callback" && request.method === "GET") return callback(request, env);
  return null;
}
