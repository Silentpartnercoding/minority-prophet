import { CONDITIONS, LIFT_BENCHMARK_VERSION, LIFT_MP_ENGINE_VERSION, LIFT_PROMPT_VERSION } from './src/domain/constants.js';
import { hashObject } from './src/lib/hash.js';
import { generateLiftWorlds, LIFT_SCENARIO_FAMILIES } from './lift-worlds.js';
import { MP_TOOL_CONTRACT_HASH } from './mp-tool-v2.js';

export const LIFT_SEED = 1_730_000;
export const LIFT_REPETITIONS = 4;
export const LIFT_WORLD_COUNT = LIFT_SCENARIO_FAMILIES.length * LIFT_REPETITIONS;
export const LIFT_MODEL_GRID = Object.freeze([
  { provider: 'openai-codex-cli', requested_model: 'gpt-5.6-sol', effort: 'medium' },
  { provider: 'anthropic-claude-cli', requested_model: 'sonnet', effort: 'medium' }
]);

export const CONDITION_PERMUTATIONS = Object.freeze([
  [CONDITIONS.BASELINE, CONDITIONS.PROVENANCE, CONDITIONS.MINORITY_PROPHET],
  [CONDITIONS.BASELINE, CONDITIONS.MINORITY_PROPHET, CONDITIONS.PROVENANCE],
  [CONDITIONS.PROVENANCE, CONDITIONS.BASELINE, CONDITIONS.MINORITY_PROPHET],
  [CONDITIONS.PROVENANCE, CONDITIONS.MINORITY_PROPHET, CONDITIONS.BASELINE],
  [CONDITIONS.MINORITY_PROPHET, CONDITIONS.BASELINE, CONDITIONS.PROVENANCE],
  [CONDITIONS.MINORITY_PROPHET, CONDITIONS.PROVENANCE, CONDITIONS.BASELINE]
]);

export function conditionOrderFor(world, adapter) {
  const ordinal = Number(world.world_id.match(/(\d+)$/)?.[1] ?? 1) - 1;
  const modelOffset = Number.parseInt(hashObject({ provider: adapter.provider, model: adapter.model }).slice(-8), 16) % CONDITION_PERMUTATIONS.length;
  return CONDITION_PERMUTATIONS[(ordinal + modelOffset) % CONDITION_PERMUTATIONS.length];
}

export function liftBenchmark() {
  const worlds = generateLiftWorlds({ repetitions: LIFT_REPETITIONS, seed: LIFT_SEED });
  const manifest = {
    benchmark_version: LIFT_BENCHMARK_VERSION,
    release_state: 'FROZEN_CANDIDATE_DEVELOPMENT',
    frozen: true,
    official_leaderboard_eligible: false,
    split: 'candidate_development',
    generator_seed: LIFT_SEED,
    repetitions_per_family: LIFT_REPETITIONS,
    expected_worlds: LIFT_WORLD_COUNT,
    scenario_families: LIFT_SCENARIO_FAMILIES,
    conditions: [CONDITIONS.BASELINE, CONDITIONS.PROVENANCE, CONDITIONS.MINORITY_PROPHET],
    prompt_version: LIFT_PROMPT_VERSION,
    mp_engine_version: LIFT_MP_ENGINE_VERSION,
    mp_tool_contract_hash: MP_TOOL_CONTRACT_HASH,
    model_grid: LIFT_MODEL_GRID,
    sampling: { temperature: 0, top_p: 1, max_tokens: 500, calls_per_model_world_condition: 1, maximum_attempts_per_cell: 2 },
    execution_order: 'six-permutation deterministic counterbalance by model and world',
    primary_endpoint: 'paired truth-recovery difference C minus B within each preregistered model',
    success_rule: 'each preregistered model must show C-B >= 0.15 and exact paired two-sided p < 0.05; adverse and null results remain valid',
    generated_at: 'deterministic',
    world_hashes: worlds.map((world) => ({ world_id: world.world_id, world_hash: world.world_hash }))
  };
  return { manifest: { ...manifest, manifest_hash: hashObject(manifest) }, worlds };
}
