#!/usr/bin/env node
import { join } from 'node:path';
import { hardBenchmark } from './hard-benchmark.js';
import { PROJECT_ROOT, openStore } from './operations.js';

const store = await openStore(join(PROJECT_ROOT, 'data', 'runtime', 'hard-tournament-state.json'));
const benchmark = hardBenchmark();
const run = store.all('benchmark_runs').find((candidate) => candidate.benchmark_manifest_hash === benchmark.manifest.manifest_hash);
if (!run) throw new Error('Hard tournament run not found');
const logicalRunId = run.logical_run_id ?? run.id;
const trials = store.filter('trials', (trial) => trial.run_id === logicalRunId);
const expectedKeys = new Set();
for (const model of run.models) for (const world of benchmark.worlds) for (const condition of ['A_RAW_BASELINE', 'B_PROVENANCE_AVAILABLE', 'C_MINORITY_PROPHET']) expectedKeys.add(`${model.provider}|${model.model}|${world.world_id}|${condition}`);
const actualKeys = trials.map((trial) => `${trial.model_provider}|${trial.model_name}|${trial.world_id}|${trial.condition}`);
const checks = [
  ['manifest_hash', run.benchmark_manifest_hash === benchmark.manifest.manifest_hash, run.benchmark_manifest_hash],
  ['expected_attempt_count', trials.length === expectedKeys.size, `${trials.length}/${expectedKeys.size}`],
  ['one_attempt_per_cell', new Set(actualKeys).size === actualKeys.length && actualKeys.every((key) => expectedKeys.has(key)), `${new Set(actualKeys).size}/${actualKeys.length}`],
  ['completed_count', trials.filter((trial) => trial.status === 'COMPLETED').length === 142, String(trials.filter((trial) => trial.status === 'COMPLETED').length)],
  ['failed_count', trials.filter((trial) => trial.status === 'FAILED').length === 2, String(trials.filter((trial) => trial.status === 'FAILED').length)],
  ['all_completed_parse', trials.filter((trial) => trial.status === 'COMPLETED').every((trial) => trial.parse_success), `${trials.filter((trial) => trial.status === 'COMPLETED' && trial.parse_success).length}/${trials.filter((trial) => trial.status === 'COMPLETED').length}`],
  ['world_hashes_match_manifest', trials.every((trial) => benchmark.worlds.find((world) => world.world_id === trial.world_id)?.world_hash === trial.world_hash), `${trials.length} attempts checked`],
  ['same_world_across_abc', [...expectedKeys].every((key) => actualKeys.includes(key)), `${actualKeys.length}/${expectedKeys.size}`],
  ['failures_preserved', trials.filter((trial) => trial.status === 'FAILED').every((trial) => trial.model_name === 'sonnet' && trial.condition === 'C_MINORITY_PROPHET' && ['mp_hard_0005', 'mp_hard_0008'].includes(trial.world_id)), 'two Sonnet C structured-output failures']
].map(([name, passed, detail]) => ({ name, passed, detail }));
const output = { status: checks.every((check) => check.passed) ? 'PASSED_WITH_DISCLOSED_FAILURES' : 'FAILED_AUDIT', logical_run_id: logicalRunId, run_status: run.status, checks };
console.log(JSON.stringify(output, null, 2));
if (!checks.every((check) => check.passed)) process.exitCode = 1;
