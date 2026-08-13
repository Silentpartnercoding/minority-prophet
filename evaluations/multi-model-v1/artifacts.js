import { mkdir, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { leaderboardData, rankLeaderboard } from './leaderboard.js';
import { hashObject } from './src/lib/hash.js';

export const METHODOLOGY = {
  design: 'The same model evaluates the same frozen world under three epistemic conditions.',
  conditions: { A_RAW_BASELINE: 'Claims only.', B_PROVENANCE_AVAILABLE: 'Claims plus complete declared ancestry; no score or recommendation.', C_MINORITY_PROPHET: 'The same claims and ancestry plus evidence-independence analysis; no truth label.' },
  estimands: { provenance_gain: 'Condition B minus Condition A.', minority_prophet_gain: 'Condition C minus Condition B.', total_epistemic_gain: 'Condition C minus Condition A.' },
  mp_score: { version: 'mp-score-v1', formula: '0.45 truth recovery + 0.25 false-consensus resistance + 0.15 minority recovery + 0.10 calibration + 0.05 abstention quality', components_always_exposed: true },
  caveat: 'A negative result is valid. Demonstration runs are excluded from official rankings.'
};

const csv = (rows) => {
  const columns = ['rank','provider','model','model_version','baseline','provenance','minority_prophet','provenance_gain','mp_gain','total_gain','trials','benchmark_version'];
  const lines = rows.map((row) => [row.rank,row.provider,row.model,row.model_version,row.baseline.mp_score,row.provenance.mp_score,row.minority_prophet.mp_score,row.provenance_gain.gain,row.minority_prophet_gain.gain,row.total_epistemic_gain.gain,row.trials,row.benchmark_version].map((value) => JSON.stringify(value)).join(','));
  return `${columns.join(',')}\n${lines.join('\n')}\n`;
};

export async function publishArtifacts(store, outputDirectory, namespace, { runIds } = {}) {
  await mkdir(outputDirectory, { recursive: true });
  const rows = rankLeaderboard(leaderboardData(store, namespace, { runIds }));
  const runs = [...new Set(rows.map((row) => row.run_id))].map((id) => store.find('benchmark_runs', (run) => run.id === id));
  const manifest = { namespace, benchmark_versions: [...new Set(rows.map((row) => row.benchmark_version))], run_ids: runs.map((run) => run.id), generated_at: new Date().toISOString(), hidden_worlds_included: false };
  const snapshot = { ...manifest, rows, snapshot_hash: hashObject(rows) };
  const files = {
    'methodology.json': METHODOLOGY,
    'benchmark-manifest.json': manifest,
    'results.json': rows,
    'statistical-summary.json': rows.map((row) => ({ provider: row.provider, model: row.model, baseline_ci: row.baseline.confidence_interval_95, provenance_ci: row.provenance.confidence_interval_95, mp_ci: row.minority_prophet.confidence_interval_95, provenance_gain: row.provenance_gain, minority_prophet_gain: row.minority_prophet_gain })),
    'leaderboard-snapshot.json': snapshot,
    'reproducibility.json': runs.map((run) => ({ run_id: run.id, benchmark_version: run.benchmark_version, manifest_hash: run.benchmark_manifest_hash, models: run.models, settings: run.settings })),
    'plots.json': rows.map((row) => ({ model: row.model, series: [{ condition: 'Baseline', value: row.baseline.mp_score }, { condition: 'Provenance', value: row.provenance.mp_score }, { condition: 'Minority Prophet', value: row.minority_prophet.mp_score }] }))
  };
  for (const [name, value] of Object.entries(files)) await writeFile(join(outputDirectory, name), `${JSON.stringify(value, null, 2)}\n`);
  await writeFile(join(outputDirectory, 'results.csv'), csv(rows));
  await writeFile(join(outputDirectory, 'publication-table.md'), `| Model | Baseline | Provenance | Minority Prophet | MP lift |\n|---|---:|---:|---:|---:|\n${rows.map((row) => `| ${row.model} | ${row.baseline.mp_score} | ${row.provenance.mp_score} | ${row.minority_prophet.mp_score} | ${row.minority_prophet_gain.gain} |`).join('\n')}\n`);
  return snapshot;
}
