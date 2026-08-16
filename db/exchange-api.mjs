import { acceptContribution, authenticateAgent, createRouteQuery, ensureExchangeSchema, getAgentAccount, getContributionStatus, getCreditLedger, getRouteQueryStatus, listOpenRouteBounties, registerAgentSigningKey, reserveResultAccess, signupAgent, submitContribution, submitWorkingRouteComp } from "./exchange-store.mjs";

const json = (body, status = 200) => Response.json(body, { status, headers: { "cache-control": "no-store" } });

async function tokenDigest(value) {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(value));
  return new Uint8Array(digest);
}

async function secureTokenEqual(actual, expected) {
  if (!actual || !expected) return false;
  const [left, right] = await Promise.all([tokenDigest(actual), tokenDigest(expected)]);
  let difference = left.length ^ right.length;
  const length = Math.max(left.length, right.length);
  for (let index = 0; index < length; index += 1) difference |= (left[index % left.length] ?? 0) ^ (right[index % right.length] ?? 0);
  return difference === 0;
}

export async function handleExchangeApi(request, db, options = {}) {
  if (!db) return json({ error: "exchange_database_unavailable" }, 503);
  await ensureExchangeSchema(db);
  const url = new URL(request.url);

  if (url.pathname === "/api/exchange/signup" && request.method === "POST") {
    const body = await request.json().catch(() => null);
    const result = await signupAgent(db, body);
    return json(result.ok ? result.account : { error: result.error }, result.status);
  }

  if (url.pathname === "/api/exchange/internal/accept" && request.method === "POST") {
    if (!options.verifierToken) return json({ error: "exchange_verifier_unconfigured" }, 503);
    const bearer = request.headers.get("authorization")?.startsWith("Bearer ")
      ? request.headers.get("authorization").slice(7).trim()
      : "";
    if (!(await secureTokenEqual(bearer, options.verifierToken))) return json({ error: "invalid_verifier_token" }, 401);
    const body = await request.json().catch(() => null);
    if (!body?.contributionId || body.independentlyAdditive !== true) {
      return json({ error: "invalid_verification_request" }, 400);
    }
    const result = await acceptContribution(db, {
      contributionId: body.contributionId,
      verifierReceiptId: body.verifierReceiptId,
      independentlyAdditive: true,
      reason: body.reason,
    });
    return json(result.ok ? result : { error: result.error }, result.status);
  }

  const agent = await authenticateAgent(db, request.headers.get("authorization"));
  if (!agent) return json({ error: "invalid_agent_key" }, 401);

  if (url.pathname === "/api/exchange/account" && request.method === "GET") {
    const account = await getAgentAccount(db, agent.id);
    return json(account ?? { error: "agent_not_found" }, account ? 200 : 404);
  }

  if (url.pathname === "/api/exchange/ledger" && request.method === "GET") {
    return json(await getCreditLedger(db, agent.id));
  }

  if (url.pathname === "/api/exchange/signing-keys" && request.method === "POST") {
    const body = await request.json().catch(() => null);
    const result = await registerAgentSigningKey(db, agent.id, body);
    return json(result.ok ? result.signingKey : { error: result.error }, result.status);
  }

  if (url.pathname === "/api/exchange/contributions" && request.method === "POST") {
    const body = await request.json().catch(() => null);
    const result = await submitContribution(db, agent.id, body);
    return json(result.ok ? result.contribution : { error: result.error }, result.status);
  }


  const contributionStatusMatch = url.pathname.match(/^\/api\/exchange\/contributions\/(comp|routecomp)_[A-Za-z0-9]+$/);
  if (contributionStatusMatch && request.method === "GET") {
    const contributionId = url.pathname.slice("/api/exchange/contributions/".length);
    const contribution = await getContributionStatus(db, agent.id, contributionId);
    return json(contribution ?? { error: "contribution_not_found" }, contribution ? 200 : 404);
  }

  if (url.pathname === "/api/exchange/queries" && request.method === "POST") {
    const body = await request.json().catch(() => null);
    const result = await createRouteQuery(db, agent.id, body);
    return json(result.ok ? result.query : { error: result.error }, result.status);
  }

  const queryStatusMatch = url.pathname.match(/^\/api\/exchange\/queries\/routeq_[A-Za-z0-9]+$/);
  if (queryStatusMatch && request.method === "GET") {
    const queryId = url.pathname.slice("/api/exchange/queries/".length);
    const query = await getRouteQueryStatus(db, agent.id, queryId);
    return json(query ?? { error: "working_route_query_not_found" }, query ? 200 : 404);
  }

  if (url.pathname === "/api/exchange/working-route-comps" && request.method === "POST") {
    const body = await request.json().catch(() => null);
    const result = await submitWorkingRouteComp(db, agent.id, body);
    return json(result.ok ? result.contribution : { error: result.error }, result.status);
  }

  if (url.pathname === "/api/exchange/bounties" && request.method === "GET") {
    return json({ bounties: await listOpenRouteBounties(db), authorityGranted: false });
  }

  if (url.pathname === "/api/exchange/unlock" && request.method === "POST") {
    const body = await request.json().catch(() => null);
    const result = await reserveResultAccess(db, agent.id, body?.resultId);
    return json(result.ok ? result.access : { error: result.error }, result.status);
  }

  return json({ error: "exchange_route_not_found" }, 404);
}
