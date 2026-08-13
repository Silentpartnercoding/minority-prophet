import { buildPrompt } from './prompts.js';
import { parseModelResponse } from './parser.js';
import { scoreTrial } from './scoring.js';
import { recordId, trialKey } from './run-ids.js';

export async function runTrial({ store, runId, adapter, world, condition, settings, executionOrder = null }) {
  const key = trialKey({ runId, benchmark_version: world.benchmark_version, world_id: world.world_id, seed: world.seed, provider: adapter.provider, model: adapter.model, model_version: adapter.version, condition, settings });
  const completed = store.find('trials', (trial) => trial.trial_key === key && trial.status === 'COMPLETED');
  if (completed) return completed;
  const attempt = store.filter('trials', (trial) => trial.trial_key === key).length + 1;
  const id = recordId('trial', { key, attempt });
  const prompt = buildPrompt(world, condition);
  const started = Date.now();
  try {
    const result = await adapter.runModel({ condition, systemPrompt: prompt.systemPrompt, messages: prompt.messages, tools: prompt.tools, temperature: settings.temperature, topP: settings.top_p, seed: world.seed, maxTokens: settings.max_tokens });
    const parsed = parseModelResponse(result.raw);
    const actualModelVersion = result.model_version ?? adapter.version;
    await store.insertIfAbsent('model_versions', { id: `${adapter.provider}:${adapter.model}:${actualModelVersion}`, provider: adapter.provider, model: adapter.model, version: actualModelVersion });
    const rawId = recordId('raw', id);
    const parsedId = recordId('parsed', id);
    await store.insert('raw_responses', { id: rawId, trial_id: id, provider: adapter.provider, model: adapter.model, raw: result.raw, provider_request_id: result.provider_request_id ?? null, usage: result.usage ?? {}, cost_usd: result.cost_usd ?? null });
    await store.insert('parsed_responses', { id: parsedId, trial_id: id, ...parsed });
    const score = scoreTrial({ condition }, world, parsed);
    const retryableParseFailure = settings.retry_parse_failures === true && !parsed.parse_success;
    return store.insert('trials', {
      id, trial_key: key, run_id: runId, attempt, status: retryableParseFailure ? 'FAILED' : 'COMPLETED', benchmark_version: world.benchmark_version,
      world_id: world.world_id, world_hash: world.world_hash, seed: world.seed, model_provider: adapter.provider,
      model_name: adapter.model, model_version: actualModelVersion, condition,
      system_prompt_hash: prompt.system_prompt_hash, user_prompt_hash: prompt.user_prompt_hash,
      epistemic_base_hash: prompt.epistemic_base_hash ?? null, mp_tool_contract_hash: prompt.mp_tool_contract_hash ?? null,
      provenance_graph_hash: prompt.provenance_graph_hash, minority_prophet_output_hash: prompt.minority_prophet_output_hash,
      timestamp: new Date().toISOString(), temperature: settings.temperature, top_p: settings.top_p,
      max_tokens: settings.max_tokens, tool_configuration: settings.tool_configuration ?? { regime: 'closed_world', allowed_tools: prompt.tools }, execution_order: executionOrder, provider_request_id: result.provider_request_id ?? null,
      raw_response_id: rawId, parsed_response_id: parsedId, parse_success: parsed.parse_success,
      error: retryableParseFailure ? { name: 'StructuredResponseError', message: parsed.parse_error ?? 'Response did not match the required schema' } : null,
      usage: result.usage ?? {}, cost_usd: result.cost_usd ?? null, execution_ms: result.execution_ms ?? Date.now() - started, score
    });
  } catch (error) {
    await store.insert('trials', { id, trial_key: key, run_id: runId, attempt, status: 'FAILED', benchmark_version: world.benchmark_version, world_id: world.world_id, world_hash: world.world_hash, seed: world.seed, model_provider: adapter.provider, model_name: adapter.model, model_version: adapter.version, condition, system_prompt_hash: prompt.system_prompt_hash, user_prompt_hash: prompt.user_prompt_hash, epistemic_base_hash: prompt.epistemic_base_hash ?? null, mp_tool_contract_hash: prompt.mp_tool_contract_hash ?? null, provenance_graph_hash: prompt.provenance_graph_hash, minority_prophet_output_hash: prompt.minority_prophet_output_hash, timestamp: new Date().toISOString(), temperature: settings.temperature, top_p: settings.top_p, max_tokens: settings.max_tokens, tool_configuration: settings.tool_configuration ?? { regime: 'closed_world', allowed_tools: prompt.tools }, execution_order: executionOrder, provider_request_id: null, error: { name: error.name, message: error.message }, execution_ms: Date.now() - started });
    throw error;
  }
}
