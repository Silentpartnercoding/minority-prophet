import assert from "node:assert/strict";
import { DatabaseSync } from "node:sqlite";
import test from "node:test";
import { handleExchangeApi } from "../db/exchange-api.mjs";

function d1TestDatabase({ legacyAgentSchema = false } = {}) {
  const sqlite = new DatabaseSync(":memory:");
  if (legacyAgentSchema) {
    sqlite.exec(`CREATE TABLE exchange_agents (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      identity_provider TEXT NOT NULL,
      external_subject TEXT NOT NULL,
      identity_status TEXT NOT NULL DEFAULT 'self-registered',
      api_key_hash TEXT NOT NULL,
      heartbeat_minutes INTEGER NOT NULL,
      delivery_channel TEXT NOT NULL,
      daily_credit_spend_limit INTEGER NOT NULL DEFAULT 0,
      status TEXT NOT NULL DEFAULT 'active',
      created_at TEXT NOT NULL,
      UNIQUE(identity_provider, external_subject),
      UNIQUE(api_key_hash)
    )`);
  }
  const prepare = (sql) => ({
    _values: [],
    bind(...values) { this._values = values; return this; },
    first() { return sqlite.prepare(sql).get(...this._values) ?? null; },
    all() { return { results: sqlite.prepare(sql).all(...this._values) }; },
    run() {
      const result = sqlite.prepare(sql).run(...this._values);
      return { meta: { changes: Number(result.changes) } };
    },
  });
  return {
    prepare,
    async batch(statements) {
      sqlite.exec("BEGIN");
      try {
        const results = statements.map((statement) => statement.run());
        sqlite.exec("COMMIT");
        return results;
      } catch (error) {
        sqlite.exec("ROLLBACK");
        throw error;
      }
    },
  };
}

