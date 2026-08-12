# Architecture

Flow: frozen manifest → deterministic worlds → A/B/C prompt builder → provider adapter → raw response → parser → trial score → paired statistics → verification gate → public-safe snapshot.

World generation happens once. Conditions reference the same `world_id`, `world_hash`, and seed. Only serialized epistemic information changes.

## Boundaries

- `worlds.js`: deterministic family generator and evaluator-only labels.
- `prompts.js`: public projection and A/B/C information boundary.
- `mp.js`: provider-independent epistemic service contract.
- `providers.js`, `http-provider.js`, `provider-registry.js`: normalized adapters.
- `trial-runner.js`, `pipeline.js`: retries, checkpoints, resume, and telemetry.
- `store.js`: atomic snapshots with append-only, deeply frozen records.
- `scoring.js`, `stats.js`: versioned metrics and paired inference.
- `verifier.js`: integrity, completeness, contamination, and publication gates.
- `leaderboard.js`, `artifacts.js`: VERIFIED-by-default queries and research outputs.
- `server.js`: local pages, public-safe APIs, and authenticated operator routes.

Condition D is reserved in the condition enum. Advanced generators should implement prestige attacks, incomplete or fabricated provenance, cycles, multiple false roots, stale evidence, sybils, paraphrase laundering, and conflicting independent evidence behind a feature flag.

Ablations fit the same condition interface: provenance only, root count only, independence only, provenance + reliability, provenance + time, and full MP. Each ablation receives the same world and generates its own prompt/output hash.

The local JSON store deliberately mirrors production entities: benchmark versions, families, worlds, claims, edges, providers, models, model versions, experiments, trials, raw responses, parsed responses, scores, runs, verification records, and snapshots. A production database adapter can replace it without changing benchmark logic.
