#!/usr/bin/env node
import { join } from 'node:path';
import { createAdapter } from './provider-registry.js';
import { openStore, PROJECT_ROOT } from './operations.js';
import { runTrial } from './trial-runner.js';
import { aggregateCondition } from './scoring.js';
import { pairedGain } from './stats.js';
import { hashObject } from './src/lib/hash.js';
import { buildRealTestPrompt, REAL_CONDITIONS } from './real-test-prompts.js';
import { realTestWorlds } from './real-test-worlds.js';

if (!process.env.OPENROUTER_API_KEY) throw new Error('OPENROUTER_API_KEY is required');

const protocolVersion = 'openrouter-balanced-b-neutral-mp-v1';
const conditions = [REAL_CONDITIONS.PROVENANCE, REAL_CONDITIONS.NEUTRAL_INDEX, REAL_CONDITIONS.MINORITY_PROPHET];
const conditionOrders = [
  conditions,
  [conditions[0], conditions[2], conditions[1]],
  [conditions[1], conditions[0], conditions[2]],
  [conditions[1], conditions[2], conditions[0]],
  [conditions[2], conditions[0], conditions[1]],
  [conditions[2], conditions[1], conditions[0]]
];
const modelConfigs = [
  { provider: 'openrouter', model: 'openai/gpt-4.1' },
  { provider: 'openrouter', model: 'anthropic/claude-sonnet-4.6', request_body: { reasoning: { enabled: false, exclude: true } } },
  { provider: 'openrouter', model: 'google/gemini-2.5-flash', request_body: { reasoning: { enabled: false, exclude: true } } }
];
const settings = {
  temperature: 0,
  top_p: 1,
  max_tokens: 800,
  retry_parse_failures: true,
  tool_configuration: {
    regime: 'closed_world',
    allowed_tools: [],
    external_retrieval: false,
    paid_api_diagnostic: true,
    reasoning_mode: 'disabled'
  }
};
const worlds = realTestWorlds();
const manifestHash = hashObject({ protocolVersion, world_hashes: worlds.map((world) => world.world_hash), conditions, modelConfigs, settings });
const runId = `${protocolVersion}:${manifestHash}`;
const statePath = join(PROJECT_ROOT, 'data', 'runtime', 'openrouter-real-test-state.json');
const store = await openStore(statePath);
const budgetLimit = Number(process.env.MP_OPENROUTER_REAL_BUDGET_USD ?? 3.75);
if (!Number.isFinite(budgetLimit) || budgetLimit <= 0 || budgetLimit > 6) throw new Error('MP_OPENROUTER_REAL_BUDGET_USD must be greater than 0 and no more than 6');

async function creditStatus() {
  const response = await fetch('https://openrouter.ai/api/v1/credits', { headers: { authorization: `Bearer ${process.env.OPENROUTER_API_KEY}` } });
  if (!response.ok) throw new Error(`Unable to read OpenRouter credits: HTTP ${response.status}`);
  const body = await response.json();
  const data = body.data ?? body;
  const totalCredits = Number(data.total_credits ?? data.totalCredits ?? 0);
  const totalUsage = Number(data.total_usage ?? data.totalUsage ?? 0);
  return { total_credits: totalCredits, total_usage: totalUsage, balance: totalCredits - totalUsage };
}

const creditsBefore = await creditStatus();
if (creditsBefore.balance < Math.min(1, budgetLimit)) throw new Error(`Insufficient OpenRouter balance: $${creditsBefore.balance.toFixed(6)}`);
const priorSpend = store.filter('trials', (trial) => trial.run_id === runId).reduce((sum, trial) => sum + Number(trial.cost_usd ?? 0), 0);
const budget = { limit: Math.min(budgetLimit, creditsBefore.balance), spent: priorSpend, invocation: 0, calls: 0, reserve: 0.08 };
const totalCells = worlds.length * modelConfigs.length * conditions.length;

