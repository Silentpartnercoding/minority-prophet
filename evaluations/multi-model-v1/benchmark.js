import { BENCHMARK_VERSION } from './src/domain/constants.js';
import { generateDevelopmentWorlds } from './worlds.js';
import { hashObject } from './src/lib/hash.js';

export function developmentBenchmark({ count = 25, seed = 41000 } = {}) {
  const worlds = generateDevelopmentWorlds({ count, seed });
  const manifest = { benchmark_version: BENCHMARK_VERSION, release_state: 'DEVELOPMENT', frozen: false, split: 'development', generator_seed: seed, expected_worlds: count, scenario_families: ['majority_copying'], generated_at: 'deterministic', world_hashes: worlds.map((world) => ({ world_id: world.world_id, world_hash: world.world_hash })) };
  return { manifest: { ...manifest, manifest_hash: hashObject(manifest) }, worlds };
}

export async function persistBenchmark(store, benchmark) {
  await store.insertIfAbsent('benchmark_versions', { id: benchmark.manifest.benchmark_version, ...benchmark.manifest });
  for (const family of benchmark.manifest.scenario_families) await store.insertIfAbsent('scenario_families', { id: family, version: benchmark.manifest.benchmark_version, enabled: true });
  for (const world of benchmark.worlds) {
    await store.insertIfAbsent('worlds', { id: world.world_id, ...world });
    for (const claim of world.claims) await store.insertIfAbsent('claims', { id: `${world.world_id}:${claim.claim_id}`, world_id: world.world_id, ...claim });
    for (const edge of world.provenance_edges) await store.insertIfAbsent('provenance_edges', { id: `${world.world_id}:${edge.parent_claim_id}:${edge.child_claim_id}`, world_id: world.world_id, ...edge });
  }
  return benchmark;
}
