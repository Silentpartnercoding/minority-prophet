# Schemas and contracts

## Benchmark world

Required top-level fields: `benchmark_version`, `world_id`, `world_hash`, `seed`, `question`, evaluator-only `ground_truth`, `claims`, `sources`, `provenance_edges`, `independent_roots`, `scenario_family`, `difficulty`, `consensus_ratio`, and `metadata`.

Claims contain `claim_id`, `text`, `asserted_answer`, `source_id`, `parent_claim_ids`, `derivation_type`, `timestamp`, optional confidence, `direct_observation`, and evaluator-only hidden labels. The public projection removes all hidden data and the ground truth before prompt hashing.

## Model response

Responses contain `answer`, confidence in `[0,1]`, `abstain`, a concise `reasoning_summary`, `evidence_used`, and `independence_assessment`. Private chain-of-thought is not requested or stored.

## Minority Prophet service

Input: claims, sources, provenance edges, and context.

Output: engine version, independent roots, claim clusters, dependency and independence scores, correlation warnings, evidence summary, uncertainty, recommended attention, and an analysis hash. Ground truth and a `correct_answer` field are prohibited.

## Trial identity

The trial key hashes logical run, benchmark version, world, seed, provider, model, model version, condition, and sampling/tool settings. Retries append immutable attempt records. A completed trial key is never called twice during resume.

## Publication gate

Official rows require a VERIFIED run, successful automated verification, a frozen benchmark manifest, complete trials, matching hashes, recorded scorer version, no failed or malformed trials, and non-development worlds. DEMO uses a distinct route, artifact directory, and snapshot namespace.
