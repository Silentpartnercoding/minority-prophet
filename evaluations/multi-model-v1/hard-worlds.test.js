import test from 'node:test';
import assert from 'node:assert/strict';
import { hardBenchmark } from './hard-benchmark.js';
import { generateHardWorlds, HARD_SCENARIO_FAMILIES } from './hard-worlds.js';
import { analyzeEvidence } from './mp.js';
import { buildPrompt } from './prompts.js';
import { scoreTrial } from './scoring.js';
import { CONDITIONS } from './src/domain/constants.js';

test('hard gauntlet is deterministic, diverse, and larger than the pilot', () => {
  const first = generateHardWorlds();
  const second = generateHardWorlds();
  assert.deepEqual(first, second);
  assert.equal(first.length, 8);
  assert.deepEqual([...new Set(first.map((world) => world.scenario_family))], [...HARD_SCENARIO_FAMILIES]);
  assert.equal(first.filter((world) => world.expected_disposition === 'ABSTAIN').length, 3);
  assert.equal(hardBenchmark().manifest.expected_worlds, 8);
});

test('A hides structured evidence while B and C expose the same declared record', () => {
  for (const world of generateHardWorlds()) {
    const a = buildPrompt(world, CONDITIONS.BASELINE).payload;
    const b = buildPrompt(world, CONDITIONS.PROVENANCE).payload;
    const c = buildPrompt(world, CONDITIONS.MINORITY_PROPHET).payload;
    assert.equal(a.world.evidence_context, undefined);
    assert.equal(a.world.provenance_edges, undefined);
    assert.ok(a.world.sources.every((source) => source.control_domain_id === undefined && source.observation_id === undefined));
    assert.ok(a.world.claims.every((claim) => claim.timestamp === undefined && claim.parent_claim_ids === undefined));
    assert.deepEqual(b.world, c.world);
    assert.ok(c.minority_prophet_analysis);
    assert.doesNotMatch(JSON.stringify(c), /ground_truth|truth_relationship|correct_answer/);
  }
});

test('gauntlet includes attacks that fool root counting and require abstention', () => {
  const worlds = generateHardWorlds();
  for (const family of ['shared_control_roots', 'observation_laundering', 'stale_override', 'revoked_authority']) {
    const world = worlds.find((candidate) => candidate.scenario_family === family);
    const analysis = analyzeEvidence({ claims: world.claims, sources: world.sources, provenance_edges: world.provenance_edges, context: world.evidence_context });
    assert.notEqual(analysis.recommended_attention[0].asserted_answer, world.ground_truth, family);
  }
  for (const world of worlds.filter((candidate) => candidate.expected_disposition === 'ABSTAIN')) {
    const scored = scoreTrial({ condition: CONDITIONS.MINORITY_PROPHET }, world, { parse_success: true, parsed: { answer: '', confidence: 0.5, abstain: true } });
    assert.equal(scored.correct, true, world.scenario_family);
    assert.equal(scored.abstention_appropriate, true, world.scenario_family);
  }
});

test('circular-only evidence has no independent root and is flagged', () => {
  const world = generateHardWorlds().find((candidate) => candidate.scenario_family === 'circular_only');
  const analysis = analyzeEvidence({ claims: world.claims, sources: world.sources, provenance_edges: world.provenance_edges, context: world.evidence_context });
  assert.equal(analysis.independent_roots.length, 0);
  assert.equal(analysis.uncertainty.circularity_detected, true);
});
