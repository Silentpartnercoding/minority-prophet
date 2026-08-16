import assert from "node:assert/strict";
import { createServer } from "node:http";
import { execFile } from "node:child_process";
import { mkdtemp, readFile, rm, stat } from "node:fs/promises";
import { tmpdir } from "node:os";
import { resolve } from "node:path";
import { promisify } from "node:util";
import { DatabaseSync } from "node:sqlite";
import test from "node:test";
import { handleExchangeApi } from "../db/exchange-api.mjs";
import { getAccount, signup } from "../packages/awe-node/lib/client.mjs";
import { writePrivateJson } from "../packages/awe-node/lib/config.mjs";
import { createNodeRuntime, runDaemon } from "../packages/awe-node/lib/daemon.mjs";

const execFileAsync = promisify(execFile);

function d1TestDatabase() {
  const sqlite = new DatabaseSync(":memory:");
  const prepare = (sql) => ({
    _values: [],
    bind(...values) { this._values = values; return this; },
    first() { return sqlite.prepare(sql).get(...this._values) ?? null; },
    all() { return { results: sqlite.prepare(sql).all(...this._values) }; },
    run() { const result = sqlite.prepare(sql).run(...this._values); return { meta: { changes: Number(result.changes) } }; },
  });
  return {
    prepare,
    async batch(statements) {
      sqlite.exec("BEGIN");
      try { const results = statements.map((statement) => statement.run()); sqlite.exec("COMMIT"); return results; }
      catch (error) { sqlite.exec("ROLLBACK"); throw error; }
    },
  };
}

async function startExchange() {
  const db = d1TestDatabase();
  const verifierToken = "test-verifier-token-with-enough-entropy";
  const server = createServer(async (incoming, outgoing) => {
    const chunks = [];
    for await (const chunk of incoming) chunks.push(chunk);
    const address = server.address();
    const request = new Request(`http://127.0.0.1:${address.port}${incoming.url}`, {
      method: incoming.method,
      headers: incoming.headers,
      body: chunks.length ? Buffer.concat(chunks) : undefined,
      duplex: chunks.length ? "half" : undefined,
    });
    const response = await handleExchangeApi(request, db, { verifierToken });
    outgoing.writeHead(response.status, Object.fromEntries(response.headers));
    outgoing.end(Buffer.from(await response.arrayBuffer()));
  });
  await new Promise((resolveListening) => server.listen(0, "127.0.0.1", resolveListening));
  return { db, verifierToken, server, baseUrl: `http://127.0.0.1:${server.address().port}` };
}

async function exchangeJson(baseUrl, path, { method = "GET", token, body } = {}) {
  const response = await fetch(`${baseUrl}${path}`, {
    method,
    headers: { ...(token ? { authorization: `Bearer ${token}` } : {}), ...(body ? { "content-type": "application/json" } : {}) },
    body: body ? JSON.stringify(body) : undefined,
  });
  const payload = await response.json();
  assert.ok(response.ok, `${path}: ${response.status} ${JSON.stringify(payload)}`);
  return payload;
}

function toolSpan({ traceId, outcome, toolVersion = "3.1.0", clientVersion = "1.7.0", resolutionKind = "none" }) {
  return {
    traceId,
    spanId: `span-${traceId}`,
    endTime: new Date().toISOString(),
    status: { code: outcome === "success" ? "OK" : "ERROR" },
    resource: { attributes: { "service.instance.id": "PRIVATE-HOST" } },
    attributes: {
      "gen_ai.operation.name": "execute_tool",
      "gen_ai.tool.name": "io.github.example/github-mcp",
      "gen_ai.tool.call.arguments": { repository: "PRIVATE/REPOSITORY", token: "PRIVATE-TOKEN" },
      "gen_ai.tool.call.result": { body: "PRIVATE-RESULT" },
      "gen_ai.input.messages": [{ content: "PRIVATE-PROMPT" }],
      "awe.tool.registry": "mcp",
      "awe.tool.version": toolVersion,
      "awe.client.id": "claude-code",
      "awe.client.version": clientVersion,
      "awe.environment": "macos-arm64",
      "awe.auth.mode": "oauth-pkce",
      "awe.operation": "repository-search",
      "awe.resolution.kind": resolutionKind,
      "error.type": outcome === "failure" ? "oauth-callback-mismatch" : undefined,
    },
  };
}

