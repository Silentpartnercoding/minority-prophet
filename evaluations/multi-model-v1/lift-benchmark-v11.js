import { hashObject } from './src/lib/hash.js';
import { liftBenchmark } from './lift-benchmark.js';

export const LIFT_V11_PROTOCOL_VERSION = 'epistemic-lift-v1.1-raw-capture';

export function liftBenchmarkV11() {
  const base = liftBenchmark();
  const { manifest_hash: ignored, ...baseManifest } = base.manifest;
  const manifest = {
    ...baseManifest,
    release_state: 'FROZEN_TRANSPORT_REPLICATION_DEVELOPMENT',
    protocol_version: LIFT_V11_PROTOCOL_VERSION,
    predecessor_manifest_hash: base.manifest.manifest_hash,
    response_transport: {
      provider_structured_output_enforcement: false,
      model_response_capture: 'one raw final response',
      parsing: 'versioned local parser after capture',
      schema_repair_model: false,
      parse_failure_policy: 'preserve and invalidate; never silently score as an ordinary wrong answer'
    },
    sampling: { ...base.manifest.sampling, maximum_attempts_per_cell: 2, formatting_retries: 0, transport_retries: 1 },
    interpretation: 'post-failure full replication on the unchanged development worlds; not an independent confirmatory test'
  };
  return { manifest: { ...manifest, manifest_hash: hashObject(manifest) }, worlds: base.worlds };
}
