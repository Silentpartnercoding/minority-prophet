const RESOURCE = "https://mcp.braas.dev/mcp";
const RESOURCE_METADATA = "https://mcp.braas.dev/.well-known/oauth-protected-resource";
const ISSUER = "https://as.braas.dev";
const AUTHORIZATION_ENDPOINT = "https://as.braas.dev/authorize";
const TOKEN_ENDPOINT = "https://as.braas.dev/token";
const PREREGISTERED_CLIENT_ID = "partner-jameshe";
const CIMD_CLIENT_ID = "https://minorityprophet.org/openid-aiim/client.json";
const CLIENT_KEY_ID = "f35c5d1f-b07b-4525-9587-c0f21295a972";
const REDIRECT_URI = "https://minorityprophet.org/openid-aiim/callback";
const SCOPE = "mcp";
// Keith opened first_contact_ping on 7 Sep as a no-argument no-op so the path can be
// re-run without CK-side approval. From that message tools/list now projects TWO tools:
// first_contact_ping callable, and file_read listed but deliberately restricted on their
// side. A file_read refusal is therefore the expected observation, not a client fault.
const CALL_TOOL = "first_contact_ping";
const RESTRICTED_TOOL = "file_read";
const COOKIE_NAME = "mp_aiim_ck_oauth";
const MCP_VERSION = "2025-06-18";
const FLOW_TTL_MS = 10 * 60 * 1000;

interface CkEnv {
  MP_AIIM_STATE_SECRET?: string;
  MP_AIIM_CLIENT_PRIVATE_KEY?: string;
  DB?: D1Database;
}

type Mode = "preregistered" | "cimd";