const adapters = modelConfigs.map((config) => {
  const adapter = createAdapter(config);
  return {
    provider: adapter.provider,
    model: adapter.model,
    version: adapter.version,
    async runModel(request) {
      if (budget.spent + budget.reserve > budget.limit) throw new Error(`OpenRouter real-test budget guard reached at $${budget.spent.toFixed(6)}`);
      const result = await adapter.runModel(request);
      const cost = Number(result.cost_usd ?? NaN);
      if (!Number.isFinite(cost) || cost < 0) throw new Error('OpenRouter returned invalid cost telemetry');
      budget.spent += cost;
      budget.invocation += cost;
      budget.calls += 1;
      if (budget.calls === 1 || budget.calls % 10 === 0) {
        process.stderr.write(`[openrouter-real-test] ${budget.calls} new calls; $${budget.spent.toFixed(6)} cumulative run spend\n`);
      }
      return result;
    }
  };
});

let executionOrder = 0;
for (let modelIndex = 0; modelIndex < adapters.length; modelIndex += 1) {
  const adapter = adapters[modelIndex];
  for (let worldIndex = 0; worldIndex < worlds.length; worldIndex += 1) {
      const world = worlds[worldIndex];
      const order = conditionOrders[(worldIndex + modelIndex * 2) % conditionOrders.length];
      for (const condition of order) {
      const priorTrials = store.filter('trials', (trial) => trial.run_id === runId && trial.world_id === world.world_id && trial.model_name === adapter.model && trial.condition === condition);
      if (priorTrials.some((trial) => trial.status === 'COMPLETED') || priorTrials.length >= 2) continue;
      for (let attempt = priorTrials.length + 1; attempt <= 2; attempt += 1) {
        executionOrder += 1;
        try {
          const trial = await runTrial({ store, runId, adapter, world, condition, settings, executionOrder, promptBuilder: buildRealTestPrompt });
          if (trial.status === 'COMPLETED') break;
        } catch (error) {
          process.stderr.write(`[openrouter-real-test] ${adapter.model} ${world.world_id} ${condition} attempt ${attempt} failed: ${error.message}\n`);
          if (String(error.message).includes('budget guard')) throw error;
        }
      }
    }
  }
}

function latestTrials() {
  const latest = new Map();
  for (const trial of store.filter('trials', (item) => item.run_id === runId)) {
    const key = `${trial.model_name}|${trial.world_id}|${trial.condition}`;
    const prior = latest.get(key);
    if (!prior || trial.attempt > prior.attempt) latest.set(key, trial);
  }
  return [...latest.values()];
}

function cohort(world) {
  if (world.expected_disposition === 'ABSTAIN') return 'abstention';
  return world.metadata.false_majority ? 'false_majority' : 'correct_majority';
}

