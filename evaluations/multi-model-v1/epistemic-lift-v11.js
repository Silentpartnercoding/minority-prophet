#!/usr/bin/env node
import { execFileSync } from 'node:child_process';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { ClaudeCliAdapter, CodexCliAdapter } from './cli-provider.js';
import { LIFT_MODEL_GRID } from './lift-benchmark.js';
import { liftBenchmarkV11 } from './lift-benchmark-v11.js';
import { runLiftBenchmark } from './lift-pipeline.js';
import { buildLiftReport, writeLiftReport } from './lift-report.js';
import { JsonStore } from './store.js';
import { verifyRun } from './verifier.js';

const PROJECT_ROOT = fileURLToPath(new URL('.', import.meta.url));
const FROZEN_MANIFEST_HASH = 'sha256:7bf6d393e59ce6fbc78ca41bda4f71b5a0c29dc95d2b535bb19901c345bf3943';
const statePath = process.env.MP_LIFT_V11_STATE ?? join(PROJECT_ROOT, 'data', 'runtime', 'epistemic-lift-v11.json');
const outputDirectory = process.env.MP_LIFT_V11_OUTPUT ?? join(PROJECT_ROOT, 'public', 'generated', 'epistemic-lift-v11');
const concurrency = Number(process.env.MP_LIFT_CONCURRENCY ?? 2);
if (!Number.isInteger(concurrency) || concurrency < 1 || concurrency > 3) throw new Error('MP_LIFT_CONCURRENCY must be an integer from 1 to 3');

const benchmark = liftBenchmarkV11();
if (benchmark.manifest.manifest_hash !== FROZEN_MANIFEST_HASH) throw new Error(`Lift v1.1 manifest is not frozen: ${benchmark.manifest.manifest_hash}`);
const protocolCommit = execFileSync('git', ['rev-parse', 'HEAD'], { cwd: PROJECT_ROOT, encoding: 'utf8' }).trim();
const worktreeStatus = execFileSync('git', ['status', '--porcelain', '--untracked-files=no'], { cwd: PROJECT_ROOT, encoding: 'utf8' }).trim();
if (worktreeStatus) throw new Error('Commit the frozen v1.1 protocol before executing model trials');
const adapters = LIFT_MODEL_GRID.map((config) => config.provider === 'openai-codex-cli'
  ? new CodexCliAdapter({ model: config.requested_model, effort: config.effort, timeoutMs: 240_000, rawCapture: true })
  : new ClaudeCliAdapter({ model: config.requested_model, effort: config.effort, timeoutMs: 240_000, rawCapture: true }));
const settings = {
  temperature: 0,
  top_p: 1,
  max_tokens: 500,
  provider_concurrency: concurrency,
  maximum_attempts_per_cell: benchmark.manifest.sampling.maximum_attempts_per_cell,
  retry_parse_failures: false,
  protocol_commit: protocolCommit,
  condition_order: benchmark.manifest.execution_order,
  tool_configuration: {
    regime: 'closed_world_precomputed_read_only_mp_receipt',
    allowed_provider_tools: [],
    external_retrieval: false,
    response_transport: 'raw_final_response_with_local_parser',
    provider_structured_output_enforcement: false,
    minority_prophet_provisioning: 'C receives a deterministic tool receipt computed only from B-visible bytes',
    isolated_temporary_working_directory: true,
    subscription_cli_candidate: true
  }
};
const runId = `epistemic-lift-v11:${benchmark.manifest.manifest_hash}:${adapters.map((adapter) => `${adapter.provider}:${adapter.model}`).join(':')}`;
const store = await new JsonStore(statePath).load();
const priorRun = store.find('benchmark_runs', (item) => (item.logical_run_id ?? item.id) === runId);
if (priorRun?.settings?.protocol_commit && priorRun.settings.protocol_commit !== protocolCommit) throw new Error('Refusing to resume a frozen v1.1 run under a different commit');
const run = await runLiftBenchmark({ store, benchmark, adapters, settings, runId });
if (run.status !== 'COMPLETED') {
  console.log(JSON.stringify({ run, resumable: false, reason: 'frozen v1.1 cell failure' }, null, 2));
  process.exitCode = 1;
} else {
  const verification = await verifyRun(store, run.id);
  const report = buildLiftReport(store, run.id, benchmark, verification);
  await writeLiftReport(report, outputDirectory);
  console.log(JSON.stringify({ run_id: run.id, status: run.status, verification: verification.status, verdict: report.verdict, report_hash: report.report_hash, output_directory: outputDirectory }, null, 2));
}
