import test from 'node:test';
import assert from 'node:assert/strict';
import { CONDITIONS } from './src/domain/constants.js';
import { assertNoHiddenLabels } from './src/domain/validation.js';
import { generateDevelopmentWorlds, generateMajorityCopyingWorld } from './worlds.js';
import { buildPrompt } from './prompts.js';
import { analyzeEvidence } from './mp.js';
import { parseModelResponse } from './parser.js';
import { DeterministicAdapter } from './providers.js';
import { scoreModel, scoreTrial } from './scoring.js';
import { pairedGain, wilsonInterval } from './stats.js';

test('world generation is deterministic and versioned', () => {
  const first = generateDevelopmentWorlds();
  const second = generateDevelopmentWorlds();
  assert.equal(first.length, 25);
  assert.deepEqual(first, second);
  assert.notEqual(generateMajorityCopyingWorld({ seed: 1 }).world_hash, generateMajorityCopyingWorld({ seed: 2 }).world_hash);
});

test('A/B/C use one world and only epistemic information changes', () => {
  const world = generateDevelopmentWorlds({ count: 1 })[0];
  const a = buildPrompt(world, CONDITIONS.BASELINE);
  const b = buildPrompt(world, CONDITIONS.PROVENANCE);
  const c = buildPrompt(world, CONDITIONS.MINORITY_PROPHET);
  assert.deepEqual(a.payload.world.claims.map((claim) => claim.claim_id), b.payload.world.claims.map((claim) => claim.claim_id));
  assert.equal(a.payload.world.provenance_edges, undefined);
  assert.ok(a.payload.world.claims.every((claim) => claim.direct_observation === undefined));
  assert.ok(a.payload.world.claims.every((claim) => claim.timestamp === undefined && claim.confidence === undefined));
  assert.ok(a.payload.world.sources.every((source) => source.prestige === undefined));
  assert.equal(a.payload.condition, undefined);
  assert.doesNotMatch(JSON.stringify(a.payload), /truth_root|false_root|source_copy|syndicat|field observer/i);
  assert.doesNotMatch(JSON.stringify(a.payload), /claim_00|source_00/i);
  assert.doesNotMatch(a.systemPrompt, /repetition|independent|provenance|lineage/i);
  assert.ok(b.payload.world.provenance_edges.length > 0);
  assert.equal(b.payload.minority_prophet_analysis, undefined);
  assert.ok(c.payload.minority_prophet_analysis.independent_roots.length >= 3);
  assert.equal(a.provenance_graph_hash, b.provenance_graph_hash);
  assertNoHiddenLabels(a.payload); assertNoHiddenLabels(b.payload); assertNoHiddenLabels(c.payload);
});

test('Minority Prophet returns structure and never a truth label', () => {
  const world = generateDevelopmentWorlds({ count: 1 })[0];
  const output = analyzeEvidence({ claims: world.claims, sources: world.sources, provenance_edges: world.provenance_edges });
  assert.ok(output.correlation_warnings.length);
  assert.equal(output.evidence_summary.independent_root_count, world.independent_roots.length);
  assert.doesNotMatch(JSON.stringify(output), /ground_truth|correct_answer|truth_relationship/);
});

test('response parsing preserves invalid formatting as parse failure', () => {
  assert.equal(parseModelResponse('not json').parse_success, false);
  const valid = { answer:'North',confidence:0.7,abstain:false,reasoning_summary:'brief',evidence_used:['claim_1'],independence_assessment:'unknown' };
  assert.deepEqual(parseModelResponse(JSON.stringify(valid)).parsed, valid);
});

test('provider interface normalizes deterministic adapter output', async () => {
  const world = generateDevelopmentWorlds({ count: 1 })[0];
  const prompt = buildPrompt(world, CONDITIONS.BASELINE);
  const result = await new DeterministicAdapter('majority-follower-v1').runModel({ ...prompt, seed: world.seed });
  assert.ok(result.provider_request_id);
  assert.ok(result.usage.input_tokens > 0);
  assert.equal(parseModelResponse(result.raw).parse_success, true);
});

test('scoring is transparent and paired gains are reproducible', () => {
  const world = generateDevelopmentWorlds({ count: 1 })[0];
  const yes = scoreTrial({ condition: CONDITIONS.BASELINE }, world, { parse_success:true,parsed:{ answer:world.ground_truth,confidence:0.9,abstain:false } });
  const no = scoreTrial({ condition: CONDITIONS.PROVENANCE }, world, { parse_success:true,parsed:{ answer:'wrong',confidence:0.8,abstain:false } });
  const invalid = scoreTrial({ condition: CONDITIONS.MINORITY_PROPHET }, world, { parse_success:false });
  assert.equal(yes.correct, true); assert.equal(no.correct, false); assert.equal(invalid.eligible, false);
  assert.deepEqual(wilsonInterval(5, 10), wilsonInterval(5, 10));
  assert.equal(pairedGain([yes], [{ ...yes, condition: CONDITIONS.PROVENANCE }]).gain, 0);
  assert.equal(scoreModel([yes,no,invalid]).by_condition[CONDITIONS.MINORITY_PROPHET].parse_failures, 1);
});
