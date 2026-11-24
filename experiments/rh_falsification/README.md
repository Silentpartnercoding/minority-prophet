# RH falsification benchmark

An experiment track for Minority Prophet built around the Riemann Hypothesis
(RH).

Disproving RH is not the success criterion. The expected mathematical outcome
of every run is `NO_COUNTEREXAMPLE_FOUND`. The benchmark succeeds if Minority
Prophet handles asymmetric evidence correctly: it keeps rare signals that
could be decisive, rejects fake ones, and never lets a count of reports stand
in for a count of independent roots.

## Why RH is a useful benchmark

RH is a universal claim: every nontrivial zero of the Riemann zeta function
has real part 1/2. Universal claims carry a built-in asymmetry.

- Confirmations are cheap and correlated. Over 10^13 zeros have been checked
  on the critical line. One more confirmation changes almost nothing, and a
  crowd of reports saying "zero found on the line" is the copied-majority
  regime this repository already studies.
- One valid counterexample is decisive. A single rigorously verified zero
  with real part other than 1/2 refutes RH. In the compiled core this is
  `universalF` in `formal/lean/MinorityProphetCore/Asymmetric.lean`, and in
  code it is `aggregation.root_vote.asymmetric_verdict` with
  `claim_shape="universal"`.
- Most apparent counterexamples are artifacts. Floating-point error,
  cancellation, truncation and precision drift produce fake off-line zeros
  far more often than mathematics produces real ones. A system that believes
  every dissenter fails here as badly as majority vote fails on copied
  majorities.

## Why "no counterexample found" is not "RH proven"

A finite search over a finite region at finite precision cannot establish a
universal claim over an infinite domain. The only valid terminal results are
`NO_COUNTEREXAMPLE_FOUND`, `NUMERICAL_ANOMALY_FOUND`,
`CANDIDATE_REQUIRES_VERIFICATION`, `FALSE_POSITIVE_REJECTED`,
`METHOD_FAILURE`, `INSUFFICIENT_PRECISION` and `UNRESOLVED`.

There is no state for a proved RH. `asymmetric_verdict` returns
`not_refuted` when no counterexample root is present, and that means exactly
that. A raw anomaly may never move directly to `FALSIFIED`.

## How a verdict is reached

There are no scores, weights or probabilities anywhere in this pack.

1. Every report is recorded in the canonical evidence graph
   (`provenance/graph.py`). A report that carries a computation fingerprint
   is recorded as reading that calculation, so one finished calculation is
   one root no matter how many reports repeat it.
2. The number of distinct roots behind a candidate comes from
   `aggregation/root_vote.py` (`verdict`, the unweighted F).
3. `src/rh_decision.py` routes the candidate from that count plus the
   recorded verification facts (level, reproduced or failed, stable,
   internally consistent). Each fact is yes or no.
4. A candidate becomes a counterexample root of the universal claim only
   once its verification is certified (level 4 or higher, reproduced, stable,
   consistent). The universal claim is then settled by
   `asymmetric_verdict`: one certified root refutes it, and the confirming
   roots are not read.

Confirmations and counterexamples are different propositions. Candidate
reports live in the candidate ledger. Confirmations and certified
counterexamples live in the universal ledger.

## Contents

- `experiment_spec.md`: the experiment in the repository's hypothesis
  template.
- `ROOT-IDENTITY.md`: what counts as a root here, and the open cap question.
- `schemas/evidence.schema.json`: the evidence object, with its mapping onto
  the canonical node.
- `schemas/search_job.schema.json`: a reproducible search-job description.
- `fixtures/true_prophet_cases.json`: control worlds A to F with known ground
  truth.
- `fixtures/false_prophet_cases.json`: injection cases FP1 to FP7 that must be
  rejected or abstained on.
- `src/ledger_adapter.py`: the report log over the canonical graph, and the
  root count from `root_vote`.
- `src/rh_decision.py`: verification records, the universal ledger, and the
  routing rule.
- `src/phase1_harness.py`: the Phase 1 synthetic runner. It checks H2.1 to
  H2.4 against majority vote.
- `tests/`: unittest suites. From the repository root:

```
python -m unittest discover -s experiments/rh_falsification/tests -p 'test_*.py'
```

The repository suite also runs them through
`tests/test_rh_falsification_pack.py`.

## Unattributed reports

A parentless report with no fingerprint names nothing checkable, and the
canonical graph refuses it. `unattributed_policy` says what happens next:

- `quarantine` (default): it stays on the report log and adds zero roots.
- `abstain_if_decisive`: zero roots, and a decision it could change is
  withheld, which is the default meaning in `root_vote`.
- `treat_as_root`: explicit opt-in. Each such report is its own root.

## Forbidden path

Do not call Gate `decide()` with `TrustAllVerifier`. Evidence assessment does
not grant authority. If Gate is used later, use `selective_decide` only, with
a subject bound to the candidate and a real verifier. Not in this pack.

## Phase 1 (synthetic only)

Phase 1 exists to beat majority vote on the fixture worlds before any zeta
computation. Run:

```
python experiments/rh_falsification/src/phase1_harness.py
```

Deterministic seed `20260817`. No zeta math. Every number in the fixtures is
synthetic.

## Not in this pack

- Numerical zeta evaluation (Phases 2 and later).
- A search-coverage ledger. `not_refuted` cannot yet say which regions were
  searched; `knowledge_ledger` carries search coverage and would be wired in
  Phase 2.
- An enforced cap on how many roots one identity may mint. The canonical
  `provenance/root_registry.py` can enforce one; this pack accepts a
  `root_authority` but does not configure one.
- Gate `decide()` or `TrustAllVerifier`.
- Leaderboard integration.
