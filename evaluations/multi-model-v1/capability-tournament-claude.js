#!/usr/bin/env node
import { spawn } from 'node:child_process';
import { mkdtemp, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { CAPABILITY_RESPONSE_SCHEMA, capabilityPrompt } from './capability-tournament.js';
import { capabilityManifest, generateCapabilityWorlds, PROPOSITIONS } from './capability-worlds.js';

const PROJECT_ROOT = fileURLToPath(new URL('.', import.meta.url));
const RUNTIME = process.env.MP_CLAUDE_CAPABILITY_RUNTIME ?? join(PROJECT_ROOT, 'data', 'runtime', 'capability-tournament-v1-claude-extension-v1.1.json');
const MODELS = (process.env.MP_CLAUDE_CAPABILITY_MODELS ?? 'opus,sonnet,haiku').split(',').map((value) => value.trim()).filter(Boolean);

function runProcess({ args, input, cwd, timeoutMs = 600_000 }) {
  return new Promise((resolve, reject) => {
    const child = spawn('claude', args, { cwd, env: process.env, stdio: ['pipe', 'pipe', 'pipe'] });
    let stdout = '';
    let stderr = '';
    const timer = setTimeout(() => { child.kill('SIGTERM'); reject(new Error(`claude exceeded ${timeoutMs}ms`)); }, timeoutMs);
    child.stdout.setEncoding('utf8');
    child.stderr.setEncoding('utf8');
    child.stdout.on('data', (chunk) => { stdout += chunk; });
    child.stderr.on('data', (chunk) => { stderr += chunk; });
    child.on('error', (error) => { clearTimeout(timer); reject(error); });
    child.on('close', (code) => {
      clearTimeout(timer);
      if (code !== 0) reject(new Error(`claude exited ${code}: ${(stderr || stdout).slice(-1600)}`));
      else resolve({ stdout, stderr });
    });
    child.stdin.end(input);
  });
}

export function parseClaudeStream(stdout, requestedModel = '') {
  const events = stdout.split(/\r?\n/).filter(Boolean).flatMap((line) => { try { return [JSON.parse(line)]; } catch { return []; } });
  const result = [...events].reverse().find((event) => event.type === 'result');
  if (!result || result.is_error) throw new Error(result?.result || 'Claude stream has no successful result');
  const toolEvents = events
    .filter((event) => event.type === 'assistant')
    .flatMap((event) => event.message?.content ?? [])
    // Claude emits the response-schema transport itself as a synthetic
    // StructuredOutput tool block even when all built-in tools are disabled.
    // It is formatting, not contestant assistance, and is audited separately
    // by structured-output validation rather than counted as a tool request.
    .filter((block) => block.type === 'tool_use' && block.name !== 'StructuredOutput')
    .map((block) => ({ type: block.name, input: block.input ?? null }));
  const modelUsage = Object.entries(result.modelUsage ?? {});
  const selected = modelUsage.find(([key, value]) => key.toLowerCase().includes(requestedModel.toLowerCase()) || String(value.canonicalModel ?? '').toLowerCase().includes(requestedModel.toLowerCase())) ?? modelUsage.at(-1);
  const parsed = result.structured_output ?? JSON.parse(result.result);
  return {
    answers: parsed.answers,
    method_summary: parsed.method_summary,
    declared_tools: parsed.tools_used,
    tool_events: toolEvents,
    usage: {
      input_tokens: result.usage?.input_tokens ?? 0,
      output_tokens: result.usage?.output_tokens ?? 0,
      cache_read_input_tokens: result.usage?.cache_read_input_tokens ?? 0,
      cache_creation_input_tokens: result.usage?.cache_creation_input_tokens ?? 0
    },
    model_version: selected?.[1]?.canonicalModel ?? selected?.[0] ?? requestedModel,
    provider_cost_estimate_usd: Number.isFinite(result.total_cost_usd) ? result.total_cost_usd : null,
    provider_duration_ms: result.duration_ms ?? null,
    session_id: result.session_id ?? null
  };
}

async function runClaudeTrial({ model, lane, packet }) {
  const directory = await mkdtemp(join(tmpdir(), `mp-claude-${lane.toLowerCase()}-`));
  if (lane === 'B_TOOLS') await writeFile(join(directory, 'case.json'), `${JSON.stringify(packet)}\n`);
  const capability = lane === 'A_REASONING'
    ? 'Tool policy: reason directly. All tools are disabled. Any tool request invalidates the trial.'
    : 'Tool policy: you may choose Bash, Read, Write, WebSearch, or WebFetch. case.json is an exact copy of the inline case. Work only inside this isolated directory. Do not inspect files outside it.';
  const system = [
    'You are an isolated contestant in a frozen evidence-aggregation benchmark.',
    'Work only on the supplied case. Do not inspect outside context, contact anyone, or send messages.',
    'Return the required JSON. Do not assume any answer is privileged by its name or position.',
    'Describe the method you actually used without naming a method you did not use.'
  ].join(' ');
  const base = [
    '--print', '--model', model, '--effort', 'medium', '--safe-mode', '--no-chrome',
    '--disable-slash-commands', '--no-session-persistence', '--strict-mcp-config',
    '--mcp-config', '{"mcpServers":{}}', '--permission-mode', 'dontAsk',
    '--output-format', 'stream-json', '--verbose', '--json-schema', JSON.stringify(CAPABILITY_RESPONSE_SCHEMA),
    '--system-prompt', system
  ];
  const args = lane === 'A_REASONING'
    ? [...base, '--tools', '']
    : [...base, '--tools', 'Bash,Read,Write,WebSearch,WebFetch', '--allowed-tools', 'Bash,Read,Write,WebSearch,WebFetch'];
  const started = Date.now();
  try {
    const { stdout } = await runProcess({ args, input: `${capability}\n\n${capabilityPrompt(packet)}`, cwd: directory });
    const parsed = parseClaudeStream(stdout, model);
    if (lane === 'A_REASONING' && parsed.tool_events.length) throw new Error(`A emitted ${parsed.tool_events.length} forbidden tool request(s)`);
    return { status: 'COMPLETED', execution_ms: Date.now() - started, ...parsed };
  } finally {
    await rm(directory, { recursive: true, force: true });
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
    return { schema: 'mp-capability-claude-extension.v1', manifest, trials: [] };
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
      const result = await runClaudeTrial({ model, lane, packet: world.public_packet });
      Object.assign(trial, result, scoreAnswers(result.answers, world.hidden_key.reference), { status: 'COMPLETED' });
    } catch (error) {
      Object.assign(trial, { status: 'FAILED', error: String(error), correct: 0, decisions: PROPOSITIONS, exact: false });
    }
    trial.completed_at = new Date().toISOString();
    state.trials.push(trial);
    await saveState(state);
    console.log(JSON.stringify({ key, status: trial.status, correct: trial.correct, execution_ms: trial.execution_ms ?? null, tools: trial.tool_events?.length ?? 0 }));
  }
  await saveState(state);
}

if (process.argv[1] === fileURLToPath(import.meta.url)) main().catch((error) => { console.error(error); process.exitCode = 1; });
