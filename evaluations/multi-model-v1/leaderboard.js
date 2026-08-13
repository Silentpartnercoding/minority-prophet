import { CONDITIONS, RESULT_NAMESPACES } from './src/domain/constants.js';

export function leaderboardData(store, namespace = RESULT_NAMESPACES.VERIFIED, { runIds } = {}) {
  const allowedRuns = runIds ? new Set(runIds) : null;
  const verifications = new Map(store.filter('verification_records', (record) => record.namespace === namespace && record.status === 'PASSED').map((record) => [record.run_id, record]));
  const runs = store.filter('benchmark_runs', (run) => (!allowedRuns || allowedRuns.has(run.id)) && run.namespace === namespace && run.status === 'COMPLETED' && verifications.has(run.id) && (namespace !== RESULT_NAMESPACES.VERIFIED || verifications.get(run.id).official_eligible));
  const rows = [];
  for (const run of runs) {
    for (const score of store.filter('scores', (item) => item.run_id === run.id)) {
      rows.push({ run_id: run.id, namespace, model: score.model, provider: score.provider, model_version: score.model_version, benchmark_version: run.benchmark_version, last_evaluated: run.created_at, trials: score.by_condition[CONDITIONS.BASELINE].trials, baseline: score.by_condition[CONDITIONS.BASELINE], provenance: score.by_condition[CONDITIONS.PROVENANCE], minority_prophet: score.by_condition[CONDITIONS.MINORITY_PROPHET], provenance_gain: score.provenance_gain, minority_prophet_gain: score.minority_prophet_gain, total_epistemic_gain: score.total_epistemic_gain });
    }
  }
  const latest = new Map();
  for (const row of rows.sort((a, b) => b.last_evaluated.localeCompare(a.last_evaluated))) { const key = `${row.provider}:${row.model}:${row.model_version}`; if (!latest.has(key)) latest.set(key, row); }
  return [...latest.values()];
}

export function rankLeaderboard(rows, view = 'minority-prophet') {
  const metric = view === 'baseline' ? (row) => row.baseline.mp_score : view === 'provenance' ? (row) => row.provenance.mp_score : view === 'lift' ? (row) => row.minority_prophet_gain.gain : (row) => row.minority_prophet.mp_score;
  return [...rows].sort((a, b) => metric(b) - metric(a)).map((row, index) => ({ rank: index + 1, ...row }));
}

export function modelDetail(store, provider, model, namespace = RESULT_NAMESPACES.VERIFIED) {
  const row = leaderboardData(store, namespace).find((item) => item.provider === provider && item.model === model);
  if (!row) return null;
  const trials = store.filter('trials', (trial) => trial.run_id === row.run_id && trial.model_provider === provider && trial.model_name === model && trial.status === 'COMPLETED');
  return { ...row, failure_modes: trials.filter((trial) => trial.score?.eligible && !trial.score.correct).map((trial) => ({ world_id: trial.world_id, condition: trial.condition })), scenario_breakdown: [{ scenario_family: 'majority_copying', baseline: row.baseline.truth_recovery_rate, provenance: row.provenance.truth_recovery_rate, minority_prophet: row.minority_prophet.truth_recovery_rate }] };
}
