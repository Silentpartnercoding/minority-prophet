import assert from 'node:assert/strict';
import test from 'node:test';
import { generateDiscoveryWorlds, publicDiscoveryWorld } from './provenance-discovery-worlds.js';
import { compileProvenanceProposal, parseAndCompileProvenanceProposal } from './provenance-receipt.js';

function proposal(links = [], unresolved = []) {
  return { schema: 'mp-lineage-proposal.v1', links, unresolved_document_ids: unresolved, summary: 'Concise untrusted model proposal.' };
}

test('deterministic compiler, not the model, mints accepted links and receipt hash', () => {
  const packet = publicDiscoveryWorld(generateDiscoveryWorlds()[0]);
  const receipt = compileProvenanceProposal(packet, proposal());
  assert.equal(receipt.status, 'ACCEPTED');
  assert.equal(receipt.accepted_links.length, 7);
  assert.match(receipt.receipt_hash, /^sha256:/);
  assert.equal(receipt.ground_truth_included, false);
  assert.equal(receipt.answer_included, false);
  assert.equal('correct_answer' in receipt, false);
  assert.equal('answer' in receipt, false);
});

test('semantic model proposals remain review-only even at confidence one', () => {
  const packet = publicDiscoveryWorld(generateDiscoveryWorlds().find((world) => world.family === 'opaque_paraphrase'));
  const [first, second] = packet.documents.filter((document) => document.publisher.startsWith('Outlet')).sort((a, b) => a.published_at.localeCompare(b.published_at));
  const receipt = compileProvenanceProposal(packet, proposal([{
    child_document_id: second.document_id,
    parent_document_id: first.document_id,
    confidence: 1,
    evidence_types: ['exact_text_match']
  }]));
  assert.equal(receipt.status, 'REVIEW_REQUIRED');
  assert.equal(receipt.accepted_links.length, 0);
  assert.equal(receipt.review_links.length, 1);
});

test('unknown IDs, self-parenting, and unsupported links fail closed', () => {
  const packet = publicDiscoveryWorld(generateDiscoveryWorlds()[0]);
  const id = packet.documents[0].document_id;
  const receipt = compileProvenanceProposal(packet, proposal([
    { child_document_id: 'doc_missing', parent_document_id: id, confidence: 0.9, evidence_types: ['explicit_citation'] },
    { child_document_id: id, parent_document_id: id, confidence: 0.9, evidence_types: ['exact_text_match'] }
  ]));
  assert.equal(receipt.status, 'REVIEW_REQUIRED');
  assert.equal(receipt.rejected_links.length, 2);
});

test('unexpected answer or truth fields reject the complete proposal', () => {
  const packet = publicDiscoveryWorld(generateDiscoveryWorlds()[0]);
  const receipt = compileProvenanceProposal(packet, { ...proposal(), correct_answer: 'Birch' });
  assert.equal(receipt.status, 'REJECTED');
  assert.equal(receipt.accepted_links.length, 0);
  assert.ok(receipt.validation_errors.some((error) => error.includes('unexpected_top_level_field')));
});

test('receipt is deterministic for identical bytes', () => {
  const packet = publicDiscoveryWorld(generateDiscoveryWorlds()[0]);
  assert.deepEqual(compileProvenanceProposal(packet, proposal()), compileProvenanceProposal(packet, proposal()));
});

test('malformed or fenced JSON is rejected without repair', () => {
  const packet = publicDiscoveryWorld(generateDiscoveryWorlds()[0]);
  const raw = `\`\`\`json\n${JSON.stringify(proposal())}\n\`\`\``;
  const receipt = parseAndCompileProvenanceProposal(packet, raw);
  assert.equal(receipt.status, 'REJECTED');
  assert.deepEqual(receipt.accepted_links, []);
  assert.ok(receipt.validation_errors.includes('proposal_not_object'));
});

test('fabricated future and conflicting citations cannot receive ACCEPTED status', () => {
  const world = generateDiscoveryWorlds().find((value) => value.family === 'deceptive_citation');
  const receipt = compileProvenanceProposal(publicDiscoveryWorld(world), proposal());
  assert.equal(receipt.status, 'REVIEW_REQUIRED');
  assert.ok(receipt.provenance_warnings.some((warning) => ['non_prior_citation', 'citation_assertion_conflict'].includes(warning.warning)));
});
