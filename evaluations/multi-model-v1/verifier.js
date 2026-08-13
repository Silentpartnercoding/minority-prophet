import { CONDITIONS, LIFT_BENCHMARK_VERSION, RESULT_NAMESPACES } from './src/domain/constants.js';
import { MP_TOOL_CONTRACT_HASH } from './mp-tool-v2.js';
import { hashObject } from './src/lib/hash.js';

function worldPayload(record) {
  const { id, record_hash, world_hash, ...world } = record;
  return world;
}

export async function verifyRun(store, runId) {
  const run = store.find('benchmark_runs', (item) => item.id === runId);
  if (!run) throw new Error(`Unknown run ${runId}`);
  const benchmark = store.find('benchmark_versions', (item) => item.id === run.benchmark_version);
  const worlds = store.filter('worlds', (world) => world.benchmark_version === run.benchmark_version);
  const trials = store.filter('trials', (trial) => trial.run_id === runId && trial.status === 'COMPLETED');
  const scores = store.filter('scores', (score) => score.run_id === runId);
  const checks = [];
  const check = (name, passed, detail) => checks.push({ name, passed, detail });
  check('run_completed', run.status === 'COMPLETED', run.status);
  check('expected_trial_count', trials.length === run.expected_trials, `${trials.length}/${run.expected_trials}`);
  check('no_failed_trials', run.failed_trials === 0, String(run.failed_trials));
  check('all_responses_parse', trials.every((trial) => trial.parse_success), `${trials.filter((trial) => trial.parse_success).length}/${trials.length}`);
  check('world_hash_integrity', worlds.every((world) => hashObject(worldPayload(world)) === world.world_hash), `${worlds.length} worlds checked`);
  const groups = new Map();
  for (const trial of trials) { const key = `${trial.model_provider}:${trial.model_name}:${trial.world_id}`; if (!groups.has(key)) groups.set(key, []); groups.get(key).push(trial); }
  check('identical_world_across_abc', [...groups.values()].every((group) => group.length === 3 && new Set(group.map((trial) => trial.world_hash)).size === 1 && new Set(group.map((trial) => trial.seed)).size === 1), `${groups.size} model-world groups`);
  if (run.benchmark_version === LIFT_BENCHMARK_VERSION) {
    const liftGroups = [...groups.values()];
    check('identical_system_prompt_across_abc', liftGroups.every((group) => new Set(group.map((trial) => trial.system_prompt_hash)).size === 1), `${liftGroups.length} model-world groups`);
    check('identical_model_version_across_abc', liftGroups.every((group) => new Set(group.map((trial) => trial.model_version)).size === 1), `${liftGroups.length} model-world groups`);
    check('identical_b_c_epistemic_base', liftGroups.every((group) => {
      const b = group.find((trial) => trial.condition === CONDITIONS.PROVENANCE);
      const c = group.find((trial) => trial.condition === CONDITIONS.MINORITY_PROPHET);
      return b?.epistemic_base_hash && b.epistemic_base_hash === c?.epistemic_base_hash;
    }), `${liftGroups.length} B/C pairs`);
    check('mp_output_only_in_c', liftGroups.every((group) => group.every((trial) => trial.condition === CONDITIONS.MINORITY_PROPHET ? Boolean(trial.minority_prophet_output_hash) : trial.minority_prophet_output_hash === null)), `${liftGroups.length} model-world groups`);
    check('mp_tool_contract_pinned', liftGroups.every((group) => group.every((trial) => trial.condition === CONDITIONS.MINORITY_PROPHET ? trial.mp_tool_contract_hash === MP_TOOL_CONTRACT_HASH : trial.mp_tool_contract_hash === null)), MP_TOOL_CONTRACT_HASH);
    const requiredConditions = [CONDITIONS.BASELINE, CONDITIONS.PROVENANCE, CONDITIONS.MINORITY_PROPHET].sort().join('|');
    check('condition_order_recorded', liftGroups.every((group) => group.length === 3 && new Set(group.map((trial) => trial.execution_order?.position)).size === 3 && group.every((trial) => [...(trial.execution_order?.schedule ?? [])].sort().join('|') === requiredConditions)), `${liftGroups.length} counterbalanced groups`);
  }
  check('scores_recorded', scores.length === run.models.length && scores.every((score) => score.scorer_version), `${scores.length}/${run.models.length}`);
  const publicSafe = worlds.every((world) => world.metadata?.split !== 'private_evaluation' || run.namespace !== RESULT_NAMESPACES.DEMO);
  check('contamination_policy', publicSafe, 'Private worlds are not exposed by artifact routes');
  const basePassed = checks.every((item) => item.passed);
  const officialEligible = basePassed && run.namespace === RESULT_NAMESPACES.VERIFIED && benchmark?.frozen === true && worlds.every((world) => world.metadata?.split !== 'development');
  if (run.namespace === RESULT_NAMESPACES.VERIFIED) check('verified_release_gate', officialEligible, 'Requires frozen benchmark and non-development worlds');
  return store.insertIfAbsent('verification_records', { id: `${runId}:verification`, run_id: runId, namespace: run.namespace, status: basePassed ? 'PASSED' : 'FAILED', official_eligible: officialEligible, checks, verified_at: new Date().toISOString(), store_snapshot_hash: store.snapshotHash() });
}
