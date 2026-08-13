import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp } from 'node:fs/promises';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { TABLES } from './src/domain/constants.js';
import { assertBenchmarkWritable, freezeManifest } from './locking.js';
import { JsonStore } from './store.js';

test('all required persistence tables exist and records are deeply immutable', async () => {
  const directory = await mkdtemp(join(tmpdir(), 'mp-store-'));
  const store = await new JsonStore(join(directory, 'state.json')).load();
  for (const table of TABLES) assert.deepEqual(store.all(table), []);
  const record = await store.insert('models', { id:'p:m',nested:{ version:'v1' } });
  assert.throws(() => { record.nested.version = 'v2'; }, TypeError);
  await assert.rejects(store.insert('models', { id:'p:m' }), /Immutable duplicate/);
  await store.insert('model_versions', { id:'p:m:v1',provider:'p',model:'m',version:'v1' });
  await store.insert('model_versions', { id:'p:m:v2',provider:'p',model:'m',version:'v2' });
  assert.equal(store.all('model_versions').length, 2);
  const reloaded = await new JsonStore(join(directory, 'state.json')).load();
  assert.equal(reloaded.all('model_versions').length, 2);
});

test('frozen benchmark manifests reject mutation workflows', () => {
  const manifest = freezeManifest({ benchmark_version:'1.0.0',frozen:false }, '2026-01-01T00:00:00Z');
  assert.equal(manifest.release_state, 'FROZEN');
  assert.throws(() => assertBenchmarkWritable(manifest), /frozen and immutable/);
});
