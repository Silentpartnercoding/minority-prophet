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
    schema: 'mp-provenance-service-request.v1',
    challenge_id: 'challenge:bound',
    dispatch_id: 'dispatch:bound',
    action_digest: 'sha256:action',
    decision_subject: 'job:123',
    packet,
    proposal: {
      schema: 'mp-lineage-proposal.v1',
      links: [],
      unresolved_document_ids: packet.documents.map((document) => document.document_id),
      summary: 'No additional model-proposed collapse links.'
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
    assert.equal(result.schema, 'mp-provenance-service-response.v1');
    assert.equal(result.challenge_id, 'challenge:bound');
    assert.equal(result.dispatch_id, 'dispatch:bound');
    assert.equal(result.output_role, 'verification_artifact');
    assert.equal(result.grants_protected_action_authority, false);
    assert.equal(result.receipt.ground_truth_included, false);
    assert.equal(result.receipt.answer_included, false);
    assert.equal('assertion' in result.receipt, false);
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
      { ...requestBody(), correct_answer: 'do not accept this' }
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
