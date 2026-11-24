# RH falsification benchmark: specification

Status: Phase 0 infrastructure and the Phase 1 synthetic benchmark are in
this pack. Phases 2 and later are out of scope. This is an experiment-local
specification with no registered experiment ID.

This document states the RH falsification track in the repository's
hypothesis template. Consensus is never treated as truth, and correlation is
never treated as independence. No score, weight or probability enters any
decision: verdicts come from counts of distinct roots, and the universal claim
is settled by the asymmetric rule (`universalF`).

---

## H2.1 Decisive evidence retention

Question. When a single piece of evidence can change the truth status of a
universal claim, does Minority Prophet keep it through to verification more
often than consensus baselines?

Null hypothesis. Minority Prophet's retention rate is not higher than the
baselines on the synthetic control worlds (Controls A, C and E in
`fixtures/true_prophet_cases.json`).

Metric. Decisive evidence retention rate: the fraction of valid rare
falsifiers that are routed to verification rather than discarded.

Failure condition. Retention rate at or below the best baseline on Controls
A, C and E, or any valid synthetic counterexample dropped because 999 reports
disagreed.

Success condition. Retention rate strictly above every baseline implemented,
with deterministic-seed replay.

---

## H2.2 False prophet rejection

Question. Does the verification and provenance layer stop Minority Prophet
from believing every dissenter?

Null hypothesis. Fake counterexample candidates (FP1 to FP7,
`fixtures/false_prophet_cases.json`) reach `FALSIFIED` or
`CANDIDATE_FALSIFIER` at the same or a higher rate under Minority Prophet as
under baselines.

Metric. False prophet rejection rate: the fraction of injected fakes ending in
`REJECTED_FALSE_POSITIVE` or `ABSTAIN`.

Failure condition. Any FP case reaches `FALSIFIED`. Any FP case moving from a
raw anomaly directly to `FALSIFIED` fails the experiment regardless of
aggregate rates.

Success condition. All seven FP families are rejected or abstained on, and
FP5 (20 reports replaying one candidate) has exactly 1 independent root.

---

## H2.3 Independence against raw support

Question. Does the system count independent work-product roots
(fingerprinted calculations; see ROOT-IDENTITY.md) rather than reports or
declared lineage?

Null hypothesis. The root count from `KnowledgeLedger.independent_support_count`
(canonical graph plus `root_vote.verdict`) does not differ from the report
count on Control D (100 copies of one fake, parents omitted) and Control E
(3 independent finders with distinct `result_hash` values).

Metric. The root count must equal the number of distinct computation
fingerprints, not the number of reports and not the number of agent ids.

Failure condition. Control D counts more than 1 root, Control E counts fewer
than 3, or parentless reports with no fingerprint count as roots under the
default quarantine policy.

Success condition. Exact match to the fingerprint-root counts across all
fixtures, under declared ancestry and under omitted parents when fingerprints
match. Only recorded or fingerprinted copies collapse. This pack does not
claim that an unrecorded duplicate cannot change a verdict.

---

## H2.4 Abstention under ambiguity

Question. Does the system hold back from a commitment when verification is
incomplete?

Null hypothesis. On Control F (an ambiguous anomaly), the system commits to
`SUPPORTED` or `FALSIFIED` at the same rate as baselines.

Metric. Fraction of fixtures with ground-truth action `abstain_or_verify`
that end in `ABSTAIN` or `VERIFYING`.

Failure condition. Any commitment to a terminal truth state on Control F
before verification level 4.

Success condition. Control F ends in `ABSTAIN` or `VERIFYING` in every seeded
replay.

---

## Routing rule

`src/rh_decision.py` applies these rules in order. Each input is a root count
or a yes or no verification fact.

1. A record that contradicts itself is rejected.
2. No attributable root: rejected, or withheld under `abstain_if_decisive`
   when unattributed reports exist.
3. A failed independent recheck rejects the candidate.
4. An anomaly is never a counterexample: abstain once verification is
   exhausted (level 4 or higher), otherwise keep verifying.
5. A certified candidate (level 4 or higher, reproduced, stable, consistent)
   enters the universal ledger as a counterexample root. If
   `asymmetric_verdict` then returns `refuted`, escalate.
6. Otherwise keep verifying.

## Root identity

A root is a finished calculation, fingerprinted by region, method, software,
seed and hash. Empty parents plus no fingerprint is unattributed, not a root.
A cap on how many roots one identity may mint is a deployment requirement
(see ROOT-IDENTITY.md). Agent ids are never roots.

## Forbidden Gate path

