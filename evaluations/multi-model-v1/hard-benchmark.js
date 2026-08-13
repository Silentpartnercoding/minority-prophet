import { HARD_BENCHMARK_VERSION } from './src/domain/constants.js';
import { HARD_SCENARIO_FAMILIES, generateHardWorlds } from './hard-worlds.js';
import { hashObject } from './src/lib/hash.js';

export function hardBenchmark({ repetitions = 1, seed = 880_000 } = {}) {
  const worlds = generateHardWorlds({ repetitions, seed });
  const manifest = {
    benchmark_version: HARD_BENCHMARK_VERSION,
    release_state: 'HARD_DEVELOPMENT',
    frozen: false,
    split: 'hard_development',
    generator_seed: seed,
    repetitions,
    expected_worlds: worlds.length,
    expected_abstention_worlds: worlds.filter((world) => world.expected_disposition === 'ABSTAIN').length,
    scenario_families: [...HARD_SCENARIO_FAMILIES],
    design: 'same-world A/B/C; baseline hides structured evidence metadata; B exposes declared metadata; C adds untrusted structural analysis',
    generated_at: 'deterministic',
    world_hashes: worlds.map((world) => ({ world_id: world.world_id, world_hash: world.world_hash }))
  };
  return { manifest: { ...manifest, manifest_hash: hashObject(manifest) }, worlds };
}
