export function assertBenchmarkWritable(manifest) {
  if (manifest.frozen) throw new Error(`Benchmark ${manifest.benchmark_version} is frozen and immutable`);
  return true;
}

export function freezeManifest(manifest, frozenAt) {
  if (manifest.frozen) return manifest;
  return Object.freeze({ ...manifest, frozen: true, release_state: 'FROZEN', frozen_at: frozenAt });
}
