import test from 'node:test';
import assert from 'node:assert/strict';
import { capabilityManifest, generateCapabilityWorlds, PROPOSITIONS } from './capability-worlds.js';

test('capability cases are deterministic, opaque, and use complete traceable lineage', () => {
  const first = generateCapabilityWorlds();
  const second = generateCapabilityWorlds();
  assert.deepEqual(first, second);
  assert.equal(first.length, 8);
  for (const { public_packet: packet, hidden_key: hidden } of first) {
    assert.equal(packet.proposition_ids.length, PROPOSITIONS);
    assert.equal(hidden.reference.length, PROPOSITIONS);
    assert.ok(packet.records.length >= hidden.roots);
    assert.ok(packet.records.every((record) => record.answers.length === PROPOSITIONS));
    assert.doesNotMatch(JSON.stringify(packet), /truth|falsehood|correct|incorrect|fresh|revok/i);
    const byId = new Map(packet.records.map((record) => [record.record_id, record]));
    const rootOf = (record) => record.parent_record_id === null ? record.record_id : rootOf(byId.get(record.parent_record_id));
    const byRoot = new Map();
    for (const record of packet.records) {
      if (record.parent_record_id !== null) {
        assert.ok(byId.has(record.parent_record_id));
        assert.ok(byId.get(record.parent_record_id).sequence < record.sequence);
      }
      const vector = JSON.stringify(record.answers);
      const root = rootOf(record);
      if (byRoot.has(root)) assert.equal(byRoot.get(root), vector);
      else byRoot.set(root, vector);
    }
    assert.equal(byRoot.size, hidden.roots);
  }
  assert.equal(capabilityManifest(first).manifest_hash, capabilityManifest(second).manifest_hash);
});

test('answerable cases use the constructed root reference and tie cases require abstention', () => {
  for (const { hidden_key: hidden } of generateCapabilityWorlds()) {
    if (hidden.family.startsWith('balanced_root_tie')) assert.ok(hidden.reference.every((value) => value === 'ABSTAIN'));
    else assert.ok(hidden.reference.every((value) => value === 'A' || value === 'B'));
  }
});
