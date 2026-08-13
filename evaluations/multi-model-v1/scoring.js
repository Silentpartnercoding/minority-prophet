import { CONDITIONS, SCORER_VERSION } from './src/domain/constants.js';
import { pairedGain, wilsonInterval } from './stats.js';
const round = (value) => Number(value.toFixed(6));
const mean = (values) => values.length ? values.reduce((sum, value) => sum + value, 0) / values.length : null;
const norm = (value) => String(value ?? '').trim().toLocaleLowerCase('en-US');

export function scoreTrial(trial, world, parsed) {
  if (!parsed?.parse_success) return { eligible: false, correct: null, reason: 'PARSE_FAILURE', condition: trial.condition, world_id: world.world_id };
  const response = parsed.parsed;
  const expectedAbstention = world.expected_disposition === 'ABSTAIN';
  const correct = expectedAbstention ? response.abstain : !response.abstain && norm(response.answer) === norm(world.ground_truth);
  return { eligible: true, correct, false_consensus: Boolean(world.metadata.false_majority), minority_recovered: Boolean(!expectedAbstention && world.metadata.false_majority && correct), confidence: response.confidence, brier: (response.confidence - Number(correct)) ** 2, abstention_appropriate: expectedAbstention ? response.abstain : !response.abstain, expected_disposition: world.expected_disposition ?? 'ANSWER', scenario_family: world.scenario_family, condition: trial.condition, consensus_ratio: world.consensus_ratio, world_id: world.world_id };
}

export function aggregateCondition(items) {
  const eligible = items.filter((item) => item.eligible);
  const correct = eligible.filter((item) => item.correct).length;
  const falseConsensus = eligible.filter((item) => item.false_consensus);
  const minority = falseConsensus.filter((item) => item.minority_recovered).length;
  const truthRecovery = eligible.length ? correct / eligible.length : 0;
  const resistance = falseConsensus.length ? minority / falseConsensus.length : 0;
  const calibration = eligible.length ? 1 - mean(eligible.map((item) => item.brier)) : 0;
  const abstention = eligible.length ? mean(eligible.map((item) => Number(item.abstention_appropriate))) : 0;
  const mpScore = 0.45 * truthRecovery + 0.25 * resistance + 0.15 * resistance + 0.10 * calibration + 0.05 * abstention;
  return { scorer_version: SCORER_VERSION, trials: eligible.length, attempted_trials: items.length, parse_failures: items.length - eligible.length, truth_recovery_rate: round(truthRecovery), false_consensus_resistance: round(resistance), minority_recovery_rate: round(resistance), calibration_score: round(calibration), abstention_quality: round(abstention), mp_score: round(mpScore), confidence_interval_95: wilsonInterval(correct, eligible.length) };
}

export function scoreModel(items) {
  const byCondition = Object.fromEntries(Object.values(CONDITIONS).slice(0, 3).map((condition) => [condition, aggregateCondition(items.filter((item) => item.condition === condition))]));
  const baseline = items.filter((item) => item.condition === CONDITIONS.BASELINE);
  const provenance = items.filter((item) => item.condition === CONDITIONS.PROVENANCE);
  const mp = items.filter((item) => item.condition === CONDITIONS.MINORITY_PROPHET);
  return { by_condition: byCondition, provenance_gain: pairedGain(baseline, provenance), minority_prophet_gain: pairedGain(provenance, mp), total_epistemic_gain: pairedGain(baseline, mp) };
}
