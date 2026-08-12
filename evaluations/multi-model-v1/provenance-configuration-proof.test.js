import assert from 'node:assert/strict';
import test from 'node:test';
import { ambiguityPair, evaluateAmbiguityConfigurations } from './provenance-configuration-proof.js';
import { inferProvenance } from './provenance-inference.js';
import { generateDiscoveryWorlds, publicDiscoveryWorld } from './provenance-discovery-worlds.js';

test('opposite hidden lineage graphs can have byte-identical public evidence', () => {
  const pair = ambiguityPair();
  assert.equal(pair.copy_world.hidden.root_by_document[pair.packet.documents[1].document_id], pair.packet.documents[0].document_id);
  assert.equal(pair.independent_world.hidden.root_by_document[pair.packet.documents[1].document_id], pair.packet.documents[1].document_id);
  assert.deepEqual(
    { world_id: pair.copy_world.world_id, question: pair.copy_world.question, documents: pair.copy_world.documents },
    { world_id: pair.independent_world.world_id, question: pair.independent_world.question, documents: pair.independent_world.documents }
  );
});

test('no deterministic threshold can distinguish observationally identical lineage worlds', () => {
  const result = evaluateAmbiguityConfigurations();
  assert.deepEqual(result.configurations.confidence_gated_review, { copy_accuracy: 0, independent_accuracy: 1, paired_mean_accuracy: 0.5 });
  assert.deepEqual(result.configurations.exact_text_auto_collapse, { copy_accuracy: 1, independent_accuracy: 0, paired_mean_accuracy: 0.5 });
});

test('improved scan detects exact and near-copy candidates without trusting them', () => {
  for (const world of generateDiscoveryWorlds().filter((value) => ['generic_boilerplate', 'opaque_paraphrase'].includes(value.family))) {
    const inference = inferProvenance(publicDiscoveryWorld(world));
    assert.equal(inference.accepted_links.length, 0);
    assert.equal(inference.review_links.length, 21);
    assert.equal(inference.claim_clusters.length, 1);
    assert.equal(inference.claim_clusters[0].evidential_independence, 'unresolved');
    assert.equal(inference.next_action, 'semantic_review_required');
  }
});
