import { generateDiscoveryWorlds } from './provenance-discovery-worlds.js';
import { hashObject } from './src/lib/hash.js';

export const DISCOVERY_PROTOCOL_VERSION = 'provenance-discovery-candidate-v2';

export function provenanceDiscoveryBenchmark() {
  const worlds = generateDiscoveryWorlds();
  const base = {
    protocol_version: DISCOVERY_PROTOCOL_VERSION,
    namespace: 'DEMO',
    split: 'candidate_development',
    seed: 8_120_026,
    world_count: worlds.length,
    families: [...new Set(worlds.map((world) => world.family))],
    models: ['gpt-5.6-sol', 'claude-sonnet-5'],
    model_tools: 'disabled',
    hidden_fields: ['ground_truth', 'parent_by_document', 'root_by_document', 'asserted_answer'],
    primary_endpoint: 'macro mean pairwise same-origin F1',
    secondary_endpoints: ['pairwise precision', 'pairwise recall', 'root-count absolute error', 'downstream truth recovery', 'appropriate abstention', 'latency', 'tokens', 'provider-reported cost'],
    candidate_engine: 'mp-provenance-inference-candidate-v2',
    deterministic_comparator: 'exp008-inference-comparator-js-v1',
    world_hashes: worlds.map((world) => ({ world_id: world.world_id, world_hash: world.world_hash }))
  };
  return { manifest: { ...base, manifest_hash: hashObject(base) }, worlds };
}

export function discoveryJobs(adapters, worlds) {
  return adapters.flatMap((adapter) => worlds.map((world) => ({
    adapter,
    world,
    key: `${adapter.provider}:${adapter.model}:${world.world_id}`
  })));
}
