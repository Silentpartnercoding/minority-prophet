# OpenRouter confirmatory v1 compact trial archive

This directory preserves the per-attempt trial records behind the published
`openrouter-confirmatory-v1` aggregate result. It is a supporting archive, not
an independent validation or a retroactive promotion into the project's
canonical research ledger.

## Contents

- `trials.jsonl.gz` — 2,730 gzip-compressed JSON Lines records, one per model
  attempt. The rows contain identifiers, conditions, scores, timings, token
  usage, provider-reported cost, hashes, and opaque provider request IDs.
- `manifest.json` — integrity hashes, final-state counts, and the reconciliation
  between the first public snapshot and the completed archive.

The archive deliberately excludes raw model response bodies, parsed response
bodies, credentials, and the resumable runtime state. Those materials are not
required to audit the published per-attempt scores and remain private.

## Integrity

| Object | Bytes | SHA-256 |
|---|---:|---|
| `trials.jsonl.gz` | 739,050 | `18fa75e26b339ca75a50453a566a2355d7ca4b9b849d7734c3651854a218cb25` |
| Decompressed JSONL | 5,529,506 | `97d9cf63992b4f95a0b4d94b099320e32239d8d386081c02e34bc9f77bd29a48` |

Verify locally:

```sh
shasum -a 256 trials.jsonl.gz
gzip -dc trials.jsonl.gz | shasum -a 256
gzip -dc trials.jsonl.gz | wc -l
```

## Final-state reconciliation

The first public result note was written from a resumable snapshot with 2,576
completed cells and 70 unresolved cells. Eleven additional Gemini cells
completed during the final seconds of the run. This archive preserves the
actual final state: 2,587 completed cells and 59 unresolved cells across 2,646
unique cells.

The additional completions change Gemini's paired sample from 282 to 285 and
its primary contrast from `+0.082` to `+0.081` after rounding. All three models
still clear the preregistered `+0.03` threshold with exact two-sided sign-test
`p < 0.05`; the substantive conclusion is unchanged.

## Claim boundary

The benchmark worlds were constructed by the same programme that built the
analysis. This archive improves durability and auditability, but it is not an
external replication, independent audit, or evidence that the method discovers
truth in unrestricted real-world settings.
