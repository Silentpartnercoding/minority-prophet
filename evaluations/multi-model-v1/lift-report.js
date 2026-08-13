import { mkdir, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { CONDITIONS } from './src/domain/constants.js';
import { hashObject } from './src/lib/hash.js';

function conditionTrials(store, runId, provider, model, condition) {
  return store.filter('trials', (trial) => trial.run_id === runId && trial.model_provider === provider && trial.model_name === model && trial.condition === condition && trial.status === 'COMPLETED');
}

function familyBreakdown(trials) {
  const groups = new Map();
  for (const trial of trials) {
    const family = trial.score.scenario_family;
    if (!groups.has(family)) groups.set(family, []);
    groups.get(family).push(trial.score);
  }
  return Object.fromEntries([...groups.entries()].sort().map(([family, scores]) => [family, {
    trials: scores.length,
    correct: scores.filter((score) => score.correct).length,
    accuracy: Number((scores.filter((score) => score.correct).length / scores.length).toFixed(6))
  }]));
}

function pairedChanges(fromTrials, toTrials) {
  const from = new Map(fromTrials.map((trial) => [trial.world_id, trial.score]));
  const pairs = toTrials.filter((trial) => from.has(trial.world_id)).map((trial) => ({ world_id: trial.world_id, from: from.get(trial.world_id), to: trial.score }));
  return {
    pairs: pairs.length,
    improvements: pairs.filter((pair) => !pair.from.correct && pair.to.correct).length,
    regressions: pairs.filter((pair) => pair.from.correct && !pair.to.correct).length,
    unchanged_correct: pairs.filter((pair) => pair.from.correct && pair.to.correct).length,
    unchanged_incorrect: pairs.filter((pair) => !pair.from.correct && !pair.to.correct).length
  };
}

export function buildLiftReport(store, runId, benchmark, verification) {
  const run = store.find('benchmark_runs', (item) => item.id === runId);
  const rows = run.models.map(({ provider, model }) => {
    const score = store.find('scores', (item) => item.run_id === runId && item.provider === provider && item.model === model);
    const a = conditionTrials(store, runId, provider, model, CONDITIONS.BASELINE);
    const b = conditionTrials(store, runId, provider, model, CONDITIONS.PROVENANCE);
    const c = conditionTrials(store, runId, provider, model, CONDITIONS.MINORITY_PROPHET);
    const gain = score.minority_prophet_gain;
    return {
      provider,
      model,
      model_version: score.model_version,
      baseline: score.by_condition[CONDITIONS.BASELINE],
      provenance: score.by_condition[CONDITIONS.PROVENANCE],
      minority_prophet: score.by_condition[CONDITIONS.MINORITY_PROPHET],
      provenance_gain: score.provenance_gain,
      minority_prophet_gain: gain,
      total_epistemic_gain: score.total_epistemic_gain,
      paired_changes_b_to_c: pairedChanges(b, c),
      by_family: {
        A_RAW_BASELINE: familyBreakdown(a),
        B_PROVENANCE_AVAILABLE: familyBreakdown(b),
        C_MINORITY_PROPHET: familyBreakdown(c)
      },
      success_rule_passed: gain.gain >= 0.15 && gain.p_value < 0.05
    };
  });
  const verdict = rows.every((row) => row.success_rule_passed) ? 'SUPPORTED_IN_FROZEN_CANDIDATE' : 'NOT_SUPPORTED_IN_FROZEN_CANDIDATE';
  const report = {
    schema: 'mp-epistemic-lift-report.v1',
    status: run.status,
    namespace: run.namespace,
    verdict,
    claim_boundary: 'Constructed candidate-development worlds and locally authenticated subscription CLI configurations; not an official leaderboard, external validation, or real-world truth claim.',
    run_id: runId,
    benchmark_version: benchmark.manifest.benchmark_version,
    benchmark_manifest_hash: benchmark.manifest.manifest_hash,
    world_count: benchmark.worlds.length,
    replication_unit: 'world',
    expected_trials: run.expected_trials,
    completed_trials: run.completed_trials,
    verification_status: verification.status,
    verification_checks: verification.checks,
    models: rows,
    cost_telemetry: run.cost_telemetry,
    limitations: [
      'synthetic constructed worlds',
      'one call per model-world-condition cell',
      'hosted CLI aliases may change',
      'same owner/operator control domain',
      'tool result is precomputed and injected to remove optional-tool-use variance',
      'provider CLI telemetry is not controlled API cost or serving latency'
    ]
  };
  return { ...report, report_hash: hashObject(report) };
}

export async function writeLiftReport(report, outputDirectory) {
  await mkdir(outputDirectory, { recursive: true });
  await writeFile(join(outputDirectory, 'result.json'), `${JSON.stringify(report, null, 2)}\n`);
  const lines = [
    '# Epistemic Lift v1 — candidate result',
    '',
    `Status: ${report.status}`,
    '',
    `Verdict: **${report.verdict}**`,
    '',
    `Boundary: ${report.claim_boundary}`,
    '',
    '| Model | A raw | B provenance | C + MP tool | B − A | C − B | Paired p | Success |',
    '|---|---:|---:|---:|---:|---:|---:|---|',
    ...report.models.map((row) => `| ${row.model_version} | ${row.baseline.truth_recovery_rate} | ${row.provenance.truth_recovery_rate} | ${row.minority_prophet.truth_recovery_rate} | ${row.provenance_gain.gain} | ${row.minority_prophet_gain.gain} | ${row.minority_prophet_gain.p_value} | ${row.success_rule_passed ? 'yes' : 'no'} |`),
    '',
    'A negative or null verdict is valid and must remain visible.',
    ''
  ];
  await writeFile(join(outputDirectory, 'result.md'), lines.join('\n'));
}
