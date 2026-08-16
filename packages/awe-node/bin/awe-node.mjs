#!/usr/bin/env node
import { randomUUID } from "node:crypto";
import { access } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { resolve } from "node:path";
import { signup, getAccount, getLedger } from "../lib/client.mjs";
import { defaultConfigPath, readConfig, validateBaseUrl, writePrivateJson, writePrivateText } from "../lib/config.mjs";
import { runDaemon } from "../lib/daemon.mjs";
import { installBackgroundService } from "../lib/service.mjs";

const ownPath = fileURLToPath(import.meta.url);

function parseArgs(argv) {
  const [command = "help", ...rest] = argv;
  const options = {};
  const positional = [];
  for (let index = 0; index < rest.length; index += 1) {
    const value = rest[index];
    if (!value.startsWith("--")) { positional.push(value); continue; }
    const [rawKey, inline] = value.slice(2).split("=", 2);
    if (["no-service", "yes"].includes(rawKey)) options[rawKey] = true;
    else options[rawKey] = inline ?? rest[++index];
  }
  return { command, options, positional };
}

function printHelp() {
  process.stdout.write(`Agent Witness Exchange node\n\nCommands:\n  install [--url URL] [--name NAME] [--port 4318] [--no-service]\n  daemon [--config PATH]\n  status [--config PATH]\n  ledger [--config PATH]\n  routes [--config PATH]\n  doctor [--config PATH]\n\nInstall is the one explicit consent step. After it, the node submits only minimized tool-outcome receipts in the background.\n`);
}

async function localJson(config, path) {
  const response = await fetch(`http://${config.collector.host}:${config.collector.port}${path}`, {
    headers: { authorization: `Bearer ${config.collector.token}` },
    signal: AbortSignal.timeout(2_000),
  });
  if (!response.ok) throw new Error(`Local AWE node returned ${response.status}`);
  return response.json();
}

async function install(options) {
  const configPath = resolve(options.config ?? defaultConfigPath());
  try {
    await access(configPath);
    throw new Error(`AWE is already configured at ${configPath}. Remove it deliberately before creating a new identity.`);
  } catch (error) {
    if (error?.code !== "ENOENT") throw error;
  }
  const baseUrl = validateBaseUrl(options.url ?? process.env.AWE_EXCHANGE_URL ?? "https://agentwex.xyz");
  const port = Number(options.port ?? 4318);
  if (!Number.isInteger(port) || port < 1024 || port > 65535) throw new Error("Collector port must be an integer from 1024 to 65535");
  const displayName = options.name ?? `AWE node ${randomUUID().slice(0, 8)}`;
  const collectorToken = `awelocal_${randomUUID().replaceAll("-", "")}${randomUUID().replaceAll("-", "")}`;
  const account = await signup(baseUrl, {
    agent: { name: displayName, identityProvider: "custom", externalSubject: randomUUID() },
    participation: { heartbeatMinutes: 15, deliveryChannel: "nexus-api", dailyCreditSpendLimit: 10 },
  });
  const config = {
    schema: "minority-prophet.awe-node-config.v0.1",
    baseUrl,
    agentId: account.agentId,
    apiKey: account.apiKey,
    policy: { shareToolOutcomes: true, shareRawTraces: false, sharePrompts: false, shareToolArguments: false, shareToolResults: false },
    collector: { host: "127.0.0.1", port, token: collectorToken },
    pollSeconds: 60,
    createdAt: new Date().toISOString(),
  };
  await writePrivateJson(configPath, config);
  const environmentPath = resolve(configPath, "..", "otel.env");
  await writePrivateText(environmentPath,
    `export OTEL_EXPORTER_OTLP_ENDPOINT='http://127.0.0.1:${port}'\nexport OTEL_EXPORTER_OTLP_PROTOCOL='http/json'\nexport OTEL_EXPORTER_OTLP_HEADERS='authorization=Bearer ${collectorToken}'\n`);
  let service = null;
  if (!options["no-service"]) service = await installBackgroundService({ binPath: ownPath, configPath });
  process.stdout.write(`AWE node installed.\nIdentity: ${account.agentId}\nCollector: http://127.0.0.1:${port}/v1/traces\nCredits: ${account.creditBalance}\nRaw prompts, arguments, results, credentials, URLs, and trace IDs are not submitted.\n`);
  if (service) process.stdout.write(`Background service: ${service.label}\n`);
  else process.stdout.write(`Start locally: awe-node daemon --config ${configPath}\n`);
  process.stdout.write(`Connect an OTLP/HTTP JSON runtime without exposing the local token:\n  source ${environmentPath}\n`);
}

async function status(configPath) {
  const config = await readConfig(configPath);
  let local = null;
  try { local = await localJson(config, "/awe/status"); } catch {}
  const account = await getAccount(config);
  process.stdout.write(`${JSON.stringify({
    agentId: config.agentId,
    backgroundNode: local ? "running" : "not_reachable",
    creditBalance: account.creditBalance,
    pendingContributions: local?.pendingContributions?.length ?? null,
    openQueries: local?.queries?.filter((entry) => !entry.unlockedAt).length ?? null,
    availableRoutes: local?.routes?.length ?? null,
    authorityGranted: false,
  }, null, 2)}\n`);
}

async function routes(configPath) {
  const config = await readConfig(configPath);
  const result = await localJson(config, "/awe/routes");
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
}

async function ledger(configPath) {
  const config = await readConfig(configPath);
  process.stdout.write(`${JSON.stringify(await getLedger(config), null, 2)}\n`);
}

async function doctor(configPath) {
  const config = await readConfig(configPath);
  const checks = [];
  try { await getAccount(config); checks.push({ check: "exchange", status: "ok" }); }
  catch (error) { checks.push({ check: "exchange", status: "failed", error: error.message }); }
  try { await localJson(config, "/health"); checks.push({ check: "background_node", status: "ok" }); }
  catch (error) { checks.push({ check: "background_node", status: "failed", error: error.message }); }
  checks.push({ check: "privacy_policy", status: config.policy.shareRawTraces === false ? "ok" : "failed" });
  process.stdout.write(`${JSON.stringify({ checks }, null, 2)}\n`);
  if (checks.some((entry) => entry.status === "failed")) process.exitCode = 1;
}

async function main() {
  const { command, options } = parseArgs(process.argv.slice(2));
  const configPath = resolve(options.config ?? defaultConfigPath());
  if (command === "help" || command === "--help" || command === "-h") return printHelp();
  if (command === "install") return install(options);
  if (command === "daemon") return runDaemon(configPath);
  if (command === "status") return status(configPath);
  if (command === "ledger") return ledger(configPath);
  if (command === "routes") return routes(configPath);
  if (command === "doctor") return doctor(configPath);
  throw new Error(`Unknown command: ${command}`);
}

main().catch((error) => {
  process.stderr.write(`AWE node error: ${error.message}\n`);
  process.exitCode = 1;
});
