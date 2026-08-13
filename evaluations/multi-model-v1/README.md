# Minority Prophet Evaluation

> **Research lane:** Exploratory/imported development harness. Its DEMO runs,
> model outputs, and internal reviews are not canonical records, independent
> validation, or evidence of real-world provenance recovery. Promotion must
> follow the repository-wide registration and evidence-alignment rules.

A local, dependency-free Node.js vertical slice for measuring truth recovery under correlated false consensus without conflating model intelligence, provenance availability, and Minority Prophet value-add.

## What works

- One deterministic `majority_copying` generator with 25 development worlds.
- The exact same world and seed under A (claims), B (claims + provenance), and C (B + Minority Prophet analysis).
- Provider-neutral adapters: deterministic development models, OpenAI-compatible endpoints, Anthropic, and Google.
- Raw responses separated from normalized responses; invalid JSON is a parse failure, not a wrong answer.
- Append-only, deeply immutable local persistence covering all required logical tables.
- Resumable trials, retry-safe identities, hashes, model versions, token/cost telemetry, and immutable history.
- Transparent MP Score components, Wilson intervals, paired gains, gain intervals, and paired significance.
- Strict DEMO/VERIFIED gates. Development models never enter the official leaderboard.
- Public leaderboard, model page, run page, methodology, public-safe API, and local operator console.
- JSON/CSV research artifacts, statistics, plots data, reproducibility metadata, and publication tables.

## Run locally

Run `npm test`, then `npm run run:demo`, `npm run publish:local`, and `npm run dev`.

For a bounded real-model pilot through authenticated subscription CLIs, run `npm run run:pilot -- 2`. The pilot uses an empty temporary directory, disables provider tools, forbids retrieval, and labels every result DEMO. It does not use API keys or silently invoke paid API endpoints.

Open `http://127.0.0.1:4173/leaderboard?namespace=DEMO`. The official `/leaderboard` remains empty until a frozen, non-development benchmark and eligible VERIFIED run exist.

No paid provider is called by these commands. Commercial adapters require explicit configuration, enabling, and credentials. Secret values are never persisted.

## Experimental control

Every trial records benchmark/world/model versions, world and prompt hashes, provenance and MP-analysis hashes, seed, sampling settings, tool configuration, provider request ID, timing, token usage, and cost. Hidden ground-truth fields are stripped before prompt construction and tested for leakage.

The MP engine reports root structure, clusters, dependencies, independence weights, correlation warnings, uncertainty, and attention targets. It does not return a ground-truth label.

## MP Score v1

`0.45 truth recovery + 0.25 false-consensus resistance + 0.15 minority recovery + 0.10 calibration + 0.05 abstention quality`

This formula is versioned and exposes every component. In a benchmark consisting only of false-majority worlds, truth recovery, resistance, and minority recovery are correlated; later scenario families make those dimensions separable.

## Local admin API

Set `MP_ADMIN_TOKEN`, then use authenticated POST requests to `/api/admin/start-demo` or `/api/admin/publish-demo`.

Public APIs default to VERIFIED data. DEMO data uses `/api/demo/leaderboard`. Hidden worlds and raw responses are never returned by public routes.

This is the first vertical slice, not scientifically frozen Benchmark v1. See `BENCHMARK_V1_FREEZE.md`. Local publication is implemented; production deployment to minorityprophet.org is intentionally not performed.