async function accept(baseUrl, verifierToken, contributionId, suffix) {
  return exchangeJson(baseUrl, "/api/exchange/internal/accept", {
    method: "POST",
    token: verifierToken,
    body: { contributionId, verifierReceiptId: `verifier:${suffix}:accepted`, independentlyAdditive: true, reason: "independent_test_reproduction" },
  });
}

test("install-once runtime contributes privately, earns credit, and retrieves a Gate-bound route", async (context) => {
  const exchange = await startExchange();
  const directory = await mkdtemp(resolve(tmpdir(), "awe-node-test-"));
  context.after(async () => { await new Promise((resolveClose) => exchange.server.close(resolveClose)); await rm(directory, { recursive: true, force: true }); });

  const first = await signup(exchange.baseUrl, {
    agent: { name: "First node", identityProvider: "custom", externalSubject: "first-node" },
    participation: { heartbeatMinutes: 15, deliveryChannel: "nexus-api", dailyCreditSpendLimit: 10 },
  });
  const configPath = resolve(directory, "config.json");
  await writePrivateJson(configPath, {
    schema: "minority-prophet.awe-node-config.v0.1",
    baseUrl: exchange.baseUrl,
    agentId: first.agentId,
    apiKey: first.apiKey,
    policy: { shareToolOutcomes: true, shareRawTraces: false },
    collector: { host: "127.0.0.1", port: 4318, token: "local-test-token" },
    pollSeconds: 60,
  });
  const runtime = await createNodeRuntime(configPath);
  const failure = { spans: [toolSpan({ traceId: "PRIVATE-TRACE-A", outcome: "failure" })] };
  const firstIngest = await runtime.ingest(failure);
  assert.deepEqual({ submitted: firstIngest.submitted, queriesOpened: firstIngest.queriesOpened }, { submitted: 1, queriesOpened: 1 });
  const retry = await runtime.ingest(failure);
  assert.equal(retry.submitted, 1);
  assert.equal(retry.queriesOpened, 0);
  assert.equal(runtime.getState().pendingContributions.length, 1);
  assert.equal(runtime.getState().queries.length, 1);

  const serializedState = await readFile(resolve(directory, "state.json"), "utf8");
  for (const secret of ["PRIVATE-TRACE-A", "PRIVATE-HOST", "PRIVATE/REPOSITORY", "PRIVATE-TOKEN", "PRIVATE-RESULT", "PRIVATE-PROMPT"]) {
    assert.doesNotMatch(serializedState, new RegExp(secret.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
  }

  const failureContribution = runtime.getState().pendingContributions[0].contributionId;
  await accept(exchange.baseUrl, exchange.verifierToken, failureContribution, "failure-root");

  for (const suffix of ["b", "c"]) {
    const contributor = await signup(exchange.baseUrl, {
      agent: { name: `Contributor ${suffix}`, identityProvider: "custom", externalSubject: `contributor-${suffix}` },
      participation: { heartbeatMinutes: 15, deliveryChannel: "nexus-api", dailyCreditSpendLimit: 10 },
    });
    const span = toolSpan({ traceId: `independent-${suffix}`, outcome: "success", toolVersion: "3.2.0", clientVersion: "1.8.0", resolutionKind: "upgrade-client-and-tool" });
    const receiptRuntimePath = await import("../packages/awe-node/lib/receipt.mjs");
    const receipt = receiptRuntimePath.adaptOtelSpanToRouteOutcome(span, { enabled: true, shareToolOutcomes: true, agentId: contributor.agentId }).receipt;
    const contribution = await exchangeJson(exchange.baseUrl, "/api/exchange/working-route-comps", { method: "POST", token: contributor.apiKey, body: receipt });
    await accept(exchange.baseUrl, exchange.verifierToken, contribution.contributionId, `success-${suffix}`);
  }

  await runtime.reconcile();
  const state = runtime.getState();
  assert.equal(state.creditBalance, 1);
  assert.equal(state.routes.length, 1);
  assert.equal(state.routes[0].gateRequired, true);
  assert.equal(state.routes[0].workingRoute.toolVersion, "3.2.0");
  assert.equal(state.routes[0].evidence.successfulIndependentRoots, 2);
});

test("one zero-fill install command creates a generated private node identity without printing its credential", async (context) => {
  const exchange = await startExchange();
  const directory = await mkdtemp(resolve(tmpdir(), "awe-node-install-test-"));
  context.after(async () => { await new Promise((resolveClose) => exchange.server.close(resolveClose)); await rm(directory, { recursive: true, force: true }); });
  const configPath = resolve(directory, "config.json");
  const { stdout, stderr } = await execFileAsync(process.execPath, [
    resolve("packages/awe-node/bin/awe-node.mjs"),
    "install",
    "--url", exchange.baseUrl,
    "--config", configPath,
    "--no-service",
  ], { cwd: resolve("."), timeout: 10_000 });
  assert.equal(stderr, "");
  assert.match(stdout, /AWE node installed/);
  assert.match(stdout, /source .*otel\.env/);
  const configText = await readFile(configPath, "utf8");
  const config = JSON.parse(configText);
  const account = await getAccount(config);
  assert.match(account.name, /^AWE node [a-f0-9]{8}$/);
  assert.equal(config.policy.shareRawTraces, false);
  assert.equal(config.policy.sharePrompts, false);
  assert.equal(config.policy.shareToolArguments, false);
  assert.equal(config.policy.shareToolResults, false);
  assert.equal((await stat(configPath)).mode & 0o777, 0o600);
  assert.doesNotMatch(stdout, new RegExp(config.apiKey));
  assert.doesNotMatch(stdout, new RegExp(config.collector.token));
  const environmentPath = resolve(directory, "otel.env");
  assert.equal((await stat(environmentPath)).mode & 0o777, 0o600);
  assert.match(await readFile(environmentPath, "utf8"), /OTEL_EXPORTER_OTLP_HEADERS/);

  const detected = await execFileAsync(process.execPath, [
    resolve("packages/awe-node/bin/awe-node.mjs"), "runtimes", "--config", configPath,
  ], { cwd: resolve("."), timeout: 10_000 });
  const runtimeStatus = JSON.parse(detected.stdout);
  assert.equal(runtimeStatus.noRuntimeBehavior, "registered_but_safely_idle");
  assert.equal(runtimeStatus.genericOtlpHttpJson.supported, true);
  assert.ok(runtimeStatus.runtimes.some((runtime) => runtime.id === "bernstein"));

  const configured = await execFileAsync(process.execPath, [
    resolve("packages/awe-node/bin/awe-node.mjs"),
    "adapter", "claude-code",
    "--config", configPath,
    "--tool", "mcp__github__search_repositories",
    "--tool-registry", "mcp",
    "--tool-version", "3.2.0",
    "--auth-mode", "oauth-pkce",
    "--operation", "repository-search",
    "--client-version", "1.0.77",
  ], { cwd: resolve("."), timeout: 10_000 });
  assert.match(configured.stdout, /Claude Code adapter configured/);
  const claudeEnvironment = await readFile(resolve(directory, "claude-code.env"), "utf8");
  assert.match(claudeEnvironment, /CLAUDE_CODE_ENABLE_TELEMETRY/);
  assert.match(claudeEnvironment, /\/v1\/logs/);
  assert.doesNotMatch(claudeEnvironment, /OTEL_LOG_TOOL_DETAILS/);
  const updated = JSON.parse(await readFile(configPath, "utf8"));
  assert.equal(updated.adapters.claudeCode.tools.mcp__github__search_repositories.toolVersion, "3.2.0");

  const codexConfigured = await execFileAsync(process.execPath, [
    resolve("packages/awe-node/bin/awe-node.mjs"),
    "adapter", "codex", "--config", configPath,
    "--tool", "exec_command", "--tool-registry", "github", "--tool-version", "1.0.0",
    "--auth-mode", "none", "--client-version", "0.145.0",
  ], { cwd: resolve("."), timeout: 10_000 });
  assert.match(codexConfigured.stdout, /Codex adapter configured/);
  const codexFragment = await readFile(resolve(directory, "codex-otel.toml"), "utf8");
  assert.match(codexFragment, /log_user_prompt = false/);
  assert.match(codexFragment, /\/v1\/codex\/logs/);
  assert.match(codexFragment, /protocol = "json"/);

  const geminiConfigured = await execFileAsync(process.execPath, [
    resolve("packages/awe-node/bin/awe-node.mjs"),
    "adapter", "gemini-cli", "--config", configPath,
    "--tool", "run_shell_command", "--tool-registry", "github", "--tool-version", "1.1.0",
    "--auth-mode", "none", "--client-version", "0.3.0",
  ], { cwd: resolve("."), timeout: 10_000 });
  assert.match(geminiConfigured.stdout, /Gemini CLI adapter configured/);
  const geminiEnvironment = await readFile(resolve(directory, "gemini-cli.env"), "utf8");
  assert.match(geminiEnvironment, /GEMINI_TELEMETRY_LOG_PROMPTS='0'/);
  assert.match(geminiEnvironment, /GEMINI_TELEMETRY_TRACES_ENABLED='0'/);
  assert.match(geminiEnvironment, new RegExp(updated.collector.token));

  await assert.rejects(execFileAsync(process.execPath, [
    resolve("packages/awe-node/bin/awe-node.mjs"),
    "adapter", "bernstein", "--config", configPath,
    "--tool", "repository_migration", "--tool-registry", "github", "--tool-version", "1.0.0",
    "--auth-mode", "none", "--client-version", "3.12.0",
  ], { cwd: resolve("."), timeout: 10_000 }), /requires --task-role/);

  const bernsteinConfigured = await execFileAsync(process.execPath, [
    resolve("packages/awe-node/bin/awe-node.mjs"),
    "adapter", "bernstein", "--config", configPath,
    "--task-role", "migration",
    "--tool", "repository_migration", "--tool-registry", "github", "--tool-version", "1.0.0",
    "--auth-mode", "none", "--operation", "repository-migration", "--client-version", "3.12.0",
  ], { cwd: resolve("."), timeout: 10_000 });
  assert.match(bernsteinConfigured.stdout, /Bernstein adapter configured/);
  assert.match(await readFile(resolve(directory, "bernstein-plugin.yaml"), "utf8"), /awe_bernstein_plugin:AgentWexPlugin/);
  const bernsteinEnvironment = await readFile(resolve(directory, "bernstein.env"), "utf8");
  assert.match(bernsteinEnvironment, /AGENT_WEX_BERNSTEIN_ENDPOINT/);
  assert.match(bernsteinEnvironment, /AGENT_WEX_BERNSTEIN_TOOL='repository_migration'/);
  assert.match(bernsteinEnvironment, /AGENT_WEX_BERNSTEIN_ROLE='migration'/);
  const bernsteinPlugin = await readFile(resolve(directory, "awe_bernstein_plugin.py"), "utf8");
  assert.match(bernsteinPlugin, /class AgentWexPlugin/);
  assert.doesNotMatch(bernsteinPlugin, /"result_summary":/);
  assert.doesNotMatch(bernsteinPlugin, /"error":/);
});

test("localhost collector rejects unauthenticated span injection", async (context) => {
  const exchange = await startExchange();
  const directory = await mkdtemp(resolve(tmpdir(), "awe-node-auth-test-"));
  let node = null;
  context.after(async () => {
    if (node) await node.close();
    await new Promise((resolveClose) => exchange.server.close(resolveClose));
    await rm(directory, { recursive: true, force: true });
  });
  const account = await signup(exchange.baseUrl, {
    agent: { name: "Authenticated node", identityProvider: "custom", externalSubject: "authenticated-node" },
    participation: { heartbeatMinutes: 15, deliveryChannel: "nexus-api", dailyCreditSpendLimit: 10 },
  });
  const configPath = resolve(directory, "config.json");
  await writePrivateJson(configPath, {
    schema: "minority-prophet.awe-node-config.v0.1",
    baseUrl: exchange.baseUrl,
    agentId: account.agentId,
    apiKey: account.apiKey,
    policy: { shareToolOutcomes: true, shareRawTraces: false },
    collector: { host: "127.0.0.1", port: 0, token: "private-local-token" },
    adapters: {
      claudeCode: {
        enabled: true,
        clientVersion: "1.0.77",
        environment: "macos-arm64",
        tools: {
          mcp__github__search_repositories: {
            toolRegistry: "mcp",
            toolId: "io.github.example/github-mcp",
            toolVersion: "3.2.0",
            authMode: "oauth-pkce",
            operation: "repository-search",
          },
        },
      },
      codex: {
        enabled: true,
        clientVersion: "0.145.0",
        environment: "macos-arm64",
        tools: { exec_command: { toolRegistry: "github", toolId: "io.agentwex/codex-exec", toolVersion: "1.0.0", authMode: "none", operation: "repository-check" } },
      },
      geminiCli: {
        enabled: true,
        clientVersion: "0.3.0",
        environment: "macos-arm64",
        tools: { run_shell_command: { toolRegistry: "github", toolId: "io.agentwex/gemini-shell", toolVersion: "1.1.0", authMode: "none", operation: "repository-check" } },
      },
      bernstein: {
        enabled: true,
        clientVersion: "3.12.0",
        environment: "macos-arm64",
        tools: { repository_migration: { toolRegistry: "github", toolId: "io.agentwex/repository-migration", toolVersion: "1.0.0", authMode: "none", operation: "repository-migration" } },
      },
    },
    pollSeconds: 60,
  });
  node = await runDaemon(configPath);
  const port = node.server.address().port;
  const payload = JSON.stringify({ spans: [toolSpan({ traceId: "authenticated-trace", outcome: "success" })] });
  const unauthorized = await fetch(`http://127.0.0.1:${port}/v1/traces`, { method: "POST", headers: { "content-type": "application/json" }, body: payload });
  assert.equal(unauthorized.status, 401);
  const authorized = await fetch(`http://127.0.0.1:${port}/v1/traces`, {
    method: "POST",
    headers: { "content-type": "application/json", authorization: "Bearer private-local-token" },
    body: payload,
  });
  assert.equal(authorized.status, 202);
  assert.equal((await authorized.json()).submitted, 1);

  const claudeLog = JSON.stringify({ resourceLogs: [{ scopeLogs: [{ logRecords: [{
    timeUnixNano: "1786870800000000000",
    body: { stringValue: "PRIVATE RESULT" },
    attributes: [
      { key: "event.name", value: { stringValue: "tool_result" } },
      { key: "tool_name", value: { stringValue: "mcp__github__search_repositories" } },
      { key: "tool_use_id", value: { stringValue: "private-tool-use-id" } },
      { key: "success", value: { stringValue: "true" } },
    ],
  }] }] }] });
  const logResponse = await fetch(`http://127.0.0.1:${port}/v1/logs`, {
    method: "POST",
    headers: { "content-type": "application/json", authorization: "Bearer private-local-token" },
    body: claudeLog,
  });
  assert.equal(logResponse.status, 202);
  assert.deepEqual(await logResponse.json(), { received: 1, submitted: 1, ignored: 0, rejected: 0, queriesOpened: 0 });

  const codexLog = JSON.stringify({ resourceLogs: [{ scopeLogs: [{ logRecords: [{
    observedTimeUnixNano: "1786870801000000000",
    attributes: [
      { key: "event.name", value: { stringValue: "codex.tool_result" } },
      { key: "tool_name", value: { stringValue: "exec_command" } },
      { key: "call_id", value: { stringValue: "codex-call" } },
      { key: "success", value: { stringValue: "true" } },
    ],
  }] }] }] });
  const codexResponse = await fetch(`http://127.0.0.1:${port}/v1/codex/logs`, {
    method: "POST",
    headers: { "content-type": "application/json", authorization: "Bearer private-local-token" },
    body: codexLog,
  });
  assert.equal(codexResponse.status, 202);
  assert.equal((await codexResponse.json()).submitted, 1);

  const bernsteinResponse = await fetch(`http://127.0.0.1:${port}/v1/bernstein/events`, {
    method: "POST",
    headers: { "content-type": "application/json", authorization: "Bearer private-local-token" },
    body: JSON.stringify({ schema: "agentwex.bernstein-hook.v0.1", events: [{ event: "task_completed", taskId: "private-bernstein-task", toolName: "repository_migration", observedAt: "2026-08-16T10:00:00.000Z", result_summary: "PRIVATE RESULT" }] }),
  });
  assert.equal(bernsteinResponse.status, 202);
  assert.equal((await bernsteinResponse.json()).submitted, 1);

  const geminiLog = JSON.stringify({ resourceLogs: [{ resource: { attributes: [{ key: "sessionId", value: { stringValue: "gemini-session" } }] }, scopeLogs: [{ logRecords: [{
    timeUnixNano: "1786870802000000000",
    attributes: [
      { key: "event.name", value: { stringValue: "gemini_cli.tool_call" } },
      { key: "function_name", value: { stringValue: "run_shell_command" } },
      { key: "success", value: { boolValue: true } },
    ],
  }] }] }] });
  const geminiResponse = await fetch(`http://127.0.0.1:${port}/gemini/private-local-token/v1/logs`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: geminiLog,
  });
  assert.equal(geminiResponse.status, 202);
  assert.equal((await geminiResponse.json()).submitted, 1);
});
