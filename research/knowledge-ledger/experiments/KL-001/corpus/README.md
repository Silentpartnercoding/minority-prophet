# KL-001 corpus and baseline — preparatory, not a kernel result

**KL-001 remains `seeded`.** Nothing here advances its state, and nothing here is
filed under `results/`.

The programme's own test caught the first attempt at that: writing
`results/baseline-v1.json` failed
`test_no_experiment_claims_progress_without_the_evidence_for_it` with *"KL-001 is
seeded but carries results"*. The rule is right. KL-001's gate says committing it
is the owner's act, and measuring a baseline is not committing it.

## What this is

Gate items (2) and (3), built so they are ready when the gate is committed:

- `generate_corpus.py` — seeded repositories with machine-checkable planted
  defects and clean controls, digest-manifested **before** any evaluation.
  Deterministic, dependency-free, zero spend: no metered model touches it. The
  word generator is LIN-000's, so the corpus is reproducible from a seed without
  depending on any language's PRNG — the F11 lesson applied from the start.
- `measure_baseline.py` — a plain pattern scanner, no dual ledger. It refuses to
  run if the corpus no longer matches its manifest.
- `frozen-v1/` — 60 repositories, 199 files, 62 planted defects, 19 clean.
- `BASELINE-v1.json` — the measurement.

## The number the registered target was missing

    planted 62   true positives 50   false negatives 12   false positives 0
    BASELINE RECALL 80.7%     false-clean rate 12.2%

KL-001's target is "preserve 95% of true positives". Until now nothing said 95%
of what, so the target could not fail. It is 95% of **80.7%**, i.e. about 76.7%
absolute recall.

## Read the aggregate with the breakdown, not instead of it

    bare-except            10/10  100%
    hardcoded-credential   13/13  100%
    shell-injection        15/15  100%
    unchecked-return       12/12  100%
    missing-timeout         0/12    0%

**All twelve misses are one class.** The scanner's `missing-timeout` pattern uses
a negative lookahead that cannot see a `timeout=` argument, so it matches nothing.
"80.7%" is really "100% on four classes and 0% on a fifth".

This matters for what comes next: a dual ledger that lifts the aggregate by
fixing only that class would look like a general improvement and would not be
one. The per-class figures, not the aggregate, are the comparison to register.

## Deliberately unimpressive

A cleverer baseline scanner would lower the bar the dual ledger has to clear.
The baseline is what a team already has — grep in CI — because that is what the
product must beat to be worth adopting.
