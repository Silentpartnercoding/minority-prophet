import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { generateDiscoveryWorlds, publicDiscoveryWorld } from './provenance-discovery-worlds.js';
import { startServer } from './server.js';

function requestBody() {
  const packet = publicDiscoveryWorld(generateDiscoveryWorlds()[0]);
  return {
    schema: 'evidence-collector.request.v1',
    dispatch: {
      dispatch_id: 'dispatch:bound',
      challenge_id: 'challenge:bound',
      action_digest: 'sha256:action',
      decision_subject: 'job:123',
      policy_id: 'policy:test',
      collection_round: 1,
      requester_control_domain: 'control:requester',
      route: {
        route_id: 'epistemic-analysis', collector_kind: 'epistemic_service',
        capability: 'provenance.analysis', output_role: 'verification_artifact',
        allowed_actions: ['evidence.read'], requires_independence: true,
        route_grants_protected_action_authority: false
      },
      requirements: [{
        requirement_id: 'lineage-map', description: 'Compile provenance',
        accepted_kinds: ['provenance.receipt'],
        collector_route: {
          route_id: 'epistemic-analysis', collector_kind: 'epistemic_service',
          capability: 'provenance.analysis', output_role: 'verification_artifact',
          allowed_actions: ['evidence.read'], requires_independence: true,
          route_grants_protected_action_authority: false
        }
      }],
      max_evidence_items: 1,
      grants_protected_action_authority: false
    },
    input: {
      schema: 'mp-provenance-service-input.v1',
      packet,
      proposal: {
        schema: 'mp-lineage-proposal.v1',
        links: [],
        unresolved_document_ids: packet.documents.map((document) => document.document_id),
        summary: 'No additional model-proposed collapse links.'
      }
    },
    grants_protected_action_authority: false
  };
}

test('loopback provenance service returns a bound non-authorizing receipt', async () => {
  const directory = await mkdtemp(join(tmpdir(), 'mp-provenance-service-'));
  const server = await startServer({
    port: 0,
    statePath: join(directory, 'state.json'),
    provenanceToken: 'local-test-token'
  });
  const endpoint = `http://127.0.0.1:${server.address().port}/internal/provenance/compile`;
  try {
    assert.equal((await fetch(endpoint, { method: 'POST' })).status, 401);
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { authorization: 'Bearer local-test-token', 'content-type': 'application/json' },
      body: JSON.stringify(requestBody())
    });
    assert.equal(response.status, 200);
    const result = await response.json();
    assert.equal(result.schema, 'evidence-collector.response.v1');
    assert.equal(result.challenge_id, 'challenge:bound');
    assert.equal(result.dispatch_id, 'dispatch:bound');
    assert.equal(result.collector_id, 'minority-prophet:provenance-service');
    assert.equal(result.grants_protected_action_authority, false);
    assert.equal(result.items.length, 1);
    assert.equal(result.items[0].envelope.ground_truth_included, false);
    assert.equal(result.items[0].envelope.answer_included, false);
    assert.equal('assertion' in result.items[0].envelope, false);
    assert.equal(result.items[0].envelope.attest.subject, 'job:123');
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
});

test('provenance service rejects authority expansion and extra fields', async () => {
  const directory = await mkdtemp(join(tmpdir(), 'mp-provenance-service-'));
  const server = await startServer({
    port: 0,
    statePath: join(directory, 'state.json'),
    provenanceToken: 'local-test-token'
  });
  const endpoint = `http://127.0.0.1:${server.address().port}/internal/provenance/compile`;
  try {
    for (const body of [
      { ...requestBody(), grants_protected_action_authority: true },
      { ...requestBody(), correct_answer: 'do not accept this' },
      { ...requestBody(), input: { ...requestBody().input, correct_answer: 'do not accept this' } }
    ]) {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { authorization: 'Bearer local-test-token', 'content-type': 'application/json' },
        body: JSON.stringify(body)
      });
      assert.equal(response.status, 400);
    }
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
});
