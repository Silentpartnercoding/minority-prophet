import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { developmentBenchmark } from './benchmark.js';
import { publishArtifacts } from './artifacts.js';
import { DeterministicAdapter } from './providers.js';
import { JsonStore } from './store.js';
import { runBenchmark } from './pipeline.js';
import { verifyRun } from './verifier.js';

export const PROJECT_ROOT = dirname(fileURLToPath(import.meta.url));
export const DEFAULT_STATE_PATH = join(PROJECT_ROOT, 'data', 'runtime', 'state.json');

export async function openStore(path = DEFAULT_STATE_PATH) { return new JsonStore(path).load(); }

export async function runLocalDemo({ statePath = DEFAULT_STATE_PATH, count = 25 } = {}) {
  const store = await openStore(statePath);
  const benchmark = developmentBenchmark({ count });
  const adapters = [new DeterministicAdapter('majority-follower-v1'), new DeterministicAdapter('lineage-reasoner-v1')];
  const run = await runBenchmark({ store, benchmark, adapters, namespace: 'DEMO' });
  const verification = await verifyRun(store, run.id);
  return { store, run, verification };
}

export async function publishLocalDemo({ statePath = DEFAULT_STATE_PATH, outputDirectory = join(PROJECT_ROOT, 'public', 'generated', 'demo') } = {}) {
  const store = await openStore(statePath);
  const snapshot = await publishArtifacts(store, outputDirectory, 'DEMO');
  await store.insertIfAbsent('leaderboard_snapshots', { id: `DEMO:${snapshot.snapshot_hash}`, ...snapshot });
  return snapshot;
}
