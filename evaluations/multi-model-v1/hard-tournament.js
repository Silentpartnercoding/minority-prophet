#!/usr/bin/env node
import { join } from 'node:path';
import { hardBenchmark } from './hard-benchmark.js';
import { ClaudeCliAdapter, CodexCliAdapter } from './cli-provider.js';
import { DEFAULT_SETTINGS, runBenchmark } from './pipeline.js';
import { PROJECT_ROOT, openStore } from './operations.js';
import { verifyRun } from './verifier.js';

const repetitions = Number(process.argv[2] ?? 1);
if (!Number.isInteger(repetitions) || repetitions < 1 || repetitions > 5) throw new Error('Repetitions must be an integer from 1 to 5');
const codexModels = (process.env.MP_CODEX_MODELS ?? 'gpt-5.6-sol,gpt-5.6-terra,gpt-5.6-luna').split(',').map((value) => value.trim()).filter(Boolean);
const claudeModels = (process.env.MP_CLAUDE_MODELS ?? 'opus,sonnet,haiku').split(',').map((value) => value.trim()).filter(Boolean);
const adapters = [
  ...codexModels.map((model) => new CodexCliAdapter({ model, effort: 'medium' })),
  ...claudeModels.map((model) => new ClaudeCliAdapter({ model, effort: 'medium' }))
];
if (!adapters.length) throw new Error('At least one model is required');

const benchmark = hardBenchmark({ repetitions });
const statePath = join(PROJECT_ROOT, 'data', 'runtime', 'hard-tournament-state.json');
const store = await openStore(statePath);
const settings = {
  ...DEFAULT_SETTINGS,
  max_tokens: 500,
  tool_configuration: {
    regime: 'closed_world',
    allowed_tools: [],
    external_retrieval: false,
    isolated_temporary_working_directory: true,
    subscription_cli_tournament: true,
    model_effort: 'medium'
  }
};
const modelSlug = adapters.map((adapter) => `${adapter.provider}:${adapter.model}`).join('|');
const runId = `hard-gauntlet-v1:${repetitions}:${modelSlug}`;
const run = await runBenchmark({ store, benchmark, adapters, namespace: 'DEMO', settings, runId });
const logicalRunId = run.logical_run_id ?? run.id;
const verification = run.status === 'COMPLETED' ? await verifyRun(store, run.id) : null;
const scores = store.filter('scores', (score) => score.run_id === logicalRunId);
const trials = store.filter('trials', (trial) => trial.run_id === logicalRunId && trial.status === 'COMPLETED');
const familyResults = [];
for (const adapter of adapters) for (const family of benchmark.manifest.scenario_families) for (const condition of ['A_RAW_BASELINE', 'B_PROVENANCE_AVAILABLE', 'C_MINORITY_PROPHET']) {
  const selected = trials.filter((trial) => trial.model_provider === adapter.provider && trial.model_name === adapter.model && trial.condition === condition && benchmark.worlds.find((world) => world.world_id === trial.world_id)?.scenario_family === family);
  familyResults.push({ provider: adapter.provider, model: adapter.model, family, condition, correct: selected.filter((trial) => trial.score.correct).length, trials: selected.length, abstained: selected.filter((trial) => store.find('parsed_responses', (response) => response.id === trial.parsed_response_id)?.parsed?.abstain).length });
}
console.log(JSON.stringify({ run, verification, scores, family_results: familyResults }, null, 2));
