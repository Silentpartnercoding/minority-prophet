import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { persistBenchmark } from './benchmark.js';
import { buildLiveToolPrompt, LIVE_TOOL_CONDITIONS } from './live-tool-prompts.js';
import { parseModelResponse } from './parser.js';
import { recordId, trialKey } from './run-ids.js';
import { scoreTrial } from './scoring.js';
import { executeMinorityProphetTool } from './mp-tool-v2.js';
import { hashObject } from './src/lib/hash.js';

function percentile(values, p) {
  if (!values.length) return null;
  const sorted = [...values].sort((a, b) => a - b);
  return sorted[Math.floor((sorted.length - 1) * p)];
}

function summarizeModel(trials, model) {
  const attempts = trials.filter((trial) => trial.model_name === model);
  const cells = attempts.filter((trial) => trial.status === 'COMPLETED');
  const failures = attempts.filter((trial) => trial.status === 'FAILED');
  const correct = cells.filter((trial) => trial.score?.correct === true).length;
  const totalMs = cells.map((trial) => trial.execution_ms);
  const mpMs = cells.map((trial) => trial.live_tool.mp_tool_execution_ms);
  const callDelayMs = cells.map((trial) => trial.live_tool.mcp_startup_to_call_ms).filter(Number.isFinite);
  const sum = (field) => cells.reduce((total, trial) => total + (trial.usage?.[field] ?? 0), 0);
  const cost = cells.reduce((total, trial) => total + (trial.cost_usd ?? 0), 0);
  return {
    model,
    model_versions: [...new Set(cells.map((trial) => trial.model_version))],
    attempted_cells: attempts.length,
    strict_valid_cells: cells.length,
    strict_failed_cells: failures.length,
    parsed_cells: cells.filter((trial) => trial.parse_success).length,
    correct_cells: correct,
    intent_to_treat_truth_recovery: attempts.length ? correct / attempts.length : 0,
    accuracy_given_strict_valid_tool_call: cells.length ? correct / cells.length : 0,
    strict_tool_success_rate: attempts.length ? cells.length / attempts.length : 0,
    successful_tool_calls: cells.reduce((total, trial) => total + trial.live_tool.mp_tool_success_count, 0),
    exact_input_hash_calls: cells.filter((trial) => trial.live_tool.mp_tool_input_hash === trial.expected_tool_input_hash).length,
    strict_failures: failures.map((trial) => ({ world_id: trial.world_id, error: trial.error?.message ?? 'unknown failure' })),
    end_to_end_execution_ms: {
      observed_strict_valid_cells: totalMs.length,
      excludes_strict_failed_cells: failures.length,
      sum: totalMs.reduce((a, b) => a + b, 0),
      mean: totalMs.reduce((a, b) => a + b, 0) / Math.max(1, totalMs.length),
      median: percentile(totalMs, 0.5),
      p95: percentile(totalMs, 0.95),
      max: percentile(totalMs, 1)
    },
    mp_tool_execution_ms: {
      sum: mpMs.reduce((a, b) => a + b, 0),
      mean: mpMs.reduce((a, b) => a + b, 0) / Math.max(1, mpMs.length),
      median: percentile(mpMs, 0.5),
      p95: percentile(mpMs, 0.95),
      max: percentile(mpMs, 1)
    },
    mcp_startup_to_call_ms: {
      mean: callDelayMs.reduce((a, b) => a + b, 0) / Math.max(1, callDelayMs.length),
      median: percentile(callDelayMs, 0.5),
      p95: percentile(callDelayMs, 0.95)
    },
    usage: { input_tokens: sum('input_tokens'), output_tokens: sum('output_tokens'), cached_tokens: sum('cached_tokens') },
    provider_reported_cost_usd: cost
  };
}

