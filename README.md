# Minority Prophet

**Count independent evidence, not repeated claims.**

> **Research status:** EXP001–EXP002 are canonical derived records; EXP003R–EXP006R and EXP008R are canonical archived-implementation replays; EXP007R is canonically incomplete; EXP007A is the canonical synthetic adversary completion. None establishes real-world provenance recovery. See the registry and evidence-alignment ledger.

Minority Prophet asks whether grounded evidence can survive an overwhelming
copied majority.

## Core invariant

**A recorded copy must not gain a new vote.** In plain language: photocopying one
witness statement does not create more witnesses.

This holds only when evidence roots cannot be freely forged, claims do not cross
between opposing roots, and the surviving root margin is large enough. See
[`PUBLIC-CLAIMS.md`](PUBLIC-CLAIMS.md) for the shortest supported claim set.

## Decision-quality boundary

Decision-quality and reputation systems ask whether an agent's recorded
behavior supports more or less future authority. Minority Prophet asks a
different question: whether the evidence supporting a present claim is
independently grounded or merely repeated. A behavioral score or replay bundle
may be an evidence input; it does not become authority or an independent root
by itself.

In the wider neutral architecture, Border binds identity, delegated authority,
declaration, policy, and evidence to one exact proposed action. Minority Prophet
assesses the structure and strength of evidence only when deterministic policy
cannot resolve an evidence-sensitive question. Gate separately interprets that
assessment as proceed, block, or escalate, and the runtime enforces the exact
effect. Evidence assessment never grants authority.

The repository contains the benchmark, formal model, canonical record registry,
root-issuance reference, neutral evidence contract, tests, and dashboard.

## Minority Prophet Test v0.1

A synthetic world has a hidden binary truth. A small set of independent observers receives reliable evidence. A larger population copies a socially dominant but false claim. An aggregation method must recover truth while preserving uncertainty and lineage.

```bash
python -m benchmark --worlds 500 --seed 7
python -m experiments.los_inspired_v01
python -m unittest discover -s tests -p 'test_*.py'
```

Example output includes truth accuracy, minority-truth recovery, Brier score, abstention rate, and average compute time for:

- simple majority voting
- competence-weighted voting

## Repository map

- [`papers/minority-prophet-v1.0.3.md`](papers/minority-prophet-v1.0.3.md)
  — current evidence-aligned pre-submission paper; earlier versions remain preserved.
- [`formal/PROOFS.md`](formal/PROOFS.md), [`formal/lean/`](formal/lean/) (pinned,
  compiling Lean 4 proofs), and
  [`verification/r1_degradation_curve.py`](verification/r1_degradation_curve.py)
  — formal and verification tracks, not canonical experiments.

- [`FOUNDATIONS.md`](FOUNDATIONS.md) — problem, philosophy, program, and mathematical framing
- [`ROADMAP.md`](ROADMAP.md) — current public research sequence
- [`CONTRIBUTORS.md`](CONTRIBUTORS.md) — authorship and independent-verification credit
- [`CANONICAL-RECORDS.md`](CANONICAL-RECORDS.md) — canonical record registry and promotion rules
- [`EVIDENCE-ALIGNMENT.md`](EVIDENCE-ALIGNMENT.md) — claim-to-record ledger, corrections, and remaining release blockers
- [`RESEARCH-DIRECTION.md`](RESEARCH-DIRECTION.md) — proposed dual evidence/search ledger program and absence-claim boundary
- [`research/knowledge-ledger/`](research/knowledge-ledger/) — public research method, experiment registry, interoperability fixtures, and results
- [`RESEARCH-HYPOTHESES.md`](RESEARCH-HYPOTHESES.md) — falsifiable hypotheses using the required template
- [`contracts/authority-evidence-v0.1/`](contracts/authority-evidence-v0.1/) — vendor-neutral authorization/evidence draft and semantic conformance rules
- [`benchmark/`](benchmark/) — synthetic worlds, evaluation metrics, and CLI
- [`aggregation/`](aggregation/) — public baseline algorithms
- [`experiments/resolved_weather_v01.py`](experiments/resolved_weather_v01.py) — Experiment 002 acquisition and scoring runner
- [`provenance/`](provenance/) — evidence graph implementation and JSON Schema
- [`results/resolved-weather-v0.1.manifest.json`](results/resolved-weather-v0.1.manifest.json) — canonical derived-record hashes and reproducibility boundary
- [`research/field-evidence/2026-08-06/`](research/field-evidence/2026-08-06/) — sanitized field observation showing why root identity and dependency matter
- [Minority Prophet Gate](https://github.com/Silentpartnercoding/minority-prophet-gate) — reference implementation of evidence-root aggregation
- [`website/`](website/) and [`app/`](app/) — dashboard specification and implementation

## Research rules

Every hypothesis states a question, null hypothesis, metric, failure condition, and success condition. Consensus is never treated as truth; confidence is never treated as correctness; correlation is never treated as independence.

## Pilot result

The first finite Łoś-inspired pilot is complete. Under correct declared lineage, evidence-root and semantic aggregation recovered all copied-majority worlds in the frozen synthetic run. Semantic aggregation also preserved a three-proposition logical constraint that proposition-wise voting violated. All methods failed under sufficiently corrupted lineage. See [`experiments/EXPERIMENT-001.md`](experiments/EXPERIMENT-001.md) and [`results/los-inspired-v0.1.md`](results/los-inspired-v0.1.md).

This is an exploratory implementation check on constructed data—not evidence that real-world provenance can be recovered, not a literal ultraproduct, and not a general truth-discovery result.

Licensed under Apache License 2.0. See [`LICENSE`](LICENSE) and
[`NOTICE`](NOTICE).
