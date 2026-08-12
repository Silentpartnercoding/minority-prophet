#!/usr/bin/env node
import { spawn } from 'node:child_process';
import { chmod, copyFile, mkdtemp, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { capabilityManifest, generateCapabilityWorlds, PROPOSITIONS } from './capability-worlds.js';

const PROJECT_ROOT = fileURLToPath(new URL('.', import.meta.url));
const RUNTIME = process.env.MP_CAPABILITY_RUNTIME ?? join(PROJECT_ROOT, 'data', 'runtime', 'capability-tournament-v1.json');
const MODELS = (process.env.MP_CAPABILITY_MODELS ?? 'gpt-5.6-sol,gpt-5.6-terra,gpt-5.6-luna').split(',').map((value) => value.trim()).filter(Boolean);
const PRICE_PER_MILLION = Object.freeze({
  'gpt-5.6-sol': { input: 5, output: 30 },
  'gpt-5.6-terra': { input: 2.5, output: 15 },
  'gpt-5.6-luna': { input: 1, output: 6 }
});

export const CAPABILITY_RESPONSE_SCHEMA = Object.freeze({
  type: 'object',
  additionalProperties: false,
  properties: {
    answers: { type: 'array', minItems: PROPOSITIONS, maxItems: PROPOSITIONS, items: { type: 'string', enum: ['A', 'B', 'ABSTAIN'] } },
    method_summary: { type: 'string', minLength: 1, maxLength: 800 },
    tools_used: { type: 'array', maxItems: 32, items: { type: 'string', maxLength: 120 } }
  },
  required: ['answers', 'method_summary', 'tools_used']
});

const BENCHMARK_AGENT_INSTRUCTIONS = [
  '# Isolated benchmark contestant',
  '',
  '- Work only on the supplied benchmark case.',
  '- Do not send handoffs, notifications, messages, or status reports.',
  '- Do not inspect files outside the supplied contestant workspace.'
].join('\n');

function runProcess({ args, input, cwd, env = process.env, timeoutMs = 600_000 }) {
  return new Promise((resolve, reject) => {
    const child = spawn('codex', args, { cwd, env, stdio: ['pipe', 'pipe', 'pipe'] });
    let stdout = '';
    let stderr = '';
    const timer = setTimeout(() => { child.kill('SIGTERM'); reject(new Error(`codex exceeded ${timeoutMs}ms`)); }, timeoutMs);
    child.stdout.setEncoding('utf8');
    child.stderr.setEncoding('utf8');
    child.stdout.on('data', (chunk) => { stdout += chunk; });
    child.stderr.on('data', (chunk) => { stderr += chunk; });
    child.on('error', (error) => { clearTimeout(timer); reject(error); });
    child.on('close', (code) => {
      clearTimeout(timer);
      if (code !== 0) reject(new Error(`codex exited ${code}: ${(stderr || stdout).slice(-1600)}`));
      else resolve({ stdout, stderr });
    });
    child.stdin.end(input);
  });
}

export function parseEvents(stdout) {
  const events = stdout.split(/\r?\n/).filter(Boolean).flatMap((line) => { try { return [JSON.parse(line)]; } catch { return []; } });
  const completed = [...events].reverse().find((event) => event.type === 'turn.completed');
  // A command is emitted once when it starts and once when it completes. Count
  // completed lifecycle records only so telemetry reflects actual tool calls.
  const items = events.filter((event) => event.type === 'item.completed').map((event) => event.item).filter(Boolean);
  const tools = items.filter((item) => ['command_execution', 'file_change', 'mcp_tool_call', 'web_search'].includes(item.type));
  return {
    usage: completed?.usage ?? {},
    tool_events: tools.map((item) => ({ type: item.type, command: item.command ?? null, query: item.query ?? null })),
    thread_id: events.find((event) => event.type === 'thread.started')?.thread_id ?? null
  };
}

export function listPriceProxy(model, usage) {
  const price = PRICE_PER_MILLION[model];
  if (!price || !Number.isFinite(usage.input_tokens) || !Number.isFinite(usage.output_tokens)) return null;
  const cached = Math.min(usage.input_tokens, Math.max(0, usage.cached_input_tokens ?? 0));
  const cacheWrite = Math.min(usage.input_tokens - cached, Math.max(0, usage.cache_write_input_tokens ?? 0));
  const uncached = usage.input_tokens - cached - cacheWrite;
  const longContext = usage.input_tokens > 272_000;
  const inputMultiplier = longContext ? 2 : 1;
  const outputMultiplier = longContext ? 1.5 : 1;
  const inputCost = (uncached * price.input + cached * price.input * 0.1 + cacheWrite * price.input * 1.25) * inputMultiplier;
  const outputCost = usage.output_tokens * price.output * outputMultiplier;
  return (inputCost + outputCost) / 1_000_000;
}

export function capabilityPrompt(packet) {
  return [
    'You are a contestant in a frozen evidence-aggregation benchmark.',
    'Use only the supplied case. Return the required JSON. Do not assume any answer is privileged by its name or position.',
    'Describe the method you actually used without naming a method you did not use.',
    JSON.stringify(packet)
  ].join('\n\n');
}

async function runCodexTrial({ model, lane, packet }) {
  const directory = await mkdtemp(join(tmpdir(), `mp-${lane.toLowerCase()}-`));
  const codexHome = await mkdtemp(join(tmpdir(), 'mp-codex-home-'));
  const schemaPath = join(directory, 'schema.json');
  const outputPath = join(directory, 'final.json');
  const sourceCodexHome = process.env.CODEX_HOME ?? join(process.env.HOME, '.codex');
  await copyFile(join(sourceCodexHome, 'auth.json'), join(codexHome, 'auth.json'));
  await chmod(join(codexHome, 'auth.json'), 0o600);
  await writeFile(join(codexHome, 'AGENTS.override.md'), `${BENCHMARK_AGENT_INSTRUCTIONS}\n`);
  await writeFile(schemaPath, `${JSON.stringify(CAPABILITY_RESPONSE_SCHEMA)}\n`);
  if (lane === 'B_TOOLS') await writeFile(join(directory, 'case.json'), `${JSON.stringify(packet)}\n`);
  const capability = lane === 'A_REASONING'
    ? 'Tool policy: reason directly. Do not call shell, files, web, retrieval, MCP, or any tool. Any tool event invalidates the trial.'
    : 'Tool policy: you may use live web search and the shell in this isolated directory, write scripts, calculate, use available packages, or install a method if the environment permits it. case.json is an exact copy of the inline case. Do not inspect files outside this directory.';
  const base = ['exec', '--ephemeral', '--ignore-user-config', '--ignore-rules', '--strict-config', '--skip-git-repo-check', '--cd', directory, '--model', model, '-c', 'project_doc_max_bytes=0', '-c', 'shell_environment_policy.exclude=["CODEX_HOME","CODEX_THREAD_ID","CODEX_INTERNAL_ORIGINATOR_OVERRIDE"]', '-c', 'model_reasoning_effort="medium"', '--output-schema', schemaPath, '--output-last-message', outputPath, '--json', '-'];
  const args = lane === 'A_REASONING'
    ? [...base.slice(0, 1), '--sandbox', 'read-only', ...base.slice(1)]
    : ['--search', '--ask-for-approval', 'never', ...base.slice(0, 1), '--sandbox', 'workspace-write', ...base.slice(1)];
  const started = Date.now();
  try {
    const env = { ...process.env, CODEX_HOME: codexHome };
    const { stdout } = await runProcess({ args, input: `${capability}\n\n${capabilityPrompt(packet)}`, cwd: directory, env });
    const telemetry = parseEvents(stdout);
    if (lane === 'A_REASONING' && telemetry.tool_events.length) throw new Error(`A emitted ${telemetry.tool_events.length} forbidden tool events`);
    const parsed = JSON.parse(await readFile(outputPath, 'utf8'));
    return {
      status: 'COMPLETED', answers: parsed.answers, method_summary: parsed.method_summary, declared_tools: parsed.tools_used,
      execution_ms: Date.now() - started, ...telemetry, list_price_proxy_usd: listPriceProxy(model, telemetry.usage)
    };
  } finally {
    await rm(directory, { recursive: true, force: true });
    await rm(codexHome, { recursive: true, force: true });
  }
}

function scoreAnswers(answers, reference) {
  if (!Array.isArray(answers) || answers.length !== reference.length) return { correct: 0, decisions: reference.length, exact: false };
  const correct = answers.filter((answer, index) => answer === reference[index]).length;
  return { correct, decisions: reference.length, exact: correct === reference.length };
}

async function loadState(manifest) {
  try {
    const state = JSON.parse(await readFile(RUNTIME, 'utf8'));
    if (state.manifest.manifest_hash !== manifest.manifest_hash) throw new Error('runtime manifest differs from frozen manifest');
    return state;
  } catch (error) {
    if (error.code !== 'ENOENT') throw error;
    return { schema: 'mp-capability-run.v1', manifest, trials: [] };
  }
}

async function saveState(state) {
  await mkdir(join(PROJECT_ROOT, 'data', 'runtime'), { recursive: true });
  await writeFile(RUNTIME, `${JSON.stringify(state, null, 2)}\n`);
}

async function main() {
  const worlds = generateCapabilityWorlds();
  const manifest = capabilityManifest(worlds);
  if (manifest.manifest_hash !== 'sha256:e65d843669b1a0ead2a468ed8f05a44f3d74cf6e8184c05d2f697e427a8ec4ff') throw new Error(`manifest is not frozen: ${manifest.manifest_hash}`);
  const state = await loadState(manifest);
  for (const model of MODELS) for (const lane of ['A_REASONING', 'B_TOOLS']) for (const world of worlds) {
    const key = `${model}:${lane}:${world.public_packet.case_id}`;
    if (state.trials.some((trial) => trial.key === key)) continue;
    const trial = { key, model, lane, case_id: world.public_packet.case_id, packet_hash: world.public_packet.packet_hash, started_at: new Date().toISOString() };
    try {
      const result = await runCodexTrial({ model, lane, packet: world.public_packet });
      Object.assign(trial, result, scoreAnswers(result.answers, world.hidden_key.reference), { status: 'COMPLETED' });
    } catch (error) {
      Object.assign(trial, { status: 'FAILED', error: String(error), correct: 0, decisions: PROPOSITIONS, exact: false });
    }
    trial.completed_at = new Date().toISOString();
    state.trials.push(trial);
    await saveState(state);
    console.log(JSON.stringify({ key, status: trial.status, correct: trial.correct, execution_ms: trial.execution_ms ?? null, tools: trial.tool_events?.length ?? 0 }));
  }
  for (const trial of state.trials) {
    if (trial.status === 'COMPLETED') trial.list_price_proxy_usd = listPriceProxy(trial.model, trial.usage ?? {});
  }
  await saveState(state);
  const summary = {};
  for (const trial of state.trials) {
    const key = `${trial.model}:${trial.lane}`;
    summary[key] ??= { correct: 0, decisions: 0, exact_cases: 0, cases: 0, execution_ms: 0, input_tokens: 0, output_tokens: 0, tool_events: 0, list_price_proxy_usd: 0, failures: 0 };
    const row = summary[key];
    row.correct += trial.correct; row.decisions += trial.decisions; row.exact_cases += Number(trial.exact); row.cases += 1;
    row.execution_ms += trial.execution_ms ?? 0; row.input_tokens += trial.usage?.input_tokens ?? 0; row.output_tokens += trial.usage?.output_tokens ?? 0;
    row.tool_events += trial.tool_events?.length ?? 0; row.list_price_proxy_usd += trial.list_price_proxy_usd ?? 0; row.failures += Number(trial.status !== 'COMPLETED');
  }
  console.log(JSON.stringify({ manifest, summary }, null, 2));
}

if (process.argv[1] === fileURLToPath(import.meta.url)) main().catch((error) => { console.error(error); process.exitCode = 1; });