const trials = latestTrials();
const byWorld = new Map(worlds.map((world) => [world.world_id, world]));
const allRunAttempts = store.filter('trials', (trial) => trial.run_id === runId);
const percentile = (values, proportion) => {
  if (!values.length) return null;
  const ordered = [...values].sort((left, right) => left - right);
  return ordered[Math.min(ordered.length - 1, Math.ceil(ordered.length * proportion) - 1)];
};
const modelResults = {};
for (const { model } of modelConfigs) {
  const modelTrials = trials.filter((trial) => trial.model_name === model && trial.status === 'COMPLETED');
  const items = modelTrials.map((trial) => trial.score);
  const byCondition = Object.fromEntries(conditions.map((condition) => [condition, aggregateCondition(items.filter((item) => item.condition === condition))]));
  const modelLatest = trials.filter((trial) => trial.model_name === model);
  const strictItems = modelLatest.map((trial) => ({
    eligible: true,
    correct: trial.status === 'COMPLETED' && trial.score?.eligible === true && trial.score.correct === true,
    world_id: trial.world_id,
    condition: trial.condition
  }));
  const cohortRates = Object.fromEntries(conditions.map((condition) => [condition, Object.fromEntries(['false_majority', 'correct_majority', 'abstention'].map((name) => {
    const selected = modelLatest.filter((trial) => trial.condition === condition && cohort(byWorld.get(trial.world_id)) === name);
    const correct = selected.filter((trial) => trial.status === 'COMPLETED' && trial.score?.eligible && trial.score.correct).length;
    return [name, { correct, attempted: selected.length, rate: selected.length ? Number((correct / selected.length).toFixed(6)) : null }];
  }))]));
  const pick = (condition) => items.filter((item) => item.condition === condition);
  const strictPick = (condition) => strictItems.filter((item) => item.condition === condition);
  const timingAndCost = Object.fromEntries(conditions.map((condition) => {
    const paidAttempts = allRunAttempts.filter((trial) => trial.model_name === model && trial.condition === condition && Number.isFinite(Number(trial.cost_usd)));
    const latencies = paidAttempts.map((trial) => Number(trial.execution_ms)).filter(Number.isFinite);
    const totalCost = paidAttempts.reduce((sum, trial) => sum + Number(trial.cost_usd ?? 0), 0);
    return [condition, {
      paid_attempts: paidAttempts.length,
      median_latency_ms: percentile(latencies, 0.5),
      p95_latency_ms: percentile(latencies, 0.95),
      total_cost_usd: Number(totalCost.toFixed(8)),
      average_cost_usd: paidAttempts.length ? Number((totalCost / paidAttempts.length).toFixed(8)) : null,
      input_tokens: paidAttempts.reduce((sum, trial) => sum + Number(trial.usage?.input_tokens ?? 0), 0),
      output_tokens: paidAttempts.reduce((sum, trial) => sum + Number(trial.usage?.output_tokens ?? 0), 0)
    }];
  }));
  modelResults[model] = {
    valid_response_metrics: byCondition,
    strict_accuracy: Object.fromEntries(conditions.map((condition) => {
      const selected = strictPick(condition);
      const correct = selected.filter((item) => item.correct).length;
      return [condition, { correct, attempted: selected.length, rate: Number((correct / selected.length).toFixed(6)) }];
    })),
    strict_cohort_rates: cohortRates,
    timing_and_cost: timingAndCost,
    neutral_over_provenance: pairedGain(pick(REAL_CONDITIONS.PROVENANCE), pick(REAL_CONDITIONS.NEUTRAL_INDEX)),
    mp_over_neutral: pairedGain(pick(REAL_CONDITIONS.NEUTRAL_INDEX), pick(REAL_CONDITIONS.MINORITY_PROPHET)),
    mp_over_provenance: pairedGain(pick(REAL_CONDITIONS.PROVENANCE), pick(REAL_CONDITIONS.MINORITY_PROPHET)),
    strict_neutral_over_provenance: pairedGain(strictPick(REAL_CONDITIONS.PROVENANCE), strictPick(REAL_CONDITIONS.NEUTRAL_INDEX)),
    strict_mp_over_neutral: pairedGain(strictPick(REAL_CONDITIONS.NEUTRAL_INDEX), strictPick(REAL_CONDITIONS.MINORITY_PROPHET)),
    strict_mp_over_provenance: pairedGain(strictPick(REAL_CONDITIONS.PROVENANCE), strictPick(REAL_CONDITIONS.MINORITY_PROPHET))
  };
}

const completedCells = trials.filter((trial) => trial.status === 'COMPLETED').length;
const attemptedCells = trials.length;
const parseFailureCells = trials.filter((trial) => trial.status === 'FAILED' && trial.error?.name === 'StructuredResponseError').length;
const baseHashesMatch = modelConfigs.every(({ model }) => worlds.every((world) => {
  const selected = trials.filter((trial) => trial.model_name === model && trial.world_id === world.world_id);
  return selected.length === conditions.length && new Set(selected.map((trial) => trial.epistemic_base_hash)).size === 1;
}));
const creditsAfter = await creditStatus();
const report = {
  label: 'local balanced diagnostic; not an independent confirmatory result or official leaderboard submission',
  protocol_version: protocolVersion,
  run_id: runId,
  manifest_hash: manifestHash,
  worlds: worlds.length,
  conditions,
  models: modelConfigs.map(({ model }) => model),
  expected_cells: totalCells,
  attempted_cells: attemptedCells,
  valid_response_cells: completedCells,
  schema_failure_cells: parseFailureCells,
  unattempted_cells: totalCells - attemptedCells,
  verification: {
    fully_attempted: attemptedCells === totalCells,
    identical_epistemic_base_across_conditions: baseHashesMatch,
    balance: { false_majority_answerable: 12, correct_majority_answerable: 12, abstention: 4 }
  },
  cost: {
    provider_reported_run_spend_usd: Number(budget.spent.toFixed(8)),
    this_invocation_spend_usd: Number(budget.invocation.toFixed(8)),
    budget_limit_usd: budget.limit,
    account_balance_before_usd: Number(creditsBefore.balance.toFixed(8)),
    account_balance_after_usd: Number(creditsAfter.balance.toFixed(8))
  },
  results: modelResults
};
console.log(JSON.stringify(report, null, 2));
