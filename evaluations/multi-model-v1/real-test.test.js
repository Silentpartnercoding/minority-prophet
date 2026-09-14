import test from 'node:test';
import assert from 'node:assert/strict';
import { realTestWorlds } from './real-test-worlds.js';
import { buildRealTestPrompt, REAL_CONDITIONS } from './real-test-prompts.js';

test('real test is balanced between false-majority and correct-majority answerable worlds', () => {
  const worlds = realTestWorlds();
  const answerable = worlds.filter((world) => world.expected_disposition === 'ANSWER');
  const classify = (world) => {
    const counts = new Map();
    for (const claim of world.claims) counts.set(claim.asserted_answer, (counts.get(claim.asserted_answer) ?? 0) + 1);
    const majority = [...counts].sort((left, right) => right[1] - left[1])[0][0];
    return majority === world.ground_truth ? 'correct' : 'wrong';
  };
  assert.equal(answerable.filter((world) => classify(world) === 'correct').length, 12);
  assert.equal(answerable.filter((world) => classify(world) === 'wrong').length, 12);
  assert.equal(worlds.filter((world) => world.expected_disposition === 'ABSTAIN').length, 4);
});

test('provenance, neutral index, and MP share an identical epistemic base without hidden labels', () => {
  for (const world of realTestWorlds()) {
    const prompts = [
      buildRealTestPrompt(world, REAL_CONDITIONS.PROVENANCE),
      buildRealTestPrompt(world, REAL_CONDITIONS.NEUTRAL_INDEX),
      buildRealTestPrompt(world, REAL_CONDITIONS.MINORITY_PROPHET)
    ];
    assert.equal(new Set(prompts.map((prompt) => prompt.epistemic_base_hash)).size, 1);
    for (const prompt of prompts) {
      assert.doesNotMatch(prompt.messages[0].content, /ground_truth|truth_relationship|correct_answer/);
    }
  }
});

test('neutral control contains no aggregation, recommendation, verdict, or MP receipt', () => {
  const prompt = buildRealTestPrompt(realTestWorlds()[0], REAL_CONDITIONS.NEUTRAL_INDEX);
  const serialized = prompt.messages[0].content;
  assert.match(serialized, /neutral_root_index/);
  assert.doesNotMatch(serialized, /minority_prophet_tool_receipt|support_by_answer|recommended|verdict|evidence_unit_count/);
});
