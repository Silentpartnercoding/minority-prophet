const RESOURCE = "https://mcp.descope.com";
const RESOURCE_METADATA = `${RESOURCE}/.well-known/oauth-protected-resource`;
const EXPECTED_ISSUER = "https://api.descope.com/v1/apps/agentic/P2DA3QqyF3N3BlmIqn1nr0LMFhrw/MS3AebdnI1nLELsiorZz77KmIleWt";
const AUTHORIZATION_ENDPOINT = "https://api.descope.com/oauth2/v1/apps/agentic/P2DA3QqyF3N3BlmIqn1nr0LMFhrw/MS3AebdnI1nLELsiorZz77KmIleWt/authorize";
const TOKEN_ENDPOINT = "https://api.descope.com/oauth2/v1/apps/agentic/P2DA3QqyF3N3BlmIqn1nr0LMFhrw/MS3AebdnI1nLELsiorZz77KmIleWt/token";
const CLIENT_ID = "https://minorityprophet.org/openid-aiim/client.json";
const REDIRECT_URI = "https://minorityprophet.org/openid-aiim/callback";
const REQUESTED_SCOPE = "project:read";
const COOKIE_NAME = "mp_aiim_oauth";
const MCP_VERSION = "2026-07-28";
const SUPPORTED_MCP_VERSIONS = new Set(["2026-07-28", "2025-11-25", "2025-06-18"]);
const FLOW_TTL_MS = 10 * 60 * 1000;

interface AiimEnv {
  MP_AIIM_STATE_SECRET?: string;
}

function stateSecret(env?: AiimEnv): string | undefined {
  return env?.MP_AIIM_STATE_SECRET ?? process.env.MP_AIIM_STATE_SECRET;
}

interface FlowState {
  state: string;
  verifier: string;
  issuedAt: number;
  issuer: string;
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

async function fetchJson<T>(url: string): Promise<{ response: Response; data: T }> {
  const response = await fetch(url, {
    headers: { accept: "application/json" },
    redirect: "error",
    signal: AbortSignal.timeout(10_000),
  });
  if (!response.ok) throw new Error(`${url} returned HTTP ${response.status}`);
  return { response, data: await response.json() as T };
}

async function validateDiscovery(): Promise<{
  protectedResource: ProtectedResourceMetadata;
  authorizationServer: OAuthMetadata;
}> {
  const { data: protectedResource } = await fetchJson<ProtectedResourceMetadata>(RESOURCE_METADATA);
  if (protectedResource.resource !== RESOURCE) throw new Error("Protected resource identifier does not match the MCP endpoint");
  if (!protectedResource.authorization_servers?.includes(EXPECTED_ISSUER)) throw new Error("Expected authorization server is not advertised");
  if (!protectedResource.scopes_supported?.includes(REQUESTED_SCOPE)) throw new Error("The read-only scope is not advertised");

  const { data: authorizationServer } = await fetchJson<OAuthMetadata>(`${EXPECTED_ISSUER}/.well-known/oauth-authorization-server`);
  if (authorizationServer.issuer !== EXPECTED_ISSUER) throw new Error("Authorization-server issuer mismatch");
  if (authorizationServer.authorization_endpoint !== AUTHORIZATION_ENDPOINT) throw new Error("Unexpected authorization endpoint");
  if (authorizationServer.token_endpoint !== TOKEN_ENDPOINT) throw new Error("Unexpected token endpoint");
  if (authorizationServer.client_id_metadata_document_supported !== true) throw new Error("Authorization server does not advertise CIMD");
  if (!authorizationServer.code_challenge_methods_supported?.includes("S256")) throw new Error("Authorization server does not advertise PKCE S256");
  if (!authorizationServer.token_endpoint_auth_methods_supported?.includes("none")) throw new Error("Authorization server does not advertise a public client");
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
    token_endpoint_auth_method: "none",
  };
}

