# Reproducing KL-000 under protocol v1.1.0

Everything in `REPRODUCE.md` applies; this file adds only what v1.1.0 changes.
No network, no credentials, standard library only, CPython 3.11+.

## Run it

From the repository root:

```bash
cd research/knowledge-ledger/experiments/KL-000
python3 src/run_kl000.py --phase all --preregistration preregistration-v1.1.0.json \
    --out results --label reproduction-v1.1.0
```

Without `--preregistration` the runner executes the v1.0.0 registration,
exactly as before.

## What must come out

`results/kl000-reproduction-v1.1.0.json` must agree with the committed
`results/kl000-confirmatory-v1.1.0.json` on every field
`REPRODUCE.md` lists, plus:

| Field | Required value |
|---|---|
| `protocolVersion` | `1.1.0` |
| `phases.fixture.controls` | **11 entries**, C01–C11, all `passed` |
| C11 `differences` | `[]` — including the pinned `contentDigest` comparison |

Every scientific number is **identical to the v1.0.0 confirmatory run**, and
that identity is itself the registered prediction
(`preregistration-v1.1.0.json`, `expectedIdenticalToRun1`): the four v1.1.0
repairs document behaviour the evaluator already had, so nothing may move.

```
exhaustive   176120 worlds   110840 receipts   65280 fail-closed   0 violations
             conclusions: absent 160 / not_established 49480 / present 41820 / supported 19380
randomized   1000000 worlds  243381 receipts   756619 fail-closed  0 violations
             conclusions: absent 1092 / not_established 119228 / present 81792 / supported 41269
baselines    B1 634440   B2 26880   B3 26208   B4 189720   (all caught)
fail-closed  exactly one cause per phase: ValueError: One root cannot support opposing sides.
```

A moved number is not a platform quirk and not a partial success; it falsifies
the documentation-only claim and must be reported as a finding.

Comparison check against the v1.0.0 confirmatory document (label,
environment, elapsed timings, protocol version, and the fixture phase differ
by design; everything else must not):

```bash
python3 - <<'EOF'
import json
a = json.load(open("results/kl000-confirmatory.json"))          # v1.0.0
b = json.load(open("results/kl000-confirmatory-v1.1.0.json"))   # v1.1.0
mismatches = []
for phase in ("exhaustive", "randomized"):
    pa, pb = a["phases"][phase], b["phases"][phase]
    for key in sorted(set(pa) | set(pb)):
        if key == "elapsedSeconds":
            continue
        if pa.get(key) != pb.get(key):
            mismatches.append(f"{phase}.{key}: {pa.get(key)!r} != {pb.get(key)!r}")
for name in sorted(a["phases"]["baselines"]):
    ba, bb = a["phases"]["baselines"][name], b["phases"]["baselines"][name]
    for key in ("worldsChecked", "totalViolations", "violationsByInvariant", "caught"):
        if ba[key] != bb[key]:
            mismatches.append(f"baselines.{name}.{key}: {ba[key]!r} != {bb[key]!r}")
print("IDENTICAL" if not mismatches else "\n".join(mismatches))
EOF
```

Must print `IDENTICAL`.

## The permanent suite

```bash
cd <repo root>
PYTHONPATH=. python3 -m pytest research/knowledge-ledger/experiments/KL-000/tests/ -q
```

68 tests: the 54 v1.0.0 tests unchanged, plus 14 in `test_kl000_v110.py`
pinning R1 (tie rule), R2 (empty scope refusal), R3/I11 (duplicate location
ids), R4 (canonical bytes, digest scope, C11's pinned digest), and the
registration-integrity checks (same evaluator hash, same bounds, same seed,
controls = v1.0.0 + C11).

## Verify the v1.1.0 registration was frozen first

```bash
P=research/knowledge-ledger/experiments/KL-000
test "$(git log -1 --format=%H -- $P/preregistration-v1.1.0.json)" \
   = "$(cat $P/PROTOCOL-COMMIT-v1.1.0.txt)" && echo "v1.1.0 unedited since registration"
```

The v1.0.0 chain (`PROTOCOL-COMMIT.txt` = `c977347…`) remains independently
checkable and independently binding; v1.1.0 does not touch it.

## Cross-implementation status

The digest in fixture C11 is the first KL-000 value that a second
implementation can be *wrong about* rather than merely different from: under
v1.0.0, canonicalisation was self-declared (independent finding F10) and
digests could not agree in principle. The independent implementation's re-run
against v1.1.0 is KL-000's next gate and a separate commission; nothing in
this repository executes it.