interface FlowState {
  state: string;
  verifier: string;
  issuedAt: number;
  issuer: string;
  mode: Mode;
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
  token_endpoint_auth_signing_alg_values_supported?: string[];
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

interface EvidenceStep {
  step: string;
  at: string;
  http_status?: number;
  ok: boolean;
  correlation_ids?: Record<string, string>;
  detail?: Record<string, unknown>;
}

function stateSecret(env?: CkEnv): string | undefined {
  return env?.MP_AIIM_STATE_SECRET ?? process.env.MP_AIIM_STATE_SECRET;
}

function clientPrivateKey(env?: CkEnv): string | undefined {
  return env?.MP_AIIM_CLIENT_PRIVATE_KEY ?? process.env.MP_AIIM_CLIENT_PRIVATE_KEY;
}

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
    iss: CIMD_CLIENT_ID,
    sub: CIMD_CLIENT_ID,
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
    if (!parsed.state || !parsed.verifier || !Number.isFinite(parsed.issuedAt) || parsed.issuer !== ISSUER) return null;
    if (parsed.mode !== "preregistered" && parsed.mode !== "cimd") return null;
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
  return new Response(`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>${escapeHtml(title)} — Minority Prophet</title><style>:root{color-scheme:light;--ink:#111510;--paper:#f1f0e8;--acid:#d8ff42;--orange:#ff6534;--muted:#66695f;--line:#cbcbbf}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font-family:Arial,sans-serif}.shell{max-width:960px;margin:0 auto;padding:56px 24px 96px}.kicker{font:700 11px/1.4 monospace;letter-spacing:.14em;text-transform:uppercase;color:var(--orange)}h1{max-width:820px;margin:18px 0 24px;font:400 clamp(45px,7vw,78px)/.95 Georgia,serif;letter-spacing:-.045em}.lede{max-width:760px;color:#4f534a;font:18px/1.55 Georgia,serif}.card{margin-top:28px;padding:24px;border:1px solid var(--ink);background:#fff}.card.dark{background:var(--ink);color:#fff}.label{font:700 10px monospace;text-transform:uppercase;letter-spacing:.1em;color:var(--muted)}.dark .label{color:var(--acid)}dl{display:grid;grid-template-columns:190px 1fr;margin:18px 0 0}dt,dd{margin:0;padding:10px 0;border-top:1px solid var(--line);font:12px/1.5 monospace;overflow-wrap:anywhere}dt{color:var(--muted)}.button{display:inline-block;margin:22px 8px 0 0;padding:16px 20px;border:0;background:var(--ink);color:#fff;font:700 11px monospace;text-transform:uppercase;letter-spacing:.08em;text-decoration:none}.button.secondary{background:transparent;color:var(--ink);border:1px solid var(--ink)}pre{overflow:auto;white-space:pre-wrap;overflow-wrap:anywhere;margin:16px 0 0;padding:18px;background:#171b15;color:#e8eadf;font:12px/1.6 monospace}.boundary{margin-top:22px;color:var(--muted);font:11px/1.55 monospace}@media(max-width:620px){dl{grid-template-columns:1fr}dt{padding-bottom:2px}dd{padding-top:2px;border-top:0}}</style></head><body><main class="shell">${content}</main></body></html>`, {
    status,
    headers: {
      "cache-control": "no-store",
      "content-security-policy": "default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; frame-ancestors 'none'",
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
  return page(title, `<p class="kicker">OpenID AIIM · CK SaaS interoperability</p><h1>${escapeHtml(title)}</h1><p class="lede">Redacted evidence from the bounded CK recording adapter. No credential or authorization artifact is displayed or retained.</p><section class="card dark"><p class="label">Evidence record</p><pre>${escapeHtml(JSON.stringify(report, null, 2))}</pre></section><a class="button secondary" href="/openid-aiim/ck/reproduce">Back to CK test page</a><p class="boundary">Authorization codes, access tokens, PKCE verifiers, client assertions, cookies, and private-key material are excluded. A failed client-authentication attempt consumes its code; every retry starts a fresh authorization round-trip with a new verifier and JWT ID.</p>`, status, { "set-cookie": clearFlowCookie() });
}

function correlations(headers: Headers): Record<string, string> | undefined {
  const keys = ["x-request-id", "x-correlation-id", "traceparent", "cf-ray", "seal_in"];
  const found: Record<string, string> = {};
  for (const key of keys) {
    const value = headers.get(key);
    if (value) found[key] = value.slice(0, 256);
  }
  return Object.keys(found).length ? found : undefined;
}

function evidence(step: string, response: Response, detail?: Record<string, unknown>): EvidenceStep {
  return {
    step,
    at: new Date().toISOString(),
    http_status: response.status,
    ok: response.ok,
    correlation_ids: correlations(response.headers),
    detail,
  };
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
  for (const [key, value] of headers) result[key] = SECRET_HEADERS.has(key.toLowerCase()) ? REDACTED : key.toLowerCase() === "location" ? redactUrl(value) : value;
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
      if (size > MAX_CAPTURE_BODY_BYTES) throw new Error("CK capture body exceeded 64 KiB; run aborted before retaining an incomplete trace");
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
  throw new Error("CK capture refused an unrecognized body format");
}

async function saveCapture(trace: CaptureContext, record: CaptureRecord): Promise<void> {
  const result = await trace.db.prepare("INSERT INTO openid_aiim_ck_capture (run_id, seq, at, record_json) VALUES (?, ?, ?, ?)")
    .bind(trace.runId, trace.nextSeq++, record.at, JSON.stringify(record)).run();
  if (!result.success) throw new Error("CK capture storage did not confirm the evidence write");
}

async function captureExchange(trace: CaptureContext, phase: string, request: Pick<Request, "url" | "method" | "headers" | "body">, response: Response | null, extra?: Record<string, unknown>): Promise<void> {
  const requestBody = redactBody(await boundedText(request.body), request.headers.get("content-type"));
  const responseBody = response ? redactBody(await boundedText(response.clone().body), response.headers.get("content-type")) : null;
  const record = {
    phase,
    at: new Date().toISOString(),
    request: { method: request.method, url: redactUrl(request.url), headers: redactHeaders(request.headers), body: requestBody },
    response: response ? { status: response.status, headers: redactHeaders(response.headers), body: responseBody } : null,
    ...extra,
  };
  await saveCapture(trace, record);
}

async function capturedFetch(url: string, init: RequestInit, trace: CaptureContext | undefined, phase: string, extra?: Record<string, unknown>): Promise<Response> {
  const request = new Request(url, init);
  const captureRequest = trace ? request.clone() : undefined;
  const response = await fetch(request);
  if (trace && captureRequest) await captureExchange(trace, phase, captureRequest, response, extra);
  return response;
}

async function fetchJson<T>(url: string, trace?: CaptureContext, phase = "metadata"): Promise<{ response: Response; data: T }> {
  const response = await capturedFetch(url, { headers: { accept: "application/json" }, redirect: "manual", signal: AbortSignal.timeout(10_000) }, trace, phase);
  if (response.status >= 300 && response.status < 400) throw new Error(`${url} attempted to redirect`);
  if (!response.ok) throw new Error(`${url} returned HTTP ${response.status}`);
  return { response, data: await response.json() as T };
}

async function validateDiscovery(trace?: CaptureContext): Promise<{ protectedResource: ProtectedResourceMetadata; authorizationServer: OAuthMetadata }> {
  if (trace) {
    const challenge = await capturedFetch(RESOURCE, { method: "POST", headers: { accept: "application/json, text/event-stream", "content-type": "application/json" }, body: JSON.stringify({ jsonrpc: "2.0", id: 0, method: "initialize", params: { protocolVersion: MCP_VERSION, capabilities: {}, clientInfo: { name: "minority-prophet-openid-aiim", version: "1.0.0" } } }), redirect: "manual", signal: AbortSignal.timeout(15_000) }, trace, "tokenless_mcp");
    const challengeHeader = challenge.headers.get("www-authenticate") ?? "";
    const metadataUrl = /resource_metadata="([^"]+)"/u.exec(challengeHeader)?.[1];
    if (challenge.status !== 401 || metadataUrl !== RESOURCE_METADATA) throw new Error("Tokenless MCP challenge did not advertise the expected OPRM URL");
  }
  const { data: protectedResource } = await fetchJson<ProtectedResourceMetadata>(RESOURCE_METADATA, trace, "oprm");
  if (protectedResource.resource !== RESOURCE) throw new Error("Protected resource identifier mismatch");
  if (!protectedResource.authorization_servers?.includes(ISSUER)) throw new Error("CK authorization server is not advertised");
  if (!protectedResource.scopes_supported?.includes(SCOPE)) throw new Error("The mcp scope is not advertised");
  const { data: authorizationServer } = await fetchJson<OAuthMetadata>(`${ISSUER}/.well-known/oauth-authorization-server`, trace, "authorization_server_metadata");
  if (authorizationServer.issuer !== ISSUER) throw new Error("Authorization-server issuer mismatch");
  if (authorizationServer.authorization_endpoint !== AUTHORIZATION_ENDPOINT) throw new Error("Unexpected authorization endpoint");
  if (authorizationServer.token_endpoint !== TOKEN_ENDPOINT) throw new Error("Unexpected token endpoint");
  if (!authorizationServer.code_challenge_methods_supported?.includes("S256")) throw new Error("PKCE S256 is not advertised");
  if (!authorizationServer.token_endpoint_auth_methods_supported?.includes("none")) throw new Error("Pre-registered public-client auth is not advertised");
  if (!authorizationServer.token_endpoint_auth_methods_supported?.includes("private_key_jwt")) throw new Error("private_key_jwt is not advertised");
  if (!authorizationServer.token_endpoint_auth_signing_alg_values_supported?.includes("RS256")) throw new Error("RS256 client assertions are not advertised");
  if (authorizationServer.client_id_metadata_document_supported !== true) throw new Error("CIMD is not advertised");
  return { protectedResource, authorizationServer };
}

function reproducePage(): Response {
  return page("Run the CK SaaS interoperability test", `<p class="kicker">OpenID AIIM · bounded test surface</p><h1>Two client paths. One governed tool call.</h1><p class="lede">Each button starts a new Authorization Code + PKCE S256 flow against CK SaaS, initializes MCP, verifies that <code>${CALL_TOOL}</code> is projected, and calls it once with no arguments. <code>${RESTRICTED_TOOL}</code> may also be listed and is expected to remain restricted on the CK side.</p><section class="card"><p class="label">Fixed inputs</p><dl><dt>MCP resource</dt><dd>${RESOURCE}</dd><dt>Pre-registered client</dt><dd>${PREREGISTERED_CLIENT_ID} · token auth none</dd><dt>CIMD client</dt><dd>${CIMD_CLIENT_ID} · private_key_jwt RS256</dd><dt>Callback</dt><dd>${REDIRECT_URI}</dd><dt>Scope</dt><dd>${SCOPE}</dd><dt>Tool under test</dt><dd>${CALL_TOOL} · no arguments</dd><dt>Also permitted</dt><dd>${RESTRICTED_TOOL} · listed, restricted by CK</dd></dl><a class="button" href="/openid-aiim/ck/start?mode=preregistered&amp;capture=1">Record cold OAuth run →</a><a class="button secondary" href="/openid-aiim/ck/start?mode=preregistered">Run pre-registered path →</a><a class="button secondary" href="/openid-aiim/ck/start?mode=cimd">Run CIMD path →</a><a class="button secondary" href="/openid-aiim/ck/diagnostics.json">View discovery checks</a></section><p class="boundary">Recorded runs require a fresh CK flow cookie and durable capture storage. They stop if the initial 401 challenge or evidence write fails. Each click creates a fresh state, PKCE verifier, and authorization code. CIMD also creates a fresh JWT ID. Failed client authentication is never retried with the same code.</p>`);
}

async function diagnostics(): Promise<Response> {
  const checkedAt = new Date().toISOString();
  try {
    const { protectedResource, authorizationServer } = await validateDiscovery();
    return Response.json({ schema: "minority-prophet.openid-aiim-ck-diagnostics.v1", checked_at: checkedAt, ok: true, checks: { protected_resource_reachable: true, resource_exact_match: protectedResource.resource === RESOURCE, issuer_advertised: protectedResource.authorization_servers?.includes(ISSUER) === true, mcp_scope_advertised: protectedResource.scopes_supported?.includes(SCOPE) === true, authorization_server_reachable: true, issuer_exact_match: authorizationServer.issuer === ISSUER, pkce_s256_advertised: authorizationServer.code_challenge_methods_supported?.includes("S256") === true, preregistered_auth_advertised: authorizationServer.token_endpoint_auth_methods_supported?.includes("none") === true, private_key_jwt_advertised: authorizationServer.token_endpoint_auth_methods_supported?.includes("private_key_jwt") === true, rs256_advertised: authorizationServer.token_endpoint_auth_signing_alg_values_supported?.includes("RS256") === true, cimd_advertised: authorizationServer.client_id_metadata_document_supported === true }, credentials_retained: false }, { headers: { "cache-control": "no-store", "x-robots-tag": "noindex, nofollow" } });
  } catch (error) {
    return Response.json({ schema: "minority-prophet.openid-aiim-ck-diagnostics.v1", checked_at: checkedAt, ok: false, error: error instanceof Error ? error.message : "Discovery validation failed", credentials_retained: false }, { status: 502, headers: { "cache-control": "no-store", "x-robots-tag": "noindex, nofollow" } });
  }
}

async function startAuthorization(request: Request, env?: CkEnv): Promise<Response> {
  const secret = stateSecret(env);
  if (!secret || secret.length < 32) return reportPage("CK test surface is not configured", { step: "local_configuration", ok: false, error: "State-signing secret is unavailable" }, 503);
  const mode = new URL(request.url).searchParams.get("mode");
  if (mode !== "preregistered" && mode !== "cimd") return reportPage("CK test mode rejected", { step: "input_validation", ok: false, error: "Mode must be preregistered or cimd" }, 400);
  const capture = new URL(request.url).searchParams.get("capture") === "1";
  if (capture && !env?.DB) return reportPage("CK capture is not configured", { step: "local_configuration", ok: false, error: "Durable capture binding is unavailable" }, 503);
  if (capture && readCookie(request, COOKIE_NAME)) return reportPage("CK cold start rejected", { step: "cold_start", ok: false, error: "An earlier CK flow cookie is present" }, 409);
  const trace: CaptureContext | undefined = capture && env?.DB ? { db: env.DB, runId: crypto.randomUUID(), nextSeq: 0 } : undefined;
  try {
    if (trace) await saveCapture(trace, { phase: "capture_start", at: new Date().toISOString(), cold_start: { flow_cookie_present: false, token_cache: "none", metadata_cache: "none" } });
    await validateDiscovery(trace);
    const verifier = randomValue(48);
    const state = randomValue(32);
    const authorizationUrl = new URL(AUTHORIZATION_ENDPOINT);
    authorizationUrl.search = new URLSearchParams({ response_type: "code", client_id: mode === "cimd" ? CIMD_CLIENT_ID : PREREGISTERED_CLIENT_ID, redirect_uri: REDIRECT_URI, scope: SCOPE, state, code_challenge: await sha256(verifier), code_challenge_method: "S256", resource: RESOURCE }).toString();
    if (trace) await captureExchange(trace, "authorization_redirect", new Request(authorizationUrl), null);
    const cookie = await encodeFlow({ state, verifier, issuedAt: Date.now(), issuer: ISSUER, mode, captureRunId: trace?.runId, captureNextSeq: trace?.nextSeq }, secret);
    return new Response(null, { status: 302, headers: { "cache-control": "no-store", location: authorizationUrl.toString(), "referrer-policy": "no-referrer", "set-cookie": flowCookie(cookie), "x-robots-tag": "noindex, nofollow" } });
  } catch (error) {
    return reportPage("CK discovery preflight failed", { step: "discovery_preflight", ok: false, error: error instanceof Error ? error.message : "Discovery preflight failed", token_issued: false }, 502);
  }
}

async function parseMcpEnvelope(response: Response): Promise<McpEnvelope> {
  const body = await response.text();
  if (!body) return {};
  if ((response.headers.get("content-type") ?? "").includes("text/event-stream")) {
    const data = body.split(/\r?\n/u).filter((line) => line.startsWith("data:")).map((line) => line.slice(5).trim()).filter(Boolean).at(-1);
    if (!data) throw new Error("MCP event stream contained no JSON data event");
    return JSON.parse(data) as McpEnvelope;
  }
  return JSON.parse(body) as McpEnvelope;
}

async function mcpPost(accessToken: string, body: Record<string, unknown>, sessionId?: string, protocolVersion?: string, trace?: CaptureContext, phase = "mcp"): Promise<Response> {
  const headers: Record<string, string> = { accept: "application/json, text/event-stream", authorization: `Bearer ${accessToken}`, "content-type": "application/json" };
  if (sessionId) headers["Mcp-Session-Id"] = sessionId;
  if (protocolVersion) headers["MCP-Protocol-Version"] = protocolVersion;
  const response = await capturedFetch(RESOURCE, { method: "POST", headers, body: JSON.stringify(body), redirect: "manual", signal: AbortSignal.timeout(15_000) }, trace, phase);
  if (response.status >= 300 && response.status < 400) throw new Error("MCP endpoint attempted to redirect a bearer-token request");
  return response;
}

async function callback(request: Request, env?: CkEnv): Promise<Response> {
  const provisionalRunId = crypto.randomUUID();
  const startedAt = new Date().toISOString();
  const timeline: EvidenceStep[] = [];
  const secret = stateSecret(env);
  if (!secret || secret.length < 32) return reportPage("CK callback rejected", { run_id: provisionalRunId, step: "local_configuration", ok: false, error: "State-signing secret is unavailable" }, 503);
  const url = new URL(request.url);
  const encodedFlow = readCookie(request, COOKIE_NAME);
  const flow = encodedFlow ? await decodeFlow(encodedFlow, secret) : null;
  if (!flow || Date.now() - flow.issuedAt > FLOW_TTL_MS || Date.now() < flow.issuedAt - 30_000) return reportPage("CK callback rejected", { run_id: provisionalRunId, step: "state_validation", ok: false, error: "Missing, invalid, or expired signed CK flow state" }, 400);
  const runId = flow.captureRunId ?? provisionalRunId;
  if (flow.captureRunId && (!env?.DB || !Number.isInteger(flow.captureNextSeq))) return reportPage("CK capture is not configured", { run_id: runId, step: "local_configuration", ok: false, error: "Durable capture binding or sequence is unavailable" }, 503);
  const trace: CaptureContext | undefined = flow.captureRunId && env?.DB ? { db: env.DB, runId, nextSeq: flow.captureNextSeq! } : undefined;
  if (url.searchParams.get("state") !== flow.state) return reportPage("CK callback rejected", { run_id: runId, step: "state_validation", ok: false, error: "OAuth state mismatch" }, 400);
  const responseIssuer = url.searchParams.get("iss");
  if (responseIssuer && responseIssuer !== ISSUER) return reportPage("CK callback rejected", { run_id: runId, step: "issuer_validation", ok: false, error: "Authorization response issuer mismatch" }, 400);
  const authorizationError = url.searchParams.get("error");
  if (authorizationError) return reportPage("CK authorization failed", { run_id: runId, step: "authorization", ok: false, oauth_error: authorizationError, oauth_error_description: url.searchParams.get("error_description"), token_issued: false }, 400);
  const code = url.searchParams.get("code");
  if (!code) return reportPage("CK callback rejected", { run_id: runId, step: "authorization", ok: false, error: "No authorization code or OAuth error was returned" }, 400);
  timeline.push({ step: "authorization_code_received", at: new Date().toISOString(), ok: true, detail: { response_issuer: responseIssuer ?? "not_returned" } });

  try {
    if (trace) await captureExchange(trace, "authorization_callback", request, null);
    const clientId = flow.mode === "cimd" ? CIMD_CLIENT_ID : PREREGISTERED_CLIENT_ID;
    const tokenParameters: Record<string, string> = { grant_type: "authorization_code", code, client_id: clientId, redirect_uri: REDIRECT_URI, code_verifier: flow.verifier, resource: RESOURCE };
    let assertionEvidence: Record<string, unknown> | undefined;
    if (flow.mode === "cimd") {
      const signingPem = clientPrivateKey(env);
      if (!signingPem?.includes("-----BEGIN PRIVATE KEY-----")) return reportPage("CK callback rejected", { run_id: runId, mode: flow.mode, step: "local_configuration", ok: false, error: "Client signing key is unavailable" }, 503);
      tokenParameters.client_assertion_type = "urn:ietf:params:oauth:client-assertion-type:jwt-bearer";
      tokenParameters.client_assertion = await clientAssertion(signingPem);
      const [header, claims] = tokenParameters.client_assertion.split(".");
      const decodedHeader = JSON.parse(new TextDecoder().decode(decodeB64url(header))) as Record<string, unknown>;
      const decodedClaims = JSON.parse(new TextDecoder().decode(decodeB64url(claims))) as Record<string, unknown>;
      assertionEvidence = { assertion: { header: { alg: decodedHeader.alg, kid: decodedHeader.kid }, claims: { iss: decodedClaims.iss, sub: decodedClaims.sub, aud: decodedClaims.aud, exp: decodedClaims.exp } } };
    }
    const tokenResponse = await capturedFetch(TOKEN_ENDPOINT, { method: "POST", headers: { accept: "application/json", "content-type": "application/x-www-form-urlencoded" }, body: new URLSearchParams(tokenParameters), redirect: "manual", signal: AbortSignal.timeout(15_000) }, trace, "token_exchange", assertionEvidence);
    if (tokenResponse.status >= 300 && tokenResponse.status < 400) throw new Error("Token endpoint attempted to redirect the authorization-code exchange");
    const tokenBody = await tokenResponse.json() as Record<string, unknown>;
    timeline.push(evidence("token_exchange", tokenResponse, { token_type: typeof tokenBody.token_type === "string" ? tokenBody.token_type : null, scope: typeof tokenBody.scope === "string" ? tokenBody.scope : null }));
    if (!tokenResponse.ok || typeof tokenBody.access_token !== "string") return reportPage("CK token exchange failed", { schema: "minority-prophet.openid-aiim-ck-run.v1", run_id: runId, started_at: startedAt, completed_at: new Date().toISOString(), mode: flow.mode, ok: false, failed_step: "token_exchange", oauth_error: tokenBody.error ?? "missing_access_token", oauth_error_description: tokenBody.error_description ?? null, timeline, retry_rule: "Start a fresh authorization round-trip; never reuse this code.", token_retained: false }, 502);
    const accessToken = tokenBody.access_token;

    const initializeResponse = await mcpPost(accessToken, { jsonrpc: "2.0", id: 1, method: "initialize", params: { protocolVersion: MCP_VERSION, capabilities: {}, clientInfo: { name: "minority-prophet-openid-aiim", title: "Minority Prophet OpenID AIIM Test Client", version: "1.0.0" } } }, undefined, undefined, trace, "mcp_initialize");
    const initializeBody = await parseMcpEnvelope(initializeResponse);
    const negotiatedVersion = typeof initializeBody.result?.protocolVersion === "string" ? initializeBody.result.protocolVersion : MCP_VERSION;
    timeline.push(evidence("mcp_initialize", initializeResponse, { negotiated_protocol_version: negotiatedVersion }));
    if (!initializeResponse.ok || initializeBody.error || !initializeBody.result) return reportPage("CK MCP initialization failed", { run_id: runId, mode: flow.mode, ok: false, failed_step: "mcp_initialize", timeline, token_retained: false }, 502);
    const sessionId = initializeResponse.headers.get("Mcp-Session-Id") ?? undefined;

    const initializedResponse = await mcpPost(accessToken, { jsonrpc: "2.0", method: "notifications/initialized" }, sessionId, negotiatedVersion, trace, "mcp_initialized_notification");
    timeline.push(evidence("mcp_initialized_notification", initializedResponse));
    if (!initializedResponse.ok) return reportPage("CK MCP initialized notification failed", { run_id: runId, mode: flow.mode, ok: false, failed_step: "mcp_initialized_notification", timeline, token_retained: false }, 502);

    const toolsResponse = await mcpPost(accessToken, { jsonrpc: "2.0", id: 2, method: "tools/list", params: {} }, sessionId, negotiatedVersion, trace, "tools_list");
    const toolsBody = await parseMcpEnvelope(toolsResponse);
    const tools = Array.isArray(toolsBody.result?.tools) ? toolsBody.result.tools : [];
    const toolNames = tools.map((tool) => typeof (tool as Record<string, unknown>).name === "string" ? (tool as Record<string, unknown>).name as string : null).filter(Boolean);
    timeline.push(evidence("tools_list", toolsResponse, { tool_names: toolNames }));
    const unexpectedTools = toolNames.filter((name) => name !== CALL_TOOL && name !== RESTRICTED_TOOL);
    if (!toolsResponse.ok || toolsBody.error || !toolNames.includes(CALL_TOOL) || unexpectedTools.length) return reportPage("CK tool projection check failed", { run_id: runId, mode: flow.mode, ok: false, failed_step: "tools_list", required_tool: CALL_TOOL, permitted_tools: [CALL_TOOL, RESTRICTED_TOOL], actual_tool_names: toolNames, unexpected_tool_names: unexpectedTools, timeline, token_retained: false }, 502);

    const toolResponse = await mcpPost(accessToken, { jsonrpc: "2.0", id: 3, method: "tools/call", params: { name: CALL_TOOL, arguments: {} } }, sessionId, negotiatedVersion, trace, "tools_call");
    const toolBody = await parseMcpEnvelope(toolResponse);
    const resultDigest = toolBody.result ? await sha256(JSON.stringify(toolBody.result)) : null;
    const isError = toolBody.result?.isError === true;
    timeline.push(evidence(`tools_call_${CALL_TOOL}`, toolResponse, { result_digest_sha256_b64url: resultDigest, result_is_error: isError }));
    if (!toolResponse.ok || toolBody.error || !toolBody.result || isError) return reportPage("CK harmless tool call failed", { run_id: runId, mode: flow.mode, ok: false, failed_step: `tools_call_${CALL_TOOL}`, timeline, token_retained: false }, 502);

    return reportPage("CK interoperability path completed", { schema: "minority-prophet.openid-aiim-ck-run.v1", run_id: runId, started_at: startedAt, completed_at: new Date().toISOString(), mode: flow.mode, ok: true, resource: RESOURCE, issuer: ISSUER, client_id: clientId, redirect_uri: REDIRECT_URI, requested_scope: SCOPE, token_endpoint_auth_method: flow.mode === "cimd" ? "private_key_jwt" : "none", client_assertion_signing_alg: flow.mode === "cimd" ? "RS256" : null, fresh_code_rule_observed: true, negotiated_protocol_version: negotiatedVersion, mcp_session_id_returned: Boolean(sessionId), projected_tool_names: toolNames, invoked_tool: CALL_TOOL, harmless_arguments: {}, restricted_tool_projected: toolNames.includes(RESTRICTED_TOOL),  tool_result_digest_sha256_b64url: resultDigest, timeline, token_retained: false, credentials_retained: false });
  } catch (error) {
    return reportPage("CK interoperability path failed", { schema: "minority-prophet.openid-aiim-ck-run.v1", run_id: runId, started_at: startedAt, completed_at: new Date().toISOString(), mode: flow.mode, ok: false, failed_step: "network_or_response_processing", error: error instanceof Error ? error.message : "Unexpected test failure", timeline, retry_rule: "Start a fresh authorization round-trip; never reuse this code.", credentials_retained: false }, 502);
  }
}

export async function handleOpenIdAiimCk(request: Request, env?: CkEnv): Promise<Response | null> {
  const url = new URL(request.url);
  if (url.pathname === "/openid-aiim/ck/reproduce" && request.method === "GET") return reproducePage();
  if (url.pathname === "/openid-aiim/ck/diagnostics.json" && request.method === "GET") return diagnostics();
  if (url.pathname === "/openid-aiim/ck/start" && request.method === "GET") return startAuthorization(request, env);
  if (url.pathname === "/openid-aiim/callback" && request.method === "GET" && readCookie(request, COOKIE_NAME)) return callback(request, env);
  return null;
}