async function runCell({ store, runId, adapter, world, settings }) {
  const condition = LIVE_TOOL_CONDITIONS.REQUIRED;
  const prompt = buildLiveToolPrompt(world, condition);
  const key = trialKey({ runId, benchmark_version: world.benchmark_version, world_id: world.world_id, seed: world.seed, provider: adapter.provider, model: adapter.model, model_version: adapter.version, condition, settings });
  const completed = store.find('trials', (trial) => trial.trial_key === key && trial.status === 'COMPLETED');
  if (completed) return completed;
  const attempt = store.filter('trials', (trial) => trial.trial_key === key).length + 1;
  const id = recordId('trial', { key, attempt });
  try {
    const result = await adapter.runModel({
      systemPrompt: prompt.systemPrompt,
      messages: prompt.messages,
      maxTokens: settings.max_tokens,
      requireToolCall: true,
      expectedToolInputHash: prompt.expected_tool_input_hash
    });
    const parsed = parseModelResponse(result.raw);
    const actualVersion = result.model_version ?? adapter.version;
    const rawId = recordId('raw', id);
    const parsedId = recordId('parsed', id);
    const initialize = result.mcp_events.find((event) => event.event === 'initialize');
    const toolCall = result.mcp_events.find((event) => event.event === 'tool_call' && event.success === true);
    const expectedOutputHash = hashObject(executeMinorityProphetTool(prompt.payload.tool_input));
    if (result.mp_tool_output_hash !== expectedOutputHash) throw new Error(`MP output hash mismatch: ${result.mp_tool_output_hash}`);
    const liveTool = {
      mcp_initialize_count: result.mcp_initialize_count,
      mcp_tools_list_count: result.mcp_tools_list_count,
      mp_tool_call_count: result.mp_tool_call_count,
      mp_tool_success_count: result.mp_tool_success_count,
      mp_tool_execution_ms: result.mp_tool_execution_ms,
      mp_tool_input_hash: result.mp_tool_input_hash,
      mp_tool_output_hash: result.mp_tool_output_hash,
      mcp_startup_to_call_ms: initialize && toolCall ? Date.parse(toolCall.timestamp) - Date.parse(initialize.timestamp) : null
    };
    await store.insertIfAbsent('model_versions', { id: `${adapter.provider}:${adapter.model}:${actualVersion}`, provider: adapter.provider, model: adapter.model, version: actualVersion });
    await store.insert('raw_responses', { id: rawId, trial_id: id, provider: adapter.provider, model: adapter.model, raw: result.raw, provider_request_id: result.provider_request_id ?? null, usage: result.usage ?? {}, cost_usd: result.cost_usd ?? null });
    await store.insert('parsed_responses', { id: parsedId, trial_id: id, ...parsed });
    const score = scoreTrial({ condition }, world, parsed);
    return store.insert('trials', {
      id, trial_key: key, run_id: runId, attempt, status: 'COMPLETED', benchmark_version: world.benchmark_version,
      world_id: world.world_id, world_hash: world.world_hash, seed: world.seed, model_provider: adapter.provider,
      model_name: adapter.model, model_version: actualVersion, condition,
      system_prompt_hash: prompt.system_prompt_hash, user_prompt_hash: prompt.user_prompt_hash,
      provenance_graph_hash: prompt.provenance_graph_hash, minority_prophet_output_hash: result.mp_tool_output_hash,
      mp_tool_contract_hash: prompt.mp_tool_contract_hash, expected_tool_input_hash: prompt.expected_tool_input_hash,
      timestamp: new Date().toISOString(), temperature: 0, top_p: 1, max_tokens: settings.max_tokens,
      tool_configuration: settings.tool_configuration, provider_request_id: result.provider_request_id ?? null,
      raw_response_id: rawId, parsed_response_id: parsedId, parse_success: parsed.parse_success,
      usage: result.usage ?? {}, cost_usd: result.cost_usd ?? null, execution_ms: result.execution_ms,
      provider_execution_ms: result.provider_execution_ms ?? null, live_tool: liveTool, score
    });
  } catch (cellError) {
    await store.insert('trials', {
      id, trial_key: key, run_id: runId, attempt, status: 'FAILED', benchmark_version: world.benchmark_version,
      world_id: world.world_id, world_hash: world.world_hash, seed: world.seed, model_provider: adapter.provider,
      model_name: adapter.model, model_version: adapter.version, condition, system_prompt_hash: prompt.system_prompt_hash,
      user_prompt_hash: prompt.user_prompt_hash, provenance_graph_hash: prompt.provenance_graph_hash,
      mp_tool_contract_hash: prompt.mp_tool_contract_hash, expected_tool_input_hash: prompt.expected_tool_input_hash,
      timestamp: new Date().toISOString(), temperature: 0, top_p: 1, max_tokens: settings.max_tokens,
      tool_configuration: settings.tool_configuration, error: { name: cellError.name, message: cellError.message }
    });
    throw cellError;
  }
}

async function runAdapter({ store, runId, adapter, worlds, settings, errors }) {
  let cursor = 0;
  async function worker() {
    while (cursor < worlds.length) {
      const world = worlds[cursor++];
      try { await runCell({ store, runId, adapter, world, settings }); }
      catch (error) { errors.push({ provider: adapter.provider, model: adapter.model, world_id: world.world_id, message: error.message }); }
    }
  }
  await Promise.all(Array.from({ length: settings.provider_concurrency }, () => worker()));
}

export async function runLiveToolBenchmark({ store, benchmark, adapters, runId, settings, protocolCommit }) {
  await persistBenchmark(store, benchmark);
  const completed = store.find('benchmark_runs', (run) => run.id === runId && run.status === 'COMPLETED');
  if (completed) return completed;
  const errors = [];
  const startedAt = new Date().toISOString();
  await Promise.all(adapters.map((adapter) => runAdapter({ store, runId, adapter, worlds: benchmark.worlds, settings, errors })));
  const trials = store.filter('trials', (trial) => trial.run_id === runId && trial.status === 'COMPLETED');
  const record = {
    id: runId,
    status: errors.length ? 'FAILED' : 'COMPLETED',
    namespace: 'DEMO',
    protocol_commit: protocolCommit,
    protocol_version: benchmark.manifest.protocol_version,
    benchmark_version: benchmark.manifest.benchmark_version,
    base_benchmark_version: benchmark.manifest.base_benchmark_version,
    benchmark_manifest_hash: benchmark.manifest.manifest_hash,
    base_benchmark_manifest_hash: benchmark.manifest.base_benchmark_manifest_hash,
    expected_trials: benchmark.worlds.length * adapters.length,
    completed_trials: trials.length,
    failed_trials: errors.length,
    models: adapters.map((adapter) => ({ provider: adapter.provider, model: adapter.model, version: adapter.version })),
    settings,
    started_at: startedAt,
    completed_at: new Date().toISOString(),
    errors
  };
  return store.insert('benchmark_runs', record);
}

