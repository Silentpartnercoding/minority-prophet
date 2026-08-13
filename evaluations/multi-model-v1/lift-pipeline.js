import { RESULT_NAMESPACES } from './src/domain/constants.js';
import { persistBenchmark } from './benchmark.js';
import { costTelemetry, registerExperiment, scoreRun } from './pipeline-support.js';
import { runTrial } from './trial-runner.js';
import { conditionOrderFor } from './lift-benchmark.js';

async function runAdapterWorlds({ store, runId, adapter, worlds, settings, concurrency, errors }) {
  let cursor = 0;
  async function worker() {
    while (cursor < worlds.length) {
      const world = worlds[cursor];
      cursor += 1;
      const order = conditionOrderFor(world, adapter);
      for (let index = 0; index < order.length; index += 1) {
        const condition = order[index];
        const maximumAttempts = Math.max(1, Number(settings.maximum_attempts_per_cell ?? 1));
        let completed = Boolean(store.find('trials', (trial) => trial.run_id === runId && trial.model_provider === adapter.provider && trial.model_name === adapter.model && trial.world_id === world.world_id && trial.condition === condition && trial.status === 'COMPLETED'));
        const existingAttempts = store.filter('trials', (trial) => trial.run_id === runId && trial.model_provider === adapter.provider && trial.model_name === adapter.model && trial.world_id === world.world_id && trial.condition === condition).length;
        let lastError = null;
        for (let attempt = existingAttempts + 1; attempt <= maximumAttempts && !completed; attempt += 1) {
          try {
            const trial = await runTrial({ store, runId, adapter, world, condition, settings, executionOrder: { schedule: order, position: index + 1 } });
            completed = trial.status === 'COMPLETED' && trial.parse_success;
            if (!completed) lastError = new Error(trial.error?.message ?? 'Trial did not produce a valid structured response');
          } catch (error) {
            lastError = error;
          }
        }
        if (!completed) errors.push({ provider: adapter.provider, model: adapter.model, world_id: world.world_id, condition, message: lastError?.message ?? `Attempt cap exhausted (${existingAttempts}/${maximumAttempts})` });
      }
    }
  }
  await Promise.all(Array.from({ length: concurrency }, () => worker()));
}

export async function runLiftBenchmark({ store, benchmark, adapters, settings, runId, namespace = RESULT_NAMESPACES.DEMO }) {
  await persistBenchmark(store, benchmark);
  const completedRun = store.find('benchmark_runs', (run) => (run.logical_run_id ?? run.id) === runId && run.status === 'COMPLETED');
  if (completedRun) return completedRun;
  const attempt = store.filter('benchmark_runs', (run) => (run.logical_run_id ?? run.id) === runId).length + 1;
  await registerExperiment(store, runId, benchmark, adapters);
  const errors = [];
  const concurrency = Math.max(1, Number(settings.provider_concurrency ?? 1));
  await Promise.all(adapters.map((adapter) => runAdapterWorlds({ store, runId, adapter, worlds: benchmark.worlds, settings, concurrency, errors })));
  const trials = store.filter('trials', (trial) => trial.run_id === runId && trial.status === 'COMPLETED');
  const common = {
    logical_run_id: runId,
    attempt,
    namespace,
    benchmark_version: benchmark.manifest.benchmark_version,
    benchmark_manifest_hash: benchmark.manifest.manifest_hash,
    expected_trials: benchmark.worlds.length * adapters.length * 3,
    completed_trials: trials.length,
    failed_trials: errors.length,
    models: adapters.map((adapter) => ({ provider: adapter.provider, model: adapter.model, version: adapter.version })),
    settings,
    cost_telemetry: { ...costTelemetry(trials, benchmark.worlds.length), failures: errors.length },
    created_at: new Date().toISOString(),
    errors
  };
  if (errors.length) return store.insert('benchmark_runs', { id: `${runId}:attempt:${attempt}`, status: 'FAILED', ...common });
  await scoreRun(store, runId, adapters);
  return store.insert('benchmark_runs', { id: runId, status: 'COMPLETED', ...common });
}
