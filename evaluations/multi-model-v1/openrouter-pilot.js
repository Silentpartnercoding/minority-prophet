#!/usr/bin/env node
import { join } from 'node:path';
import { developmentBenchmark } from './benchmark.js';
import { DEFAULT_SETTINGS, runBenchmark } from './pipeline.js';
import { createAdapter } from './provider-registry.js';
import { PROJECT_ROOT, openStore } from './operations.js';
import { verifyRun } from './verifier.js';

const count = Number(process.argv[2] ?? 25);
if (!Number.isInteger(count) || count < 1 || count > 25) throw new Error('World count must be an integer from 1 to 25');
if (!process.env.OPENROUTER_API_KEY) throw new Error('OPENROUTER_API_KEY is required');

const budgetUsd = Number(process.env.MP_OPENROUTER_BUDGET_USD ?? 3);
if (!Number.isFinite(budgetUsd) || budgetUsd <= 0 || budgetUsd > 10) throw new Error('MP_OPENROUTER_BUDGET_USD must be greater than 0 and no more than 10');

const modelConfigs = [
  { provider: 'openrouter', model: 'openai/gpt-4.1' },
  { provider: 'openrouter', model: 'anthropic/claude-sonnet-4.6', request_body: { reasoning: { enabled: false, exclude: true } } },
  { provider: 'openrouter', model: 'google/gemini-2.5-flash', request_body: { reasoning: { enabled: false, exclude: true } } }
];

const benchmark = developmentBenchmark({ count });
const statePath = join(PROJECT_ROOT, 'data', 'runtime', 'openrouter-pilot-state.json');
const store = await openStore(statePath);
const modelKey = modelConfigs.map(({ model }) => model).join('|');
const runId = `openrouter-api-pilot-v1:${count}:${modelKey}`;
const priorSpend = store.filter('trials', (trial) => trial.run_id === runId)
  .reduce((sum, trial) => sum + Number(trial.cost_usd ?? 0), 0);
const totalCalls = count * modelConfigs.length * 3;
const budget = { limit: budgetUsd, spent: priorSpend, invocationSpend: 0, calls: 0, reservedPerCall: 0.05 };
const adapters = modelConfigs.map((config) => {
  const adapter = createAdapter(config);
  return {
    provider: adapter.provider,
    model: adapter.model,
    version: adapter.version,
    async runModel(request) {
      if (budget.spent + budget.reservedPerCall > budget.limit) throw new Error(`OpenRouter pilot budget guard reached at $${budget.spent.toFixed(6)}`);
      const result = await adapter.runModel(request);
      const cost = Number(result.cost_usd ?? 0);
      if (!Number.isFinite(cost) || cost < 0) throw new Error('OpenRouter returned invalid cost telemetry');
      budget.spent += cost;
      budget.invocationSpend += cost;
      budget.calls += 1;
      if (budget.calls === 1 || budget.calls % 10 === 0 || budget.calls === totalCalls) {
        process.stderr.write(`[openrouter-pilot] ${budget.calls} new calls; $${budget.spent.toFixed(6)} cumulative provider-reported spend\n`);
      }
      return result;
    }
  };
});

const settings = {
  ...DEFAULT_SETTINGS,
  max_tokens: 800,
  retry_parse_failures: false,
  tool_configuration: {
    regime: 'closed_world',
    allowed_tools: [],
    external_retrieval: false,
    paid_api_pilot: true,
    spend_ceiling_usd: budgetUsd,
    reasoning_mode: 'disabled'
  }
};
const run = await runBenchmark({ store, benchmark, adapters, namespace: 'DEMO', settings, runId });
const verification = run.status === 'COMPLETED' ? await verifyRun(store, run.id) : null;
const scores = store.filter('scores', (score) => score.run_id === run.id);

console.log(JSON.stringify({
  run_id: run.id,
  status: run.status,
  expected_trials: run.expected_trials,
  completed_trials: run.completed_trials,
  failed_trials: run.failed_trials,
  provider_reported_cost_usd: run.cost_telemetry?.provider_reported_cost_usd ?? budget.spent,
  local_budget_guard_spend_usd: budget.spent,
  this_invocation_spend_usd: budget.invocationSpend,
  budget_limit_usd: budget.limit,
  verification: verification ? { status: verification.status, official_eligible: verification.official_eligible, checks: verification.checks } : null,
  scores
}, null, 2));
