# Reproducing KL-000

No network, no credentials, no third-party packages. Standard library only,
CPython 3.11+.

## Run it

From the repository root:

```bash
cd research/knowledge-ledger/experiments/KL-000
python3 src/run_kl000.py --phase all --out results --label reproduction
```

Runtime is about one minute (59s on an Apple M4: 10s exhaustive, 44s
randomized, the rest fixtures and baselines).

## What must come out

`results/kl000-reproduction.json` must agree with the committed
`results/kl000-confirmatory.json` on every field below. These are deterministic:
there is no sampling, no timestamp, and no OS entropy in any of them.

| Field | Required value |
|---|---|
| `result` | `passed` |
| `invalidationReasons` | `[]` |
| `evaluatorUnderTest.sha256` | `15dfd50051ef5da3db13d8e591f58537325ee50aa4e3573914f86e4ff3a3e21f` |
| `evaluatorUnderTest.matchesPreregistration` | `true` |
| `boundsDriftFromPreregistration` | `[]` |
| `derivedExhaustiveCount` | `176120` |
| `phases.exhaustive.worldsChecked` | `176120` |
| `phases.exhaustive.totalViolations` | `0` |
| `phases.exhaustive.failClosedRejections` | `65280` |
| `phases.exhaustive.outOfDeclaredBounds` | `0` |
| `phases.randomized.worldsChecked` | `1000000` |
| `phases.randomized.totalViolations` | `0` |
| `phases.randomized.failClosedRejections` | `756619` |
| `phases.fixture.mismatchedControls` | `[]` |
| every `phases.baselines.*.caught` | `true` |
| every `phases.baselines.*.worldsChecked` | `176120` (full exhaustive set) |
| `phases.exhaustive.receiptProducingWorlds` | `110840` |
| `phases.randomized.receiptProducingWorlds` | `243381` |
| `phases.*.failClosedUnexpectedCauses` | `{}` |
| `phases.*.stopConditionTriggered` | `false` |

Baseline violation counts on the full set:

```
B1-head-count                634440   (I1 520200, I10 114240)
B2-source-count               26880   (I2)
B3-evidence-without-coverage  26208   (I2)
B4-search-without-collapse   189720   (I1)
```

Fail-closed refusals must decompose to exactly **one** cause in both phases:

```
exhaustive   65280  ValueError: One root cannot support opposing sides.
randomized  756619  ValueError: One root cannot support opposing sides.
```

Any other cause appearing in `failClosedByCause` marks the run `incomplete`,
not `failed`: an unrecognised refusal is an implementation defect, not a
scientific outcome. Receipts plus refusals must reconcile exactly to worlds
drawn (`110840 + 65280 = 176120`, `243381 + 756619 = 1000000`).

Conclusion distributions must match exactly:

```
exhaustive  absent_within_declared_scope 160   not_established 49480
            present 41820                      supported 19380
randomized  absent_within_declared_scope 1092  not_established 119228
            present 81792                      supported 41269
```

### Fields that legitimately differ

Only these. Anything else differing is a reproduction failure, not a platform
quirk.

- `label` — set by `--label`.
- `environment.python`, `environment.implementation`, `environment.platform` —
  describe the reproducing machine.
- `phases.*.elapsedSeconds` — wall clock.

A one-line check:

```bash
python3 - <<'EOF'
import json
a=json.load(open("results/kl000-confirmatory.json"))
b=json.load(open("results/kl000-reproduction.json"))
drop=lambda d:{k:v for k,v in d.items() if k not in("label","environment")}
for p in ("exhaustive","randomized"):
    a["phases"][p].pop("elapsedSeconds"); b["phases"][p].pop("elapsedSeconds")
print("MATCH" if drop(a)==drop(b) else "DIFFERS")
EOF
```

## Run the permanent suite

```bash
cd <repo root>
PYTHONPATH=. python3 -m pytest research/knowledge-ledger/experiments/KL-000/tests/ -q
```

54 tests. **Seven of them pass because the evaluator is vulnerable** — every
test named `test_limit_*` asserts that a weakness is present, so that closing or
losing one breaks a test instead of changing behaviour silently. A green run is
not a claim that the system resisted every attack. See `PROTOCOL.md` and
constraints `ADV-001`..`ADV-007`.

## Verify the registration was frozen first

```bash
P=research/knowledge-ledger/experiments/KL-000
test "$(git log -1 --format=%H -- $P/preregistration.json)" = "$(cat $P/PROTOCOL-COMMIT.txt)" \
  && echo "preregistration unedited since registration"
```

The commit in `PROTOCOL-COMMIT.txt` (`c977347`) must also precede the commit
carrying `results/`. `preregistration.json` keeps `"protocolCommit": null`
deliberately — see `PROTOCOL.md`, "Why `protocolCommit` is deliberately null".

## What a successful reproduction establishes

That the reference evaluator, within the declared bounds, did not let a recorded
copy change evidential mass and did not let an incomplete search yield an
absence conclusion.

**It does not establish** that the dual ledger recovers truth, that declared
roots are genuinely independent, that the invariants hold outside the declared
bounds, or that any real-world evidence process is improved. It is a conformance
result in a frozen synthetic model.

Read `results/kl000-effective-sample.json` before quoting the million. 75.7% of
randomized worlds fail closed and never produce a receipt, so eight of the ten
invariants were exercised on 243,381 worlds, not 1,000,000.
