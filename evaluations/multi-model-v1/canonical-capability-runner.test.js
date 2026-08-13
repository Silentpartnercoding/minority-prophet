import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, rm, writeFile } from 'node:fs/promises';
import { spawnSync } from 'node:child_process';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { generateCapabilityWorlds } from './capability-worlds.js';

test('pinned canonical implementation consumes the exact public packets', async () => {
  const directory = await mkdtemp(join(tmpdir(), 'mp-canonical-test-'));
  const input = join(directory, 'packets.json');
  try {
    const worlds = generateCapabilityWorlds();
    const packets = worlds.map((world) => world.public_packet);
    for (const packet of packets) {
      assert.equal(Object.hasOwn(packet, 'hidden_key'), false);
      assert.equal(Object.hasOwn(packet, 'roots'), false);
      for (const record of packet.records) {
        assert.equal(Object.hasOwn(record, 'root_id'), false);
      }
    }
    await writeFile(input, JSON.stringify(packets));
    const result = spawnSync('python3', ['canonical-capability-runner.py', input], { cwd: process.cwd(), encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
    const parsed = JSON.parse(result.stdout);
    assert.equal(parsed.cases.length, worlds.length);
    for (const [index, item] of parsed.cases.entries()) {
      assert.deepEqual(item.methods.minority_prophet_root_vote.answers, worlds[index].hidden_key.reference);
      assert.equal(item.packet_hash, worlds[index].public_packet.packet_hash);
      for (const method of Object.values(item.methods)) assert.equal(method.answers.length, 16);
    }
    assert.equal(parsed.canonical_provenance.commit, '41911af5b372dbeec8513581d6970abcda4dd166');
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
});