export async function buildLiveToolReport({ store, run, benchmark, comparisonStatePath }) {
  const trials = store.filter('trials', (trial) => trial.run_id === run.id);
  const comparison = JSON.parse(await readFile(comparisonStatePath, 'utf8'));
  const priorRun = comparison.benchmark_runs.find((item) => item.status === 'COMPLETED');
  const priorTrials = comparison.trials.filter((trial) => trial.run_id === priorRun.id && trial.condition === 'C_MINORITY_PROPHET');
  const models = run.models.map(({ model }) => {
    const live = summarizeModel(trials, model);
    const prior = priorTrials.filter((trial) => trial.model_name === model);
    const priorCorrect = prior.filter((trial) => trial.score?.correct).length;
    const priorMs = prior.map((trial) => trial.execution_ms);
    return {
      ...live,
      precomputed_comparison: {
        cells: prior.length,
        correct_cells: priorCorrect,
        truth_recovery: prior.length ? priorCorrect / prior.length : 0,
        execution_ms_mean: priorMs.reduce((a, b) => a + b, 0) / Math.max(1, priorMs.length),
        concrete_model_versions: [...new Set(prior.map((trial) => trial.model_version))]
      }
    };
  });
  const reportBase = {
    schema: 'mp-epistemic-live-tool-report.v1',
    status: run.status,
    namespace: run.namespace,
    claim_boundary: 'Known constructed development worlds and a post-result native-MCP transport extension; not hidden evaluation, independent confirmation, or controlled API-serving latency.',
    run_id: run.id,
    protocol_version: benchmark.manifest.protocol_version,
    protocol_commit: run.protocol_commit,
    manifest_hash: benchmark.manifest.manifest_hash,
    base_benchmark_manifest_hash: benchmark.manifest.base_benchmark_manifest_hash,
    expected_trials: run.expected_trials,
    completed_trials: run.completed_trials,
    failed_trials: run.failed_trials,
    attempted_trials: trials.length,
    grid_complete: trials.length === run.expected_trials,
    strict_validation_status: run.failed_trials === 0 ? 'PASSED' : 'FAILED',
    wall_clock_ms: Date.parse(run.completed_at) - Date.parse(run.started_at),
    models,
    limitations: [
      'world answers and prior A/B/C outcomes were known before this transport extension',
      'one live-tool call per model-world cell',
      'subscription CLI telemetry is not controlled API cost or serving latency',
      'the required lane measures provisioned-tool execution, not voluntary tool adoption',
      'the live MCP server ran locally over stdio without network transport',
      'per-call latency, token, and provider-cost summaries exclude strict-failed cells because the provider adapters rejected those responses before returning normalized telemetry; wall clock includes them'
    ]
  };
  return { ...reportBase, report_hash: hashObject(reportBase) };
}

export async function writeLiveToolReport(report, outputDirectory) {
  await mkdir(outputDirectory, { recursive: true });
  await writeFile(join(outputDirectory, 'result.json'), `${JSON.stringify(report, null, 2)}\n`);
  const lines = [
    '# Epistemic Live Tool v1 — native MCP transport extension', '',
    `Status: **${report.status}**`, '', `Boundary: ${report.claim_boundary}`, '',
    `Wall clock: ${(report.wall_clock_ms / 1000).toFixed(3)} seconds`, '',
    '| Model | Correct | Live accuracy | Precomputed accuracy | Live mean | Precomputed mean | MP compute mean | Tool calls | Provider estimate |',
    '|---|---:|---:|---:|---:|---:|---:|---:|---:|',
    ...report.models.map((row) => `| ${row.model_versions.join(', ')} | ${row.correct_cells}/${row.attempted_cells} | ${(100 * row.intent_to_treat_truth_recovery).toFixed(3)}% | ${(100 * row.precomputed_comparison.truth_recovery).toFixed(3)}% | ${(row.end_to_end_execution_ms.mean / 1000).toFixed(3)} s | ${(row.precomputed_comparison.execution_ms_mean / 1000).toFixed(3)} s | ${row.mp_tool_execution_ms.mean.toFixed(3)} ms | ${row.strict_valid_cells}/${row.attempted_cells} | $${row.provider_reported_cost_usd.toFixed(6)} |`),
    '', 'The live condition includes MCP discovery, argument construction, local tool execution, receipt transport, post-tool model reasoning, and final response generation.', ''
  ];
  await writeFile(join(outputDirectory, 'result.md'), lines.join('\n'));
}
