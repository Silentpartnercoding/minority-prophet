#!/usr/bin/env node
import { execFileSync } from 'node:child_process';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { ClaudeLiveMcpAdapter, CodexLiveMcpAdapter } from './live-tool-provider.js';
import { liveToolBenchmark } from './live-tool-benchmark.js';
import { buildLiveToolReport, runLiveToolBenchmark, writeLiveToolReport } from './live-tool-runner.js';
import { JsonStore } from './store.js';

const PROJECT_ROOT = fileURLToPath(new URL('.', import.meta.url));
const FROZEN_MANIFEST_HASH = 'sha256:a61cd271d5eb0642093d63157726a2a3aeca2a01798ae50260cdc42e48330933';
const benchmark = liveToolBenchmark();
if (benchmark.manifest.manifest_hash !== FROZEN_MANIFEST_HASH) throw new Error(`Live-tool manifest is not frozen: ${benchmark.manifest.manifest_hash}`);
const protocolCommit = execFileSync('git', ['rev-parse', 'HEAD'], { cwd: PROJECT_ROOT, encoding: 'utf8' }).trim();
const status = execFileSync('git', ['status', '--porcelain', '--untracked-files=no'], { cwd: PROJECT_ROOT, encoding: 'utf8' }).trim();
if (status) throw new Error('Commit the frozen live-tool protocol before model execution');
const statePath = process.env.MP_LIVE_TOOL_STATE ?? join(PROJECT_ROOT, 'data', 'runtime', 'epistemic-live-tool-v1.json');
const outputDirectory = process.env.MP_LIVE_TOOL_OUTPUT ?? join(PROJECT_ROOT, 'public', 'generated', 'epistemic-live-tool-v1');
const comparisonStatePath = join(PROJECT_ROOT, 'data', 'runtime', 'epistemic-lift-v11.json');
const adapters = [new CodexLiveMcpAdapter(), new ClaudeLiveMcpAdapter()];
const settings = {
  temperature: 0,
  top_p: 1,
  max_tokens: 500,
  provider_concurrency: 2,
  tool_configuration: {
    transport: 'native_cli_stdio_mcp',
    permitted_tools: ['minority_prophet.analyze_evidence_structure'],
    required_successful_calls: 1,
    shell: false,
    files: false,
    network: false,
    web_search: false,
    external_retrieval: false
  }
};
const runId = `epistemic-live-tool-v1:${benchmark.manifest.manifest_hash}:${adapters.map((adapter) => `${adapter.provider}:${adapter.model}`).join(':')}`;
const store = await new JsonStore(statePath).load();
const run = await runLiveToolBenchmark({ store, benchmark, adapters, runId, settings, protocolCommit });
const report = await buildLiveToolReport({ store, run, benchmark, comparisonStatePath });
await writeLiveToolReport(report, outputDirectory);
console.log(JSON.stringify({ run_id: run.id, status: run.status, completed_trials: run.completed_trials, failed_trials: run.failed_trials, report_hash: report.report_hash, output_directory: outputDirectory }, null, 2));
if (run.status !== 'COMPLETED') process.exitCode = 1;
