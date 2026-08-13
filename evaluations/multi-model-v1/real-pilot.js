#!/usr/bin/env node
import { join } from 'node:path';
import { developmentBenchmark } from './benchmark.js';
import { ClaudeCliAdapter, CodexCliAdapter } from './cli-provider.js';
import { publishArtifacts } from './artifacts.js';
import { DEFAULT_SETTINGS, runBenchmark } from './pipeline.js';
import { PROJECT_ROOT, openStore } from './operations.js';
import { verifyRun } from './verifier.js';

const count = Number(process.argv[2] ?? 2);
if (!Number.isInteger(count) || count < 1 || count > 25) throw new Error('World count must be an integer from 1 to 25');
const codexModel = process.env.MP_CODEX_MODEL ?? 'gpt-5.6-sol';
const claudeModel = process.env.MP_CLAUDE_MODEL ?? 'sonnet';
const statePath = join(PROJECT_ROOT, 'data', 'runtime', 'real-pilot-state.json');
const store = await openStore(statePath);
const benchmark = developmentBenchmark({ count });
const adapters = [new CodexCliAdapter({ model: codexModel }), new ClaudeCliAdapter({ model: claudeModel })];
const settings = {
  ...DEFAULT_SETTINGS,
  max_tokens: 500,
  tool_configuration: {
    regime: 'closed_world',
    allowed_tools: [],
    external_retrieval: false,
    isolated_temporary_working_directory: true,
    subscription_cli_pilot: true
  }
};
const runId = `cli-pilot-v4:${count}:${codexModel}:${claudeModel}`;
const run = await runBenchmark({ store, benchmark, adapters, namespace:'DEMO', settings, runId });
const verification = run.status === 'COMPLETED' ? await verifyRun(store, run.id) : null;
const outputDirectory = join(PROJECT_ROOT, 'public', 'generated', 'real-pilot');
const snapshot = run.status === 'COMPLETED' ? await publishArtifacts(store, outputDirectory, 'DEMO', { runIds:[run.id] }) : null;
console.log(JSON.stringify({ run, verification, snapshot_hash:snapshot?.snapshot_hash ?? null, output_directory:outputDirectory }, null, 2));
