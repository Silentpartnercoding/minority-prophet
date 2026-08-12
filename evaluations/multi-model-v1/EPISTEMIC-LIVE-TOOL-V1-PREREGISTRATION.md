# Epistemic Live Tool v1 — preregistration

Status: **FROZEN before benchmark model execution — 2026-08-11 America/Los_Angeles**

Manifest: `sha256:a61cd271d5eb0642093d63157726a2a3aeca2a01798ae50260cdc42e48330933`

Two non-benchmark transport probes using invented claims were executed before freeze solely to verify native MCP connectivity. They are excluded from every endpoint and contain none of the 32 benchmark worlds.

This is a post-result transport extension of Epistemic Lift v1.1. The 32 development worlds and prior A/B/C outcomes are already known. It cannot provide independent confirmation or a new causal estimate of MP lift.

## Question

What accuracy, latency, tool-call reliability, token use, and provider-reported cost result when the same model must discover and invoke Minority Prophet as a real local MCP tool instead of receiving a precomputed receipt?

## Fixed design

- Worlds: the exact 32-world `0.3.0-lift-candidate` set pinned by the v1.1 manifest.
- Models: `gpt-5.6-sol` through Codex CLI and `sonnet` through Claude CLI, medium effort.
- Cells: 32 worlds × 2 models × one required-live-tool condition = 64.
- One model call per cell; no response retry for parse failure.
- Provider concurrency: two per model, with both model adapters running concurrently.
- Sampling request: temperature 0, top-p 1, maximum 500 final-response tokens where the CLI honors those fields.
- Tool transport: native stdio MCP configured independently for each isolated temporary working directory.
- Available tool surface: only `analyze_evidence_structure`; shell, files, web, external retrieval, and all unrelated tools are prohibited.
- The model must call MP exactly once using the complete B-visible claim/source/provenance/context packet supplied in the prompt.
- The harness validates the actual MCP telemetry input hash and recomputes the expected deterministic output hash.
- MP receives no hidden label and returns no recommended or correct answer.

## End-to-end timing boundary

The primary elapsed time begins immediately before spawning the provider CLI and ends after its final response is captured. It therefore includes CLI startup, MCP initialization and tool listing, model tool selection and argument construction, local MP execution, tool-result transport, post-tool model reasoning, and final response generation.

MP's own execution time is separately measured inside the MCP server. `MCP initialize → tool call` is descriptive because it combines model reasoning and transport delay.

## Endpoints

Report without suppression:

- intent-to-treat truth recovery, counting parse failures as incorrect;
- successful exact-input MP calls / 32;
- mean, median, p95, maximum, and cumulative end-to-end time;
- mean, median, p95, maximum, and cumulative MP execution time;
- MCP initialize-to-call delay;
- input, output, cached, and cache-creation tokens when reported;
- provider-reported dollar estimate when present, explicitly not treated as an actual subscription bill;
- concrete model version, failures, raw response, parse result, and immutable hashes.

The frozen v1.1 precomputed C lane is displayed only as a descriptive comparison. No statistical non-inferiority claim is permitted because this extension runs later, after the prior results were known, with one call per cell and hosted aliases.

## Failure and validity rules

- A cell fails transport validation unless exactly one successful MP tool call has the exact expected input hash and deterministic output hash.
- Any unrelated provider tool event invalidates that cell.
- A structurally invalid final answer remains in the denominator as incorrect.
- A changed base world hash, MP contract, manifest, or concrete model family invalidates comparison with v1.1.
- Results remain `DEMO`, never `VERIFIED` or an official leaderboard entry.
- The run may be resumed only for missing transport-failed cells; completed cells are immutable.
