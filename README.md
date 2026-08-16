# Minority Prophet

**Count independent evidence, not repeated claims.**

> **Research status:** EXP001–EXP002 are canonical derived records; EXP003R–EXP006R and EXP008R are canonical archived-implementation replays; EXP007R is canonically incomplete; EXP007A is the canonical synthetic adversary completion. None establishes real-world provenance recovery. See the registry and evidence-alignment ledger.

Minority Prophet asks whether grounded evidence can survive an overwhelming
copied majority.

## What is actually established

The repository is large. The established claims are not, and separating the two
is the point of this section. Full detail: [`formal/CLAIM-SCOPE.md`](formal/CLAIM-SCOPE.md),
statuses in [`formal/THEOREM-LEDGER.json`](formal/THEOREM-LEDGER.json).

**Proved** — compiled in Lean 4.32.2 against pinned Mathlib, zero `sorry`, no
added axioms. Checkable by anyone, no trust in us required.

- Under side-consistency, `S_a` is exactly the `a`-asserting roots.
- Lineage may be arbitrarily wrong without moving a verdict, provided no edge
  crosses sides, no root is created or destroyed, and assertions are unchanged.
- Copies **whose parent edge is recorded** are free.
- A verdict flips only if net per-side root flow reaches the margin; flow equal
  to the margin abstains; reversal needs margin + 1.
- With assertions fixed, `k` units of root-set change cannot move a verdict of
  margin > `k`.
- Conversions preserve the margin's parity, so an odd margin cannot be driven to
  abstention by conversion alone.

**Measured** — one number about the world, at scale, no labelling.

- Among 60.8M journal articles (2015–2024), **46.2%** record no ancestry. Each
  becomes an evidence root. So in the copy-dominant regime this project is
  about, over-count ≥ `u × N` — with `u` from **33%** (medicine) to **74%**
  (arts and humanities). A floor, not an average.

**Not established** — and not on a roadmap to being established without people.

- Whether one evidence root corresponds to one real observation in the typical
  case. This is blocked *structurally*, not for want of effort: the over-count
  lives only among works that record no ancestry, so the ground truth needed to
  measure it is the very data whose absence constitutes it. See
  [`HRI1-BLOCKER-20260816.md`](research/knowledge-ledger/experiments/KL-014/HRI1-BLOCKER-20260816.md).
- Accordingly `flip_budget` is publishable as a count of root-set units, which
  is what it provably is, and **not** as an operational security budget.

**Not claimed at all.** That the system discovers truth, that agreement implies
independence, or that any of this has been demonstrated outside synthetic worlds
and public bibliographic metadata.

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

- [`CONTRIBUTOR-QUICKSTART.md`](CONTRIBUTOR-QUICKSTART.md) and
  [`CONTRIBUTING.md`](CONTRIBUTING.md) — the shortest path to choosing a lane,
  creating a research record, and running the same checks as CI.
- [`papers/00-CURRENT-PAPER.md`](papers/00-CURRENT-PAPER.md)
  — stable entry point to the current evidence-aligned pre-submission paper;
- [`papers/peer-review/`](papers/peer-review/)
  — focused peer-review manuscript, literature audit, metadata, and submission checklist;
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
