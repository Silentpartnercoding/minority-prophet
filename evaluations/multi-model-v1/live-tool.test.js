import assert from 'node:assert/strict';
import { mkdtemp, rm } from 'node:fs/promises';
import test from 'node:test';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { handleMcpRequest } from './mp-mcp-server.js';
import { liftBenchmarkV11 } from './lift-benchmark-v11.js';
import { liveToolBenchmark } from './live-tool-benchmark.js';
import { buildLiveToolPrompt, LIVE_TOOL_CONDITIONS } from './live-tool-prompts.js';
import { runLiveToolBenchmark } from './live-tool-runner.js';
import { MP_TOOL_CONTRACT_HASH, MP_TOOL_DEFINITION } from './mp-tool-v2.js';
import { JsonStore } from './store.js';
import { hashObject } from './src/lib/hash.js';

function recursiveKeys(value) {
  if (Array.isArray(value)) return value.flatMap(recursiveKeys);
  if (!value || typeof value !== 'object') return [];
  return Object.entries(value).flatMap(([key, child]) => [key, ...recursiveKeys(child)]);
}

test('MCP server exposes only the pinned read-only Minority Prophet tool', () => {
  const initialized = handleMcpRequest({ jsonrpc: '2.0', id: 1, method: 'initialize', params: { protocolVersion: '2025-06-18' } });
  assert.equal(initialized.result.protocolVersion, '2025-06-18');
  const listed = handleMcpRequest({ jsonrpc: '2.0', id: 2, method: 'tools/list', params: {} });
  assert.equal(listed.result.tools.length, 1);
  assert.equal(listed.result.tools[0].name, MP_TOOL_DEFINITION.name);
  assert.equal(listed.result.tools[0].annotations.readOnlyHint, true);
});

test('live MCP call returns a receipt without a ground-truth answer', () => {
  const world = liftBenchmarkV11().worlds[0];
  const prompt = buildLiveToolPrompt(world, LIVE_TOOL_CONDITIONS.REQUIRED);
  const called = handleMcpRequest({ jsonrpc: '2.0', id: 3, method: 'tools/call', params: { name: MP_TOOL_DEFINITION.name, arguments: prompt.payload.tool_input } });
  assert.equal(called.result.isError, false);
  assert.equal(called.result.structuredContent.contract_hash, MP_TOOL_CONTRACT_HASH);
  const keys = recursiveKeys(called.result).map((key) => key.toLowerCase());
  assert.equal(keys.some((key) => ['hidden', 'ground_truth', 'correct_answer', 'truth_label'].includes(key)), false);
});

test('required and optional prompts expose the same provenance world and exact tool input', () => {
  const world = liftBenchmarkV11().worlds[4];
  const optional = buildLiveToolPrompt(world, LIVE_TOOL_CONDITIONS.OPTIONAL);
  const required = buildLiveToolPrompt(world, LIVE_TOOL_CONDITIONS.REQUIRED);
  assert.deepEqual(optional.payload.world, required.payload.world);
  assert.deepEqual(optional.payload.tool_input, required.payload.tool_input);
  assert.equal(optional.expected_tool_input_hash, required.expected_tool_input_hash);
  const keys = recursiveKeys(optional.payload).map((key) => key.toLowerCase());
  assert.equal(keys.some((key) => ['hidden', 'ground_truth', 'correct_answer', 'truth_label'].includes(key)), false);
});

test('live-tool runner persists an exact-call completed cell', async () => {
  const directory = await mkdtemp(join(tmpdir(), 'mp-live-runner-test-'));
  try {
    const full = liveToolBenchmark();
    const benchmark = { manifest: { ...full.manifest, benchmark_version: 'live-test', world_count: 1, expected_worlds: 1, world_hashes: full.manifest.world_hashes.slice(0, 1) }, worlds: full.worlds.slice(0, 1) };
    const world = benchmark.worlds[0];
    const adapter = {
      provider: 'fake-live-mcp', model: 'fake-model', version: 'fake-v1',
      async runModel(request) {
        const payload = JSON.parse(request.messages[0].content);
        const call = handleMcpRequest({ jsonrpc: '2.0', id: 1, method: 'tools/call', params: { name: MP_TOOL_DEFINITION.name, arguments: payload.tool_input } });
        return {
          raw: { answer: world.ground_truth, confidence: 0.9, abstain: false, reasoning_summary: 'Used the receipt.', evidence_used: [], independence_assessment: 'Independent roots inspected.' },
          provider_request_id: 'fake-request', usage: { input_tokens: 10, output_tokens: 5, cached_tokens: 0 }, cost_usd: 0,
          execution_ms: 12, model_version: 'fake-v1', mcp_initialize_count: 1, mcp_tools_list_count: 1,
          mp_tool_call_count: 1, mp_tool_success_count: 1, mp_tool_execution_ms: 0.1,
          mp_tool_input_hash: request.expectedToolInputHash,
          mp_tool_output_hash: hashObject(call.result.structuredContent.output),
          mcp_events: [
            { event: 'initialize', timestamp: '2026-08-11T00:00:00.000Z' },
            { event: 'tool_call', success: true, timestamp: '2026-08-11T00:00:00.005Z' }
          ]
        };
      }
    };
    const store = await new JsonStore(join(directory, 'state.json')).load();
    const run = await runLiveToolBenchmark({ store, benchmark, adapters: [adapter], runId: 'live-runner-test', settings: { max_tokens: 500, provider_concurrency: 1, tool_configuration: {} }, protocolCommit: 'a'.repeat(40) });
    assert.equal(run.status, 'COMPLETED');
    assert.equal(run.completed_trials, 1);
    const trial = store.all('trials')[0];
    assert.equal(trial.live_tool.mp_tool_success_count, 1);
    assert.equal(trial.live_tool.mcp_startup_to_call_ms, 5);
    assert.equal(trial.score.correct, true);
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
});
