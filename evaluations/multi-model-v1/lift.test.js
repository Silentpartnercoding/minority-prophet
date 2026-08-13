import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { CONDITIONS } from './src/domain/constants.js';
import { conditionOrderFor, CONDITION_PERMUTATIONS, liftBenchmark, LIFT_MODEL_GRID } from './lift-benchmark.js';
import { liftBenchmarkV11 } from './lift-benchmark-v11.js';
import { runLiftBenchmark } from './lift-pipeline.js';
import { buildLiftPrompt } from './lift-prompts.js';
import { executeMinorityProphetTool, MP_TOOL_CONTRACT_HASH } from './mp-tool-v2.js';
import { JsonStore } from './store.js';

function toolInput(world) {
  const b = buildLiftPrompt(world, CONDITIONS.PROVENANCE).payload.world;
  return { claims: b.claims, sources: b.sources, provenance_edges: b.provenance_edges, context: b.evidence_context };
}

test('lift benchmark is deterministic, counterbalanced, and has the preregistered shape', () => {
  const first = liftBenchmark();
  const second = liftBenchmark();
  assert.deepEqual(first, second);
  assert.equal(first.worlds.length, 32);
  assert.equal(new Set(first.worlds.map((world) => world.scenario_family)).size, 8);
  assert.equal(first.worlds.filter((world) => world.expected_disposition === 'ANSWER').length, 24);
  assert.equal(first.worlds.filter((world) => world.expected_disposition === 'ABSTAIN').length, 8);
  assert.ok(first.worlds.filter((world) => world.expected_disposition === 'ANSWER').every((world) => world.metadata.false_majority));
  for (const model of LIFT_MODEL_GRID) {
    const orders = first.worlds.map((world) => conditionOrderFor(world, { provider: model.provider, model: model.requested_model }));
    assert.deepEqual(new Set(orders.map((order) => order.join('|'))), new Set(CONDITION_PERMUTATIONS.map((order) => order.join('|'))));
    const positions = Object.fromEntries([CONDITIONS.BASELINE, CONDITIONS.PROVENANCE, CONDITIONS.MINORITY_PROPHET].map((condition) => [condition, [0, 0, 0]]));
    for (const order of orders) order.forEach((condition, index) => { positions[condition][index] += 1; });
    assert.ok(Object.values(positions).flat().every((count) => count >= 10 && count <= 12));
  }
});

test('v1.1 changes transport protocol without changing any benchmark world', () => {
  const original = liftBenchmark();
  const revised = liftBenchmarkV11();
  assert.notEqual(revised.manifest.manifest_hash, original.manifest.manifest_hash);
  assert.equal(revised.manifest.predecessor_manifest_hash, original.manifest.manifest_hash);
  assert.equal(revised.manifest.response_transport.provider_structured_output_enforcement, false);
  assert.equal(revised.manifest.response_transport.schema_repair_model, false);
  assert.deepEqual(revised.worlds, original.worlds);
});

test('B and C differ only by the deterministic Minority Prophet receipt', () => {
  for (const world of liftBenchmark().worlds) {
    const a = buildLiftPrompt(world, CONDITIONS.BASELINE);
    const b = buildLiftPrompt(world, CONDITIONS.PROVENANCE);
    const c = buildLiftPrompt(world, CONDITIONS.MINORITY_PROPHET);
    assert.equal(a.system_prompt_hash, b.system_prompt_hash);
    assert.equal(b.system_prompt_hash, c.system_prompt_hash);
    assert.equal(b.epistemic_base_hash, c.epistemic_base_hash);
    assert.deepEqual(b.payload, { instruction: c.payload.instruction, world: c.payload.world, response_schema: c.payload.response_schema });
    assert.equal(a.payload.world.provenance_edges, undefined);
    assert.equal(a.payload.world.evidence_context, undefined);
    assert.equal(b.payload.minority_prophet_tool_receipt, undefined);
    assert.equal(c.payload.minority_prophet_tool_receipt.contract_hash, MP_TOOL_CONTRACT_HASH);
    assert.deepEqual(a.tools, []);
    assert.deepEqual(b.tools, []);
    assert.deepEqual(c.tools, []);
  }
});

test('MP receipt is deterministic, closed to hidden labels, and structurally informative', () => {
  for (const world of liftBenchmark().worlds) {
    const input = toolInput(world);
    const first = executeMinorityProphetTool(input);
    assert.deepEqual(first, executeMinorityProphetTool(input));
    const serialized = JSON.stringify(first);
    assert.doesNotMatch(serialized, /ground_truth|correct_answer|truth_relationship|recommended_answer/i);
    if (world.expected_disposition === 'ANSWER') {
      const ranked = [...first.support_by_answer].sort((left, right) => right.current_evidence_unit_count - left.current_evidence_unit_count);
      assert.equal(ranked[0].asserted_answer, world.ground_truth);
      assert.ok(ranked[0].current_evidence_unit_count > ranked[1].current_evidence_unit_count);
    } else {
      assert.ok(first.abstention_signals.length > 0);
    }
  }
  const world = liftBenchmark().worlds[0];
  assert.throws(() => executeMinorityProphetTool({ ...toolInput(world), ground_truth: world.ground_truth }), /not allowed/);
});

test('lift pipeline preserves a parse failure and makes only the preregistered retry', async () => {
  const directory = await mkdtemp(join(tmpdir(), 'mp-lift-test-'));
  try {
    const full = liftBenchmark();
    const benchmark = { manifest: full.manifest, worlds: full.worlds.slice(0, 1) };
    const calls = new Map();
    const adapter = {
      provider: 'test-provider', model: 'test-model', version: 'test-v1',
      async runModel(request) {
        const count = (calls.get(request.condition) ?? 0) + 1;
        calls.set(request.condition, count);
        return {
          raw: count === 1 ? 'not-json' : { answer: benchmark.worlds[0].ground_truth, confidence: 0.5, abstain: false, reasoning_summary: 'structured retry', evidence_used: [], independence_assessment: 'not stated' },
          provider_request_id: `${request.condition}:${count}`, usage: {}, execution_ms: 1, model_version: 'test-v1'
        };
      }
    };
    const store = await new JsonStore(join(directory, 'state.json')).load();
    const run = await runLiftBenchmark({ store, benchmark, adapters: [adapter], runId: 'lift-retry-test', settings: { temperature: 0, top_p: 1, max_tokens: 500, provider_concurrency: 1, maximum_attempts_per_cell: 2, retry_parse_failures: true, tool_configuration: {} } });
    assert.equal(run.status, 'COMPLETED');
    assert.equal(store.filter('trials', (trial) => trial.status === 'FAILED').length, 3);
    assert.equal(store.filter('trials', (trial) => trial.status === 'COMPLETED').length, 3);
    assert.equal(store.all('raw_responses').length, 6);
    assert.ok([...calls.values()].every((count) => count === 2));
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
});
