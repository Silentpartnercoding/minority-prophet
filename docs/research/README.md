# Research map

This map separates the research question, the experimental machinery, the
results, and the lifecycle records that determine status.

## Program and hypotheses

- [`ROADMAP.md`](../../ROADMAP.md) — current public sequence.
- [`RESEARCH-DIRECTION.md`](../../RESEARCH-DIRECTION.md) — proposed research
  direction and open boundaries.
- [`RESEARCH-HYPOTHESES.md`](../../RESEARCH-HYPOTHESES.md) — falsifiable
  hypotheses and required templates.
- [`FOUNDATIONS.md`](../../FOUNDATIONS.md) — conceptual and mathematical framing.

These planning documents do not promote results by themselves.

## Methods and implementations

- [`benchmark/`](../../benchmark/) — synthetic world generator and metrics.
- [`aggregation/`](../../aggregation/) — baseline and experimental methods.
- [`provenance/`](../../provenance/) — lineage representation and analysis.
- [`experiments/`](../../experiments/) — protocols, runners, and experiment-local
  documentation.
- [`formal/`](../../formal/) — proofs and theorem scope.
- [`verification/`](../../verification/) — additional verification tracks that
  are not canonical experiments unless separately enrolled.

## Evidence and records

- [`research/integrity/`](../../research/integrity/) — graduated integrity model
  and schema.
- [`research/records/`](../../research/records/) — per-experiment lifecycle
  records; canonical and imported records are immutable.
- [`results/`](../../results/) — preserved outputs, manifests, replays, nulls,
  adverse results, and incomplete runs.
- [`research/knowledge-ledger/`](../../research/knowledge-ledger/) — knowledge
  ledger methods, conformance profile, findings, and experiments.
- [`research/field-evidence/`](../../research/field-evidence/) — sanitized field
  observations with explicitly bounded claims.
- [`public/research/`](../../public/research/) — website-ready research summaries;
  use the underlying records for authority.

## Papers

Start at [`papers/00-CURRENT-PAPER.md`](../../papers/00-CURRENT-PAPER.md). The
[`papers/`](../../papers/) directory preserves earlier manuscripts and review
packages rather than rewriting history. Rendered PDFs live under
[`output/pdf/`](../../output/pdf/); source and validation metadata control their
meaning.

## Interpreting status

| Label | Meaning |
|---|---|
| Exploratory | Useful work that cannot support a canonical claim |
| Candidate | Preregistered/content-bound protocol awaiting a qualifying result |
| Canonical | Repository-native result satisfying the recorded lifecycle |
| Imported | Content-bound external result with its control relationship stated |
| Incomplete/adverse/rejected | A preserved outcome, not a result to hide or relabel |

The complete rules are in
[`research/integrity/README.md`](../../research/integrity/README.md). For the
current plain-language boundary, see [Evidence status](../evidence/STATUS.md).