Do not wire Gate `decide()` with `TrustAllVerifier`. Evidence assessment does
not grant authority. If Gate is used later, use `selective_decide` only, with
a subject bound to the candidate and a real verifier. Not in this pack.

## Architecture (Phase 1 is in this pack; Phases 2 and later are not)

Roles: (A) search workers S1 to S5, (B) consequence and equivalence workers
E1 to E4, (C) adversarial false-positive injectors FP1 to FP7, (D)
verification workers, (E) the provenance ledger, (F) the Minority Prophet
decision layer, (G) baseline consensus systems.

Planes are separated. The proposal plane suggests regions, methods and
critiques. Deterministic mathematical software produces every numerical value
(numerical plane). Independent workers recompute claims (verification plane).
No number from the proposal plane is trusted until recomputed, and no prose
may certify a zero.

### Search workers

- S1 sequential: finite interval, high precision, logged method. A real part
  of approximately 0.5 is never treated as proof.
- S2 random high-altitude windows: reproducible pseudorandom windows at large
  imaginary height, with the seed logged.
- S3 stratified: logarithmic height strata (1e4, 1e6, 1e8 and so on), with
  independent windows per stratum.
- S4 suspicious-region hunter: close zero pairs, large derivatives, small
  values of |zeta| off the line, unstable regions.
- S5 off-line grid scout: coverage of Re(s) < 0.5 - eps and
  Re(s) > 0.5 + eps. Candidates are never declared zeros from floating-point
  magnitude alone.

### Indirect falsification workers

- E1 prime-counting error bounds. E2 Mobius and Mertens-type behavior (the
  historical Mertens conjecture is not treated as equivalent to RH). E3
  established equivalent criteria (Li, Robin and others), each with a theorem
  citation, implication direction, assumptions and falsification condition.
  E4 zero-spacing statistics: a statistical anomaly is a reason to look, never
  a counterexample.

"Related to RH" may never be turned into "equivalent to RH".

### Los and ultraproduct track (exploratory)

- L1 formalization: what is first-order expressible, and what Los's theorem
  transfers and what it does not. L2 ultraproduct investigator. L3 skeptic,
  whose job is to kill every proposal by demanding the language, structures,
  transferred formula, ultrafilter assumptions, internal or external status,
  and preservation of analytic convergence. Success is a clarification or a
  lemma. "Los proves RH" is never an output.

### Verification levels

0 candidate. 1 independent recomputation. 2 precision escalation
(128, 256, 512 and 1024 bits; the candidate must converge, not wander).
3 independent algorithm. 4 interval or rigorous arithmetic (a certified zero
and a certified real-part interval excluding 1/2). 5 argument-principle root
counting. 6 a standalone external verifier producing a reproducible
certificate.

### Claim states

SUPPORTED, UNSUPPORTED, ANOMALY, CANDIDATE_FALSIFIER, VERIFYING, REPRODUCED,
REJECTED_FALSE_POSITIVE, ABSTAIN, FALSIFIED. ANOMALY never moves directly to
FALSIFIED.

### Baselines

1 majority vote (implemented). Planned comparisons, not implemented: 2
confidence-weighted majority, 3 a language-model judge, 4 best single
model, 5 simple ensemble, 6 provenance-aware ensemble without Minority
Prophet routing. 7 is full Minority Prophet. The planned baselines are rivals
to beat. Nothing from them enters a Minority Prophet decision.

### Ablations

Re-run with each removed: provenance, verification, root counting,
false-prophet injection, consensus count, Minority Prophet routing.
Attribute any improvement to components, not to the system as a whole.

### Phases

0 infrastructure (in this pack). 1 synthetic benchmark (in this pack; must
beat majority vote before going further; no zeta math; deterministic seed).
2 known zeta regions as a rediscovery sanity check, with a search-coverage
ledger. 3 false-positive torture test. 4 high-height exploratory search.
5 indirect attacks. 6 Los research track.

### Red team

A dedicated worker whose only job is to explain every exciting result as an
artifact. Did the candidate converge as precision increased? Was the
computation independent? Is everything copying one source? Is an implication
backwards? Is a theorem used outside its assumptions? Is a cited theorem
real? Is it a near-zero rather than a zero? Is the interval proof rigorous? Is
it reproducible from a clean room?

---

## Valid terminal results

`NO_COUNTEREXAMPLE_FOUND` (meaning exactly that), `NUMERICAL_ANOMALY_FOUND`,
`CANDIDATE_REQUIRES_VERIFICATION`, `FALSE_POSITIVE_REJECTED`,
`METHOD_FAILURE`, `INSUFFICIENT_PRECISION`, `UNRESOLVED`.

There is no state for a proved RH anywhere in this experiment.