function apiRequest(path, { method = "GET", token, body } = {}) {
  return new Request(`https://awe.test${path}`, {
    method,
    headers: {
      ...(token ? { authorization: `Bearer ${token}` } : {}),
      ...(body ? { "content-type": "application/json" } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  });
}

test("first node can submit idempotently, await verification, and earn durable credits", async () => {
  const db = d1TestDatabase();
  const verifierToken = "verifier_test_secret_123456789";
  const signupResponse = await handleExchangeApi(apiRequest("/api/exchange/signup", {
    method: "POST",
    body: {
      agent: { name: "First Node", identityProvider: "custom", externalSubject: "first-node" },
      participation: { heartbeatMinutes: 15, deliveryChannel: "nexus-api", dailyCreditSpendLimit: 10 },
    },
  }), db, { verifierToken });
  assert.equal(signupResponse.status, 201);
  const signup = await signupResponse.json();
  assert.equal(signup.creditBalance, 0);

  const contributionBody = {
    recordKind: "tool-result",
    topic: "public-tool-compatibility",
    provenanceRootId: "first-node-run-0001",
    independenceBasis: "attested",
    freshnessDays: 0,
  };
  const submittedResponse = await handleExchangeApi(apiRequest("/api/exchange/contributions", {
    method: "POST", token: signup.apiKey, body: contributionBody,
  }), db, { verifierToken });
  assert.equal(submittedResponse.status, 202);
  const submitted = await submittedResponse.json();

  const replayResponse = await handleExchangeApi(apiRequest("/api/exchange/contributions", {
    method: "POST", token: signup.apiKey, body: contributionBody,
  }), db, { verifierToken });
  assert.equal(replayResponse.status, 200);
  const replay = await replayResponse.json();
  assert.equal(replay.contributionId, submitted.contributionId);
  assert.equal(replay.idempotentReplay, true);

  const pendingResponse = await handleExchangeApi(apiRequest(`/api/exchange/contributions/${submitted.contributionId}`, {
    token: signup.apiKey,
  }), db, { verifierToken });
  assert.equal(pendingResponse.status, 200);
  assert.equal((await pendingResponse.json()).status, "pending");

  const deniedVerification = await handleExchangeApi(apiRequest("/api/exchange/internal/accept", {
    method: "POST", token: "wrong-token", body: {
      contributionId: submitted.contributionId,
      verifierReceiptId: "verifier:first-node-run-0001",
      independentlyAdditive: true,
    },
  }), db, { verifierToken });
  assert.equal(deniedVerification.status, 401);

  const acceptedResponse = await handleExchangeApi(apiRequest("/api/exchange/internal/accept", {
    method: "POST", token: verifierToken, body: {
      contributionId: submitted.contributionId,
      verifierReceiptId: "verifier:first-node-run-0001",
      independentlyAdditive: true,
      reason: "reproduced_public_tool_outcome",
    },
  }), db, { verifierToken });
  assert.equal(acceptedResponse.status, 200);
  assert.equal((await acceptedResponse.json()).creditsAwarded, 2);

  const acceptedStatus = await handleExchangeApi(apiRequest(`/api/exchange/contributions/${submitted.contributionId}`, {
    token: signup.apiKey,
  }), db, { verifierToken });
  const contribution = await acceptedStatus.json();
  assert.equal(contribution.status, "accepted");
  assert.equal(contribution.creditsAwarded, 2);

  const accountResponse = await handleExchangeApi(apiRequest("/api/exchange/account", { token: signup.apiKey }), db, { verifierToken });
  assert.equal((await accountResponse.json()).creditBalance, 2);

  const ledgerResponse = await handleExchangeApi(apiRequest("/api/exchange/ledger", { token: signup.apiKey }), db, { verifierToken });
  assert.equal(ledgerResponse.status, 200);
  const ledger = await ledgerResponse.json();
  assert.equal(ledger.immutable, true);
  assert.equal(ledger.creditBalance, 2);
  assert.equal(ledger.entries.length, 1);
  assert.equal(ledger.entries[0].entryType, "earn");
  assert.equal(ledger.entries[0].balanceAfter, 2);
});

test("private operator stats exclude labeled smoke agents and fail closed without the admin token", async () => {
  const db = d1TestDatabase();
  const adminToken = "admin_test_secret_123456789";

  const unconfigured = await handleExchangeApi(apiRequest("/api/exchange/internal/stats"), db, {});
  assert.equal(unconfigured.status, 503);

  const denied = await handleExchangeApi(apiRequest("/api/exchange/internal/stats", { token: "wrong-token" }), db, { adminToken });
  assert.equal(denied.status, 401);

  const realSignup = await handleExchangeApi(apiRequest("/api/exchange/signup", {
    method: "POST",
    body: {
      agent: { name: "Agent WEX node real", identityProvider: "custom", externalSubject: "real-node" },
      participation: { heartbeatMinutes: 15, deliveryChannel: "nexus-api", dailyCreditSpendLimit: 10 },
    },
  }), db, { adminToken });
  assert.equal(realSignup.status, 201);
  const real = await realSignup.json();

  const smokeSignup = await handleExchangeApi(apiRequest("/api/exchange/signup", {
    method: "POST",
    body: {
      agent: { name: "Live smoke requester unit", identityProvider: "custom", externalSubject: "live-smoke-unit-requester" },
      participation: { heartbeatMinutes: 15, deliveryChannel: "nexus-api", dailyCreditSpendLimit: 10 },
    },
  }), db, { adminToken });
  assert.equal(smokeSignup.status, 201);

  const contribution = await handleExchangeApi(apiRequest("/api/exchange/contributions", {
    method: "POST",
    token: real.apiKey,
    body: {
      recordKind: "tool-result",
      topic: "operator-stats-test",
      provenanceRootId: "real-node-run-1",
      independenceBasis: "attested",
      freshnessDays: 0,
    },
  }), db, { adminToken });
  assert.equal(contribution.status, 202);

  const response = await handleExchangeApi(apiRequest("/api/exchange/internal/stats", { token: adminToken }), db, { adminToken });
  assert.equal(response.status, 200);
  const stats = await response.json();
  assert.equal(stats.registeredAgents, 1);
  assert.equal(stats.testAgents, 1);
  assert.equal(stats.signedAgents, 0);
  assert.equal(stats.activeAgents, 1);
  assert.equal(stats.contributingAgents, 1);
  assert.equal(stats.supportedRoutesReturned, 0);
  assert.equal(stats.testTrafficExcluded, true);
});

test("public API bounds bodies, throttles signup fingerprints, rotates keys, and deactivates accounts", async () => {
  const db = d1TestDatabase();
  const oversized = await handleExchangeApi(new Request("https://awe.test/api/exchange/signup", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ padding: "x".repeat(70_000) }),
  }), db, { clientFingerprint: "oversized-test", requireClientFingerprint: true });
  assert.equal(oversized.status, 413);

  let account;
  for (let index = 0; index < 6; index += 1) {
    const response = await handleExchangeApi(apiRequest("/api/exchange/signup", {
      method: "POST",
      body: {
        agent: { name: `Rate Node ${index}`, identityProvider: "custom", externalSubject: `rate-node-${index}` },
        participation: { heartbeatMinutes: 15, deliveryChannel: "nexus-api", dailyCreditSpendLimit: 10 },
      },
    }), db, { clientFingerprint: "same-network-client", requireClientFingerprint: true });
    if (index < 5) {
      assert.equal(response.status, 201);
      if (index === 0) account = await response.json();
    } else {
      assert.equal(response.status, 429);
      assert.ok(Number(response.headers.get("retry-after")) > 0);
    }
  }

  const rotatedResponse = await handleExchangeApi(apiRequest("/api/exchange/api-keys/rotate", {
    method: "POST", token: account.apiKey,
  }), db);
  assert.equal(rotatedResponse.status, 200);
  const rotated = await rotatedResponse.json();
  assert.notEqual(rotated.apiKey, account.apiKey);
  assert.equal((await handleExchangeApi(apiRequest("/api/exchange/account", { token: account.apiKey }), db)).status, 401);
  assert.equal((await handleExchangeApi(apiRequest("/api/exchange/account", { token: rotated.apiKey }), db)).status, 200);

  const deactivated = await handleExchangeApi(apiRequest("/api/exchange/account", { method: "DELETE", token: rotated.apiKey }), db);
  assert.equal(deactivated.status, 200);
  assert.equal((await deactivated.json()).deactivated, true);
  assert.equal((await handleExchangeApi(apiRequest("/api/exchange/account", { token: rotated.apiKey }), db)).status, 401);
});

test("deactivation upgrades an existing exchange_agents table before use", async () => {
  const db = d1TestDatabase({ legacyAgentSchema: true });
  const signupResponse = await handleExchangeApi(apiRequest("/api/exchange/signup", {
    method: "POST",
    body: {
      agent: { name: "Legacy Node", identityProvider: "custom", externalSubject: "legacy-node" },
      participation: { heartbeatMinutes: 15, deliveryChannel: "nexus-api", dailyCreditSpendLimit: 10 },
    },
  }), db);
  assert.equal(signupResponse.status, 201);
  const signup = await signupResponse.json();

  const deactivated = await handleExchangeApi(apiRequest("/api/exchange/account", {
    method: "DELETE", token: signup.apiKey,
  }), db);
  assert.equal(deactivated.status, 200);
  assert.equal((await deactivated.json()).deactivated, true);
});
