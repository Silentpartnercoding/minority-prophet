# Minority Prophet

**When AI agents agree, check whether the evidence does.**

Five agents can return the same answer while all relying on one recorded source.
Minority Prophet uses recorded claim ancestry, collapses dependent support into
evidence roots, preserves independently supported dissent, and can require new
evidence before a consequential decision proceeds.

Observability asks **what happened**. Evaluation asks **whether the task
worked**. Minority Prophet asks **why the system should believe its answer**.

> **Research status:** EXP001–EXP002 are canonical derived records; EXP003R–EXP006R and EXP008R are canonical archived-implementation replays; EXP007R is canonically incomplete; EXP007A is the canonical synthetic adversary completion. None establishes real-world provenance recovery. See the registry and evidence-alignment ledger.

Minority Prophet asks whether grounded evidence can survive an overwhelming
copied majority.

## Run the canonical failure

MP.01 is a deterministic six-agent teaching fixture. Five agents support Answer
A, one supports Answer B, and the five A claims descend from one recorded root.
The apparent 5:1 majority therefore becomes a 1:1 evidence-root tie. The system
abstains, preserves the minority, and asks for another independent source; it
does **not** declare Answer B true.

```sh
python -m experiments.mp01.run_mp01
```

The committed [machine-readable result](public/research/mp01-canonical-demo.json)
is checked against the runner in CI. This is a synthetic demonstration under
declared ancestry, not a claim that hidden real-world copying has been solved.

## Installable surfaces

The repository deliberately separates research code from the deterministic
agent runtime.

```sh
# Python benchmark, aggregation, and provenance primitives
python -m pip install .

# Provider-neutral read-only MCP/HTTP engine
npm --prefix evaluations/multi-model-v1 install
MP_ENGINE_ALLOW_INSECURE_LOCAL=1 npm --prefix evaluations/multi-model-v1 exec mp-engine -- doctor
```

The engine package exposes only versioned runtime modules in its publish
allowlist. See
[`evaluations/multi-model-v1/RUNTIME-README.md`](evaluations/multi-model-v1/RUNTIME-README.md).
Installation does not authorize an agent to execute protected actions.

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
The component and adapter boundaries are summarized in
[`SYSTEM-ARCHITECTURE.md`](SYSTEM-ARCHITECTURE.md).

## Benchmark v0.1

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

- [`CONTRIBUTOR-QUICKSTART.md`](CONTRIBUTOR-QUICKSTART.md) and
  [`CONTRIBUTING.md`](CONTRIBUTING.md) — the shortest path to choosing a lane,
  creating a research record, and running the same checks as CI.
- [`papers/00-CURRENT-PAPER.md`](papers/00-CURRENT-PAPER.md)
  — stable entry point to the current evidence-aligned pre-submission paper;
  earlier versions remain preserved.
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
- [`experiments/lir1/`](experiments/lir1/), [`experiments/lir2/`](experiments/lir2/),
  [`experiments/lir3/`](experiments/lir3/), and [`experiments/lir4/`](experiments/lir4/)
  — lineage-inference boundary track;
  LIR-3 supports a narrow recorded-reply provenance bridge, not causal evidence
  independence or truth recovery; LIR-4 shows that bridge does not degrade
  gracefully under substantial identity missingness
- [`provenance/`](provenance/) — evidence graph implementation and JSON Schema
- [`results/resolved-weather-v0.1.manifest.json`](results/resolved-weather-v0.1.manifest.json) — canonical derived-record hashes and reproducibility boundary
- [`results/hes1-v1/`](results/hes1-v1/) — blind evidence-seeking result: strong coverage recovery with a material false-negative software limitation
- [`research/field-evidence/2026-08-06/`](research/field-evidence/2026-08-06/) — sanitized field observation showing why root identity and dependency matter
- [`results/eaa-p5-out-of-tree-v1/`](results/eaa-p5-out-of-tree-v1/) — imported out-of-tree test of a unified dependence auditor; the frozen gate rejected the candidate, which did not displace the simpler comparators
- [`evaluations/multi-model-v1/`](evaluations/multi-model-v1/) — exploratory,
  dependency-free A/B/C model-evaluation and provenance-formation harness;
  its DEMO studies are preserved but are not canonical or independently
  validated records
- [Minority Prophet Gate](https://github.com/Silentpartnercoding/minority-prophet-gate) — reference implementation of evidence-root aggregation
- [`website/`](website/) and [`app/`](app/) — dashboard specification and implementation

## Research rules

Every hypothesis states a question, null hypothesis, metric, failure condition, and success condition. Consensus is never treated as truth; confidence is never treated as correctness; correlation is never treated as independence.

## Pilot result

The first finite Łoś-inspired pilot is complete. Under correct declared lineage, evidence-root and semantic aggregation recovered all copied-majority worlds in the frozen synthetic run. Semantic aggregation also preserved a three-proposition logical constraint that proposition-wise voting violated. All methods failed under sufficiently corrupted lineage. See [`experiments/EXPERIMENT-001.md`](experiments/EXPERIMENT-001.md) and [`results/los-inspired-v0.1.md`](results/los-inspired-v0.1.md).

This is an exploratory implementation check on constructed data—not evidence that real-world provenance can be recovered, not a literal ultraproduct, and not a general truth-discovery result.

Licensed under Apache License 2.0. See [`LICENSE`](LICENSE) and
[`NOTICE`](NOTICE).