function reproducePage(): Response {
  return page("Reproduce the Descope CIMD test", `<p class="kicker">OpenID AIIM · read-only test surface</p>
<h1>One stable client. One exact rerun.</h1>
<p class="lede">This page runs a standards-shaped public-client authorization attempt against Descope's OpenID AIIM MCP sandbox. It requests only <code>${REQUESTED_SCOPE}</code>. If authorization succeeds, it initializes MCP and lists tool names; it never calls a tool.</p>
<section class="card"><p class="label">Fixed inputs</p><dl>
<dt>MCP resource</dt><dd>${RESOURCE}</dd><dt>Client ID / metadata</dt><dd><a href="${CLIENT_ID}">${CLIENT_ID}</a></dd>
<dt>Callback</dt><dd>${REDIRECT_URI}</dd><dt>OAuth shape</dt><dd>Authorization Code + PKCE S256 · public client · token auth none</dd>
<dt>Requested scope</dt><dd>${REQUESTED_SCOPE} (deliberately least privilege)</dd><dt>MCP action ceiling</dt><dd>initialize → notifications/initialized → tools/list only</dd>
</dl><form method="get" action="/openid-aiim/start"><button type="submit">Start read-only CIMD attempt →</button></form>
<a class="button secondary" href="/openid-aiim/diagnostics.json">View live discovery checks</a></section>
<p class="boundary">If the validator issue is present, Descope will show <code>invalid_client</code> before login. The fixed client ID above lets the Descope operator find the matching validator request. Boundary: this is an exploratory interoperability probe, not a canonical result. Successful listing shows tool names and titles only. No project/company write scope is requested and no MCP tool call is permitted by this harness.</p>`);
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
        public_client_auth_advertised: authorizationServer.token_endpoint_auth_methods_supported?.includes("none") === true,
      },
      fixed_inputs: { resource: RESOURCE, client_id: CLIENT_ID, redirect_uri: REDIRECT_URI, scope: REQUESTED_SCOPE },
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

async function startAuthorization(env?: AiimEnv): Promise<Response> {
  const secret = stateSecret(env);
  if (!secret || secret.length < 32) {
    return reportPage("Test surface is not configured", { step: "local_configuration", ok: false, error: "State-signing secret is unavailable" }, 503);
  }
  try {
    await validateDiscovery();
    const verifier = randomValue(48);
    const state = randomValue(32);
    const cookie = await encodeFlow({ state, verifier, issuedAt: Date.now(), issuer: EXPECTED_ISSUER }, secret);
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

async function mcpPost(accessToken: string, body: Record<string, unknown>, sessionId?: string, protocolVersion?: string): Promise<Response> {
  const headers: Record<string, string> = {
    accept: "application/json, text/event-stream",
    authorization: `Bearer ${accessToken}`,
    "content-type": "application/json",
  };
  if (sessionId) headers["Mcp-Session-Id"] = sessionId;
  if (protocolVersion) headers["MCP-Protocol-Version"] = protocolVersion;
  return fetch(RESOURCE, { method: "POST", headers, body: JSON.stringify(body), redirect: "error", signal: AbortSignal.timeout(15_000) });
}

async function callback(request: Request, env?: AiimEnv): Promise<Response> {
  const runId = crypto.randomUUID();
  const completedAt = new Date().toISOString();
  const secret = stateSecret(env);
  if (!secret || secret.length < 32) {
    return reportPage("Callback rejected", { run_id: runId, completed_at: completedAt, step: "local_configuration", ok: false, error: "State-signing secret is unavailable" }, 503);
  }
  const url = new URL(request.url);
  const encodedFlow = readCookie(request, COOKIE_NAME);
  const flow = encodedFlow ? await decodeFlow(encodedFlow, secret) : null;
  if (!flow || Date.now() - flow.issuedAt > FLOW_TTL_MS || Date.now() < flow.issuedAt - 30_000) {
    return reportPage("Callback rejected", { run_id: runId, completed_at: completedAt, step: "state_validation", ok: false, error: "Missing, invalid, or expired signed flow state" }, 400);
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
    const tokenResponse = await fetch(TOKEN_ENDPOINT, {
      method: "POST",
      headers: { accept: "application/json", "content-type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        grant_type: "authorization_code",
        code,
        client_id: CLIENT_ID,
        redirect_uri: REDIRECT_URI,
        code_verifier: flow.verifier,
        resource: RESOURCE,
      }),
      redirect: "error",
      signal: AbortSignal.timeout(15_000),
    });
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
    });
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
    }, sessionId, negotiatedVersion);
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
    const toolsResponse = await mcpPost(accessToken, { jsonrpc: "2.0", id: 2, method: "tools/list", params: {} }, sessionId, negotiatedVersion);
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
  if (url.pathname === "/openid-aiim/reproduce" && request.method === "GET") return reproducePage();
  if (url.pathname === "/openid-aiim/diagnostics.json" && request.method === "GET") return diagnostics();
  if (url.pathname === "/openid-aiim/start" && request.method === "GET") return startAuthorization(env);
  if (url.pathname === "/openid-aiim/callback" && request.method === "GET") return callback(request, env);
  return null;
}
