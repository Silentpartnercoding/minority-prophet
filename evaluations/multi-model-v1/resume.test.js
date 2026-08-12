import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp } from 'node:fs/promises';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { developmentBenchmark } from './benchmark.js';
import { runBenchmark } from './pipeline.js';
import { DeterministicAdapter } from './providers.js';
import { JsonStore } from './store.js';

test('failed provider trial resumes without duplicating completed trials', async () => {
  const directory = await mkdtemp(join(tmpdir(), 'mp-resume-'));
  const store = await new JsonStore(join(directory, 'state.json')).load();
  const base = new DeterministicAdapter('flaky-v1');
  let fail = true;
  const flaky = { provider:base.provider,model:base.model,version:base.version,runModel: async (request) => { if (fail) { fail = false; throw new Error('temporary outage'); } return base.runModel(request); } };
  const benchmark = developmentBenchmark({ count: 1 });
  const first = await runBenchmark({ store, benchmark, adapters:[flaky], runId:'resume-run' });
  assert.equal(first.status, 'FAILED');
  const second = await runBenchmark({ store, benchmark, adapters:[flaky], runId:'resume-run' });
  assert.equal(second.status, 'COMPLETED');
  const completed = store.filter('trials', (item) => item.run_id === 'resume-run' && item.status === 'COMPLETED');
  assert.equal(completed.length, 3);
  assert.equal(new Set(completed.map((item) => item.trial_key)).size, 3);
  assert.equal(store.filter('trials', (item) => item.run_id === 'resume-run' && item.status === 'FAILED').length, 1);
});
