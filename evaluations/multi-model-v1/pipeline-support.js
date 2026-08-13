import { CONDITIONS, SCORER_VERSION } from './src/domain/constants.js';
import { scoreModel } from './scoring.js';
import { slug } from './run-ids.js';

export async function registerExperiment(store, id, benchmark, adapters) {
  for (const adapter of adapters) {
    await store.insertIfAbsent('providers', { id: adapter.provider, name: adapter.provider });
    await store.insertIfAbsent('models', { id: `${adapter.provider}:${adapter.model}`, provider: adapter.provider, name: adapter.model, slug: slug(`${adapter.provider}-${adapter.model}`) });
    await store.insertIfAbsent('model_versions', { id: `${adapter.provider}:${adapter.model}:${adapter.version}`, provider: adapter.provider, model: adapter.model, version: adapter.version });
  }
  await store.insertIfAbsent('experiments', { id: `${id}:abc`, run_id: id, design: 'SAME_WORLD_A_B_C', conditions: [CONDITIONS.BASELINE, CONDITIONS.PROVENANCE, CONDITIONS.MINORITY_PROPHET], benchmark_version: benchmark.manifest.benchmark_version });
}

export async function scoreRun(store, id, adapters) {
  for (const adapter of adapters) {
    const trials = store.filter('trials', (trial) => trial.run_id === id && trial.model_provider === adapter.provider && trial.model_name === adapter.model && trial.status === 'COMPLETED');
    const latest = new Map();
    for (const trial of trials) latest.set(`${trial.world_id}:${trial.condition}`, trial);
    const aggregate = scoreModel([...latest.values()].map((trial) => trial.score));
    const versions = [...new Set(trials.map((trial) => trial.model_version))];
    await store.insert('scores', { id: `${id}:${adapter.provider}:${adapter.model}`, run_id: id, provider: adapter.provider, model: adapter.model, model_version: versions.join('+') || adapter.version, scorer_version: SCORER_VERSION, ...aggregate });
  }
}

export function costTelemetry(trials, worldCount) {
  const usage = trials.reduce((sum, trial) => ({ input_tokens: sum.input_tokens + (trial.usage.input_tokens ?? 0), output_tokens: sum.output_tokens + (trial.usage.output_tokens ?? 0), cached_tokens: sum.cached_tokens + (trial.usage.cached_tokens ?? 0), provider_reported_cost_usd: sum.provider_reported_cost_usd + (trial.cost_usd ?? 0), execution_ms: sum.execution_ms + (trial.execution_ms ?? 0) }), { input_tokens: 0, output_tokens: 0, cached_tokens: 0, provider_reported_cost_usd: 0, execution_ms: 0 });
  return { ...usage, trials_completed: trials.length, provider_reported_cost_per_world_usd: worldCount ? usage.provider_reported_cost_usd / worldCount : 0 };
}
