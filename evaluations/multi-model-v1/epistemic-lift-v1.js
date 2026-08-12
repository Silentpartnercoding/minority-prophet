#!/usr/bin/env node
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';
import { ClaudeCliAdapter, CodexCliAdapter } from './cli-provider.js';
import { liftBenchmark, LIFT_MODEL_GRID } from './lift-benchmark.js';
import { runLiftBenchmark } from './lift-pipeline.js';
import { buildLiftReport, writeLiftReport } from './lift-report.js';
import { JsonStore } from './store.js';
import { verifyRun } from './verifier.js';

const PROJECT_ROOT = fileURLToPath(new URL('.', import.meta.url));
const FROZEN_MANIFEST_HASH = 'sha256:27f03b6fa35938eb5c81fc3f255aac17aa523b7802e68f52d8fba6b8d2518b7f';
const statePath = process.env.MP_LIFT_STATE ?? join(PROJECT_ROOT, 'data', 'runtime', 'epistemic-lift-v1.json');
const outputDirectory = process.env.MP_LIFT_OUTPUT ?? join(PROJECT_ROOT, 'public', 'generated', 'epistemic-lift-v1');
const concurrency = Number(process.env.MP_LIFT_CONCURRENCY ?? 2);
if (!Number.isInteger(concurrency) || concurrency < 1 || concurrency > 3) throw new Error('MP_LIFT_CONCURRENCY must be an integer from 1 to 3');

const benchmark = liftBenchmark();
if (benchmark.manifest.manifest_hash !== FROZEN_MANIFEST_HASH) throw new Error(`Lift manifest is not frozen: ${benchmark.manifest.manifest_hash}`);
const protocolCommit = execFileSync('git', ['rev-parse', 'HEAD'], { cwd: PROJECT_ROOT, encoding: 'utf8' }).trim();
const worktreeStatus = execFileSync('git', ['status', '--porcelain', '--untracked-files=no'], { cwd: PROJECT_ROOT, encoding: 'utf8' }).trim();
if (worktreeStatus) throw new Error('Commit the frozen protocol before executing model trials');
const adapters = LIFT_MODEL_GRID.map((config) => config.provider === 'openai-codex-cli'
  ? new CodexCliAdapter({ model: config.requested_model, effort: config.effort, timeoutMs: 240_000 })
  : new ClaudeCliAdapter({ model: config.requested_model, effort: config.effort, timeoutMs: 240_000 }));
const settings = {
  temperature: 0,
  top_p: 1,
  max_tokens: 500,
  provider_concurrency: concurrency,
  maximum_attempts_per_cell: benchmark.manifest.sampling.maximum_attempts_per_cell,
  retry_parse_failures: true,
  protocol_commit: protocolCommit,
  condition_order: benchmark.manifest.execution_order,
  tool_configuration: {
    regime: 'closed_world_precomputed_read_only_mp_receipt',
    allowed_provider_tools: [],
    external_retrieval: false,
    minority_prophet_provisioning: 'C receives a deterministic tool receipt computed only from B-visible bytes',
    isolated_temporary_working_directory: true,
    subscription_cli_candidate: true
  }
};
const runId = `epistemic-lift-v1:${benchmark.manifest.manifest_hash}:${adapters.map((adapter) => `${adapter.provider}:${adapter.model}`).join(':')}`;
const store = await new JsonStore(statePath).load();
const priorRun = store.find('benchmark_runs', (item) => (item.logical_run_id ?? item.id) === runId);
if (priorRun?.settings?.protocol_commit && priorRun.settings.protocol_commit !== protocolCommit) {
  throw new Error(`Refusing to resume a frozen run under a different commit: ${priorRun.settings.protocol_commit} != ${protocolCommit}`);
}
const run = await runLiftBenchmark({ store, benchmark, adapters, settings, runId });
if (run.status !== 'COMPLETED') {
  console.log(JSON.stringify({ run, resumable: false, reason: 'preregistered attempt cap exhausted for one or more cells' }, null, 2));
  process.exitCode = 1;
} else {
  const verification = await verifyRun(store, run.id);
  const report = buildLiftReport(store, run.id, benchmark, verification);
  await writeLiftReport(report, outputDirectory);
  console.log(JSON.stringify({ run_id: run.id, status: run.status, verification: verification.status, verdict: report.verdict, report_hash: report.report_hash, output_directory: outputDirectory }, null, 2));
}
