# Reproducing KL-000 under protocol v1.3.0

Prior REPRODUCE documents apply; this adds what v1.3.0 changes. Standard
library only, CPython 3.11+, no network.

## Run it

```bash
cd research/knowledge-ledger/experiments/KL-000
python3 src/run_kl000.py --phase all --preregistration preregistration-v1.3.0.json \
    --out results --label reproduction-v1.3.0
```

Runtime is longer than prior versions (~3 minutes): the confirmatory now
includes the `decisionAblations` phase, two additional full-enumeration
checker sweeps.

## What must come out

Everything the v1.2.0 document requires — every count, conclusion, baseline
preserved total, and both pinned digests **unchanged** — plus:

| Field | Required value |
|---|---|
| `protocolVersion` | `1.3.0` |
| `phases.decisionAblations.ablations.ABL-R1.i12Violations` | **exactly 22440** |
| `phases.decisionAblations.ablations.ABL-R1.otherInvariantViolations` | 0 |
| `phases.decisionAblations.ablations.ABL-R52.i12Violations` | **exactly 38760** |
| `phases.decisionAblations.ablations.ABL-R52.otherInvariantViolations` | 0 |
| every `matchesRegisteredExpectation` | `true` |
| `phases.exhaustive.violationsByInvariant` | `{}` — B5 records zero I12 violations everywhere |
| `phases.baselines.*.totalViolations` | the registered I1–I11 sums, unchanged (634,440 / 26,880 / 26,208 / 189,720) |
| `phases.baselines.*.i12Violations` | reported, positive, and NOT part of the preserved totals |

A caught-count differing from 22,440 / 38,760 **in either direction** marks
the run invalid: I12 is then wrong, not the measurement.

## Version-compatibility note

`check_world` now carries I12 permanently. Re-running older registrations
still reproduces every registered number (B5 has zero I12 violations and the
baseline preserved metric is the I1–I11 sum), but the result documents gain
two new baseline fields (`i12Violations`, `totalViolationsNote`), so
REPRODUCE.md's original whole-document equality one-liner no longer holds
against a fresh reproduction — use the field-level comparisons in the
versioned REPRODUCE documents instead.

## The permanent suite

```bash
PYTHONPATH=. python3 -m pytest research/knowledge-ledger/experiments/KL-000/tests/ -q
```

88 tests: 54 (v1.0.0) + 14 (v1.1.0) + 12 (v1.2.0) + 8 (v1.3.0).

## Verify the v1.3.0 registration was frozen first

```bash
P=research/knowledge-ledger/experiments/KL-000
test "$(git log -1 --format=%H -- $P/preregistration-v1.3.0.json)" \
   = "$(cat $P/PROTOCOL-COMMIT-v1.3.0.txt)" && echo "v1.3.0 unedited since registration"
```

All four chains (v1.0.0–v1.3.0) are independently checkable.
