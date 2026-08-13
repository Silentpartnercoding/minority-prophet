import { liftBenchmarkV11 } from './lift-benchmark-v11.js';
import { LIVE_TOOL_CONDITIONS } from './live-tool-prompts.js';
import { MP_TOOL_CONTRACT_HASH } from './mp-tool-v2.js';
import { hashObject } from './src/lib/hash.js';

export const LIVE_TOOL_PROTOCOL_VERSION = 'epistemic-live-tool-v1';

export function liveToolBenchmark() {
  const base = liftBenchmarkV11();
  const manifestBase = {
    protocol_version: LIVE_TOOL_PROTOCOL_VERSION,
    namespace: 'DEMO',
    benchmark_version: '0.3.0-lift-candidate-live-tool-v1',
    base_benchmark_version: base.manifest.benchmark_version,
    base_benchmark_manifest_hash: base.manifest.manifest_hash,
    world_count: base.worlds.length,
    scenario_families: base.manifest.scenario_families,
    world_hashes: base.manifest.world_hashes,
    models: base.manifest.model_grid,
    condition: LIVE_TOOL_CONDITIONS.REQUIRED,
    calls_per_model_world: 1,
    required_successful_tool_calls_per_cell: 1,
    response_max_tokens: 500,
    provider_concurrency: 2,
    mp_tool_contract_hash: MP_TOOL_CONTRACT_HASH,
    transport: 'native_cli_stdio_mcp',
    general_tools: 'disabled',
    external_retrieval: false,
    comparison_run: 'epistemic-lift-v1.1-raw-capture',
    primary_endpoints: [
      'intent_to_treat_truth_recovery',
      'live_tool_call_success_rate',
      'end_to_end_execution_ms',
      'mp_tool_execution_ms',
      'input_output_cached_tokens',
      'provider_reported_cost_when_available'
    ]
  };
  return { manifest: { ...manifestBase, manifest_hash: hashObject(manifestBase) }, worlds: base.worlds };
}
