# Reproducing KL-000 under protocol v1.2.0

`REPRODUCE.md` (v1.0.0) and `REPRODUCE-v1.1.0.md` apply; this adds what
v1.2.0 changes. Standard library only, CPython 3.11+, no network.

## Run it

```bash
cd research/knowledge-ledger/experiments/KL-000
python3 src/run_kl000.py --phase all --preregistration preregistration-v1.2.0.json \
    --out results --label reproduction-v1.2.0
```

## What must come out

Everything the v1.1.0 document requires, plus:

| Field | Required value |
|---|---|
| `protocolVersion` | `1.2.0` |
| `phases.fixture.controls` | **12 entries**, C01–C12, all `passed` |
| C11 `differences` | `[]` — digest **unchanged** from the v1.1.0 pin (`sha256:84e63c21…33eafe`), 703-byte canonical form matched character-for-character |
| C12 `differences` | `[]` — digest `sha256:61000a9b…aa3b6e`, margin 1 (absolute), 691-byte canonical form |

Counts, conclusion distributions, and baselines are identical to every prior
confirmatory run — the registered prediction
(`preregistration-v1.2.0.json`, `expectedIdenticalToRun1`) with the added
claim that **no digest moved either**: R5.1/R5.2 registered the receipt the
evaluator already emits.

```
exhaustive   176,120 / 110,840 / 65,280 / 0     conclusions 160 / 49,480 / 41,820 / 19,380
randomized   1,000,000 / 243,381 / 756,619 / 0
baselines    B1 634,440   B2 26,880   B3 26,208   B4 189,720
```

A moved digest falsifies the registration-only claim; a moved count or
conclusion is worse — it means a serialisation repair changed evaluation.

## The permanent suite

```bash
PYTHONPATH=. python3 -m pytest research/knowledge-ledger/experiments/KL-000/tests/ -q
```

80 tests: 54 (v1.0.0) + 14 (v1.1.0) + 12 (v1.2.0, `test_kl000_v120.py`).

## Verify the v1.2.0 registration was frozen first

```bash
P=research/knowledge-ledger/experiments/KL-000
test "$(git log -1 --format=%H -- $P/preregistration-v1.2.0.json)" \
   = "$(cat $P/PROTOCOL-COMMIT-v1.2.0.txt)" && echo "v1.2.0 unedited since registration"
```

The v1.0.0 and v1.1.0 chains remain independently checkable. Note protocol
v1.2.0 carries **Amendment 1** (a member-count typo corrected before any
execution; the preregistration untouched, its own prose error documented in
the amendment log).

## Cross-implementation status

Under v1.2.0, every byte C11 hashes is registered for the first time:
receipt member list, types, the exact `schema`/`reason`/`limits` values, the
margin sign (absolute, R5.2), and the `conversionsToReverse` formula. C11's
and C12's `expected` blocks carry their complete canonical unsigned strings,
so an implementation that fails the digest can see which byte diverged.
Whether a digest actually reproduces across implementations is
IND-20260807-3's question — a separate commission, not runnable from this
repository.
