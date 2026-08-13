import assert from 'node:assert/strict';
import test from 'node:test';
import { decideFromInferredRoots, inferProvenance, inferProvenanceExp008Comparator } from './provenance-inference.js';
import { generateDiscoveryWorlds, publicDiscoveryWorld } from './provenance-discovery-worlds.js';
import { scoreProvenance } from './provenance-discovery-scoring.js';
import { discoveryJobs } from './provenance-discovery-benchmark.js';

test('discovery worlds are deterministic and hide all lineage keys', () => {
  const a = generateDiscoveryWorlds(); const b = generateDiscoveryWorlds();
  assert.deepEqual(a, b); assert.equal(a.length, 24);
  for (const world of a) {
    const encoded = JSON.stringify(publicDiscoveryWorld(world));
    assert.doesNotMatch(encoded, /parent_by_document|root_by_document|ground_truth|asserted_answer/);
  }
});

test('candidate collapses supported signals and routes unsupported cases to semantic review', () => {
  const worlds = generateDiscoveryWorlds();
  for (const world of worlds) {
    const packet = publicDiscoveryWorld(world);
    const inference = inferProvenance(packet);
    const score = scoreProvenance(world, inference.inferred_root_by_document);
    const decision = decideFromInferredRoots(packet, inference);
    if (['generic_boilerplate', 'opaque_paraphrase'].includes(world.family)) {
      assert.equal(inference.accepted_links.length, 0);
      assert.equal(score.pairwise_recall, 0);
      assert.equal(decision.abstain, true);
      assert.equal(decision.abstention_reason, 'no_observable_lineage');
      assert.equal(inference.next_action, 'semantic_review_required');
    } else {
      assert.equal(inference.accepted_links.length, 7);
      assert.equal(score.pairwise_f1, 1);
      assert.equal(decision.abstain, false);
      assert.equal(decision.answer, world.hidden.ground_truth);
      if (world.family === 'deceptive_citation') {
        assert.ok(inference.provenance_warnings.length > 0);
        assert.equal(inference.next_action, 'integrity_review_required');
      } else assert.equal(inference.next_action, 'auto_collapse');
    }
  }
});

test('EXP008 comparator is measured and does not silently replace the confidence gate', () => {
  for (const world of generateDiscoveryWorlds()) {
    const packet = publicDiscoveryWorld(world);
    const comparator = inferProvenanceExp008Comparator(packet);
    const score = scoreProvenance(world, comparator.inferred_root_by_document);
    assert.ok(score.pairwise_precision < 1, `${world.family} should expose false collapses`);
    assert.equal(comparator.engine_version, 'exp008-inference-comparator-js-v1');
  }
});

test('downstream decision is computed only from inferred roots', () => {
  const world = generateDiscoveryWorlds()[0];
  const packet = publicDiscoveryWorld(world);
  const decision = decideFromInferredRoots(packet, inferProvenance(packet));
  assert.equal(decision.answer, world.hidden.ground_truth);
});

test('scheduler creates the complete model-by-world cross product exactly once', () => {
  const worlds = generateDiscoveryWorlds();
  const adapters = [{ provider: 'one', model: 'alpha' }, { provider: 'two', model: 'beta' }];
  const jobs = discoveryJobs(adapters, worlds);
  assert.equal(jobs.length, adapters.length * worlds.length);
  assert.equal(new Set(jobs.map((job) => job.key)).size, jobs.length);
  for (const adapter of adapters) {
    assert.equal(jobs.filter((job) => job.adapter === adapter).length, worlds.length);
  }
});
