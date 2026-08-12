# Epistemic Live Tool v1 — native MCP transport result

Status: **GRID COMPLETE / STRICT VALIDATION FAILED / DEMO**

All 64 preregistered cells were attempted. Fifty-eight passed the exact live-tool contract; six were correctly rejected for tool-orchestration violations. These failures remain in the accuracy denominator.

This is a post-result transport extension on known synthetic development worlds. It is not a hidden evaluation, independent confirmation, controlled API latency study, or official leaderboard result.

## Frozen identity

- Protocol commit: `3259539c1ec661059b958b744c409aa747a2536e`
- Protocol manifest: `sha256:a61cd271d5eb0642093d63157726a2a3aeca2a01798ae50260cdc42e48330933`
- Base v1.1 manifest: `sha256:7bf6d393e59ce6fbc78ca41bda4f71b5a0c29dc95d2b535bb19901c345bf3943`
- MP tool contract: `sha256:fac9d675d2c77998174a6d934a4c24ff4e3258b69b812d1a02d54365db59394a`
- Runtime state SHA-256: `531ad6c973426d5c5d6d4ca4a58af424d129447404fa22810a5da372af60ecfd`
- Machine-readable result file SHA-256: `a2091c5bf7720d16ac3ff6298ea1681cff231217aadb185ac408ea5acb51bb09`
- Semantic report hash: `sha256:fb363d67a4dc194452d669ffe572385d229d449f3269295052ce14b4eea7c19e`

## Result

| Model | Correct / all attempts | Strict live accuracy | Accuracy after a valid call | Valid exact calls | Precomputed C accuracy |
|---|---:|---:|---:|---:|---:|
| `gpt-5.6-sol` | 27/32 | **84.375%** | 27/28 = 96.429% | 28/32 = 87.5% | 31/32 = 96.875% |
| `claude-sonnet-5` | 29/32 | **90.625%** | 29/30 = 96.667% | 30/32 = 93.75% | 29/32 = 90.625% |

Strict live accuracy is the intent-to-treat result: any malformed, duplicate, or wrong-input tool call counts as a failure. Conditional accuracy is shown only to separate decision quality from integration reliability.

## End-to-end speed

The timer starts before spawning the provider CLI and stops after final-response capture. It includes CLI startup, MCP initialization and listing, model argument construction, MP execution, receipt transport, post-tool reasoning, and final response generation.

| Model | Live mean | Live median | Live p95 | Live maximum | Precomputed C mean | MP computation mean |
|---|---:|---:|---:|---:|---:|---:|
| `gpt-5.6-sol` | **67.750 s** | 51.040 s | 116.706 s | 170.533 s | 8.166 s | **1.628 ms** |
| `claude-sonnet-5` | **44.732 s** | 36.445 s | 92.465 s | 96.956 s | 9.067 s | **2.206 ms** |

Whole-grid wall time was **19 minutes 36.319 seconds** with two concurrent workers per model and both providers running concurrently.

The local deterministic MP calculation was not the bottleneck. The dominant time was before the tool call: MCP initialization to tool invocation averaged 60.491 seconds for GPT and 32.464 seconds for Claude. That interval includes the model reading the prompt and constructing a large exact structured argument.

Per-call timing excludes the six strict-failed cells because the adapters rejected them before returning normalized telemetry. The whole-grid wall time includes them.

## Tool-orchestration failures

- GPT: four wrong-input-hash calls (`mp_lift_00001`, `00005`, `00006`, `00009`).
- Claude: one duplicate call (`mp_lift_00009`) and one wrong-input-hash call (`mp_lift_00012`).
- Both models also made one valid but epistemically wrong decision: GPT failed to abstain on a balanced conflict; Claude failed to abstain under incomplete provenance.
- There were zero parse failures among the 58 strictly valid cells.

This is the central new finding: injected receipts measured reasoning lift, but native provisioning also introduces a reliability problem. A production integration should not ask the LLM to recopy a large evidence graph into tool arguments. The orchestrator should bind an immutable evidence packet or receipt handle and reject mutation before execution.

## Tokens and partial cost

| Model | Recorded input | Recorded output | Recorded cached | Provider-reported estimate |
|---|---:|---:|---:|---:|
| GPT | 1,308,215 | 91,942 | 818,176 | not reported by subscription CLI |
| Claude | 128 | 175,178 | 407,173 | **$6.342547** |

The Claude input-token field is not comparable with the Codex field under these CLI envelopes. The dollar figure includes only the 30 normalized valid Claude cells, excludes two rejected calls, and is a provider estimate rather than an established incremental subscription bill. It is therefore a lower-bound partial telemetry figure, not “the cost of the study.” MP itself used no paid model call.

## Integrity audit

The post-run audit passed all structural checks:

- 64 unique model/world attempts and 32 attempts per model;
- all world hashes matched the frozen base;
- all 58 accepted cells parsed and contained exactly one successful MP call;
- every accepted MP input hash and recomputed deterministic output hash matched;
- the tool contract and protocol commit were pinned;
- 58 accepted raw responses and parsed responses were retained;
- the six rejected cells remained visible rather than being retried away.

## Interpretation

The production-style result is not “MP takes a minute.” MP took roughly two milliseconds. The result is:

> A naive native-tool integration makes the model spend tens of seconds reconstructing a large evidence payload and sometimes reconstruct it incorrectly.

The next engineering step is a bound-packet tool contract: the trusted orchestrator stores the exact B-visible packet, gives the model an opaque content hash or handle, and MP analyzes those already-bound bytes. That preserves real tool discovery and receipt transport while removing lossy LLM transcription from the security boundary.
