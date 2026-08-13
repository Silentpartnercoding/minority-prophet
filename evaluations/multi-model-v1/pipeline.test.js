import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp } from 'node:fs/promises';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { developmentBenchmark } from './benchmark.js';
import { leaderboardData } from './leaderboard.js';
import { runBenchmark } from './pipeline.js';
import { DeterministicAdapter } from './providers.js';
import { JsonStore } from './store.js';
import { verifyRun } from './verifier.js';

async function freshStore() { const directory = await mkdtemp(join(tmpdir(), 'mp-eval-')); return new JsonStore(join(directory, 'state.json')).load(); }

test('full A/B/C loop persists responses and validates DEMO', async () => {
  const store = await freshStore();
  const adapters = [new DeterministicAdapter('majority-follower-v1'), new DeterministicAdapter('lineage-reasoner-v1')];
  const run = await runBenchmark({ store, benchmark: developmentBenchmark({ count: 2 }), adapters, runId: 'integration-run' });
  assert.equal(run.status, 'COMPLETED');
  assert.equal(run.completed_trials, 12);
  assert.equal(store.all('raw_responses').length, 12);
  assert.equal(store.all('parsed_responses').length, 12);
  const trial = store.all('trials')[0];
  for (const field of ['benchmark_version','world_id','world_hash','seed','model_provider','model_name','model_version','condition','system_prompt_hash','user_prompt_hash','provenance_graph_hash','timestamp','temperature','top_p','max_tokens','tool_configuration','provider_request_id']) assert.ok(field in trial, field);
  const verification = await verifyRun(store, run.id);
  assert.equal(verification.status, 'PASSED');
  assert.equal(verification.official_eligible, false);
  assert.equal(leaderboardData(store, 'DEMO').length, 2);
  assert.equal(leaderboardData(store, 'VERIFIED').length, 0);
  await runBenchmark({ store, benchmark: developmentBenchmark({ count: 2 }), adapters, runId: 'integration-run' });
  assert.equal(store.filter('trials', (item) => item.status === 'COMPLETED').length, 12);
});
