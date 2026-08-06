# REPRODUCE.md

Exact commands to reproduce every result in this audit from a clean environment.
Recorded results are from 2026-08-05 on macOS 15 (Darwin 25.5.0, arm64).

Substitute your own paths for `<REPO>` (a checkout of `minority-prophet`),
`<GATE>` (a checkout of `minority-prophet-gate`) and `<AUDIT>` (this worktree).
No absolute paths from the audit machine appear in any deliverable.

---

## 0. Prerequisites

| Component | Pinned version | How it is pinned |
|---|---|---|
| Python | ≥ 3.11 (audit ran 3.14.6) | `pyproject.toml: requires-python` |
| pytest | any (audit ran 9.1.1) | not pinned upstream |
| Lean toolchain | `leanprover/lean4:v4.32.2` | `formal/lean/lean-toolchain` |
| Mathlib | `905b95818eb32af7874a58b427f50c1711a5e96c` (tag `v4.32.2`) | `formal/lean/lake-manifest.json` |
| elan | 4.2.3 | installer below |

```bash
curl -sSf https://elan.lean-lang.org/elan-init.sh -o elan-init.sh
sh elan-init.sh -y --default-toolchain none
export PATH="$HOME/.elan/bin:$PATH"

python3 -m venv .venv && .venv/bin/pip install pytest
```

---

## 1. Pinned Lean build — the only step that ratifies a proof

```bash
cd <REPO>/formal/lean
lake exe cache get      # downloads Mathlib oleans; first run on a cold machine
                        # fetches ~8,639 files from the Mathlib CDN
lake build
```

**Recorded result:** `Build completed successfully (3004 jobs).` — exit 0.
Warnings only (two unused-binder-name linter notes in `Margin.lean`). No errors.

### 1a. Clean-room verification of the same build

```bash
mkdir /tmp/leanclean && cd /tmp/leanclean
cp <AUDIT>/formal/lean/{lean-toolchain,lakefile.toml,lake-manifest.json,MinorityProphetCore.lean} .
cp -R <AUDIT>/formal/lean/MinorityProphetCore .
lake exe cache get && lake build
```

**Recorded result:** exit 0, `Build completed successfully (3004 jobs)`, from six
source files plus three pin files and nothing else. The clean room independently
resolved and cloned Mathlib at `905b958`.

**Honest caveat:** this run reported `No files to download / Decompressed 8638
already-cached file(s)` because the machine already held Mathlib's oleans in the
user-level cache `~/.cache/mathlib` (466 MB). That cache is a content-addressed
download cache, so the run is a legitimate clean-*project* reproduction, but it
is **not** a cold-machine reproduction. On a machine with an empty
`~/.cache/mathlib`, step 1 downloads ~8,639 files first. This has not been
tested here and should not be claimed.

### 1b. Axiom and placeholder audit — required before citing any proof

```bash
cd <REPO>/formal/lean
cat > /tmp/axcheck.lean <<'EOF'
import MinorityProphetCore
open MinorityProphet
#print axioms side_locality
#print axioms immunity
#print axioms immunity_pointwise
#print axioms copy_invariance
#print axioms margin_addCopy
#print axioms majority_not_copy_invariant
#print axioms margin_diff_le_rootSet_diff
#print axioms root_error_tolerance
#print axioms no_reversal_of_margin_ge
#print axioms T4_flip_requires_margin
#print axioms T4'_flow_eq_margin_abstains
#print axioms T4'_reversal_needs_margin_succ
#print axioms margin_parity_of_rootSet_eq
#print axioms no_abstention_of_odd_margin
#print axioms CE01_unrecorded_copies_flip_the_verdict
#print axioms CE02_conversion_moves_margin_by_two
#print axioms T5_needs_assert_fixed
#print axioms CE06_root_supports_both_sides
EOF
lake env lean /tmp/axcheck.lean
grep -rn "sorry\|admit\|native_decide\|^axiom " MinorityProphetCore/
```

**Recorded result:** every theorem reports
`depends on axioms: [propext, Classical.choice, Quot.sound]`, except
`majority_not_copy_invariant`, which `does not depend on any axioms`.
The `grep` returns nothing. Zero `sorry`, zero `native_decide`, zero added
axioms.

---

## 2. Counterexample regressions (this audit)

```bash
cd <AUDIT>
.venv/bin/python -m pytest audit/test_counterexamples.py -q
```

**Recorded result:** `32 passed` — exit 0. (27 before the remediation commit; CE-09…CE-12 were rewritten to pin the *repaired* behaviour and gained four new cases.)

These tests assert the *counterexamples still hold*. A failure means a hole was
closed (good) or a witness decayed (must be re-derived) — either way it must be
investigated, not silenced.

---

## 3. Falsification harness (this audit)

```bash
cd <AUDIT>/audit
../.venv/bin/python falsify.py            # human readable
../.venv/bin/python falsify.py --json     # machine readable
```

**Recorded results (exact):**

| check | result |
|---|---|
| forest, side-consistent worlds n≤6 | 5,912 |
| forest Lemma 1 violations | 0 |
| forest T1 root-preserving rewirings | 116,032 |
| forest T1 violations | 0 |
| **DAG** side-consistent worlds n≤4 | 252 |
| **DAG** Lemma 1 violations | 0 |
| **DAG** T1 rewirings checked | 1,992 |
| **DAG** T1 violations | 0 |
| **DAG** T2 duplications tested | 962 |
| **DAG** T2 violations | 0 |
| **DAG** single-edge edits checked | 1,072 |
| **DAG** edits moving >1 root-count | 0 (max movement 1) |
| non-SC worlds n≤5 | 3,410 |
| non-SC worlds with a root on **both** sides | 3,410 (100%) |
| witnesses emitted | **10** (CE-01…CE-08, CE-11, CE-12) |
| CE-09 / CE-10 | no longer reproduce — repaired in `provenance/graph.py` |

---

## 4. Repository verification scripts

```bash
cd <REPO>
<AUDIT>/.venv/bin/python verification/independent_check_2026-08.py
<AUDIT>/.venv/bin/python verification/r1_degradation_curve.py
```

**Recorded result — `independent_check_2026-08.py`, exit 0, reproduces the
repository's published figures exactly:**

```
side_consistent_worlds: 5912          t1_rewirings: 116032
lemma1_violations: 0                  t1_violations: 0
rootchanging_rewirings: 1221780       rootchanging_verdict_changes: 117236
duplications_tested: 4166             t2_violations: 0
majority_copy_variance_witnesses: 592 nolineage_vs_majority_mismatches: 0
non_sc_worlds: 44450                  worlds_with_root_on_both_sides: 44450
root_preserving_edits: 22032          root_preserving_flips: 0
root_changing_edits: 28368            root_changing_flips: 9364  (rate 0.3301)
```

`check_t4_tightness` was **rewritten** in the remediation commit; the original
never constructed a second world and could not fail (ledger F2). The corrected
function builds `W'` explicitly under two adversary shapes:

```
addition_flow_eq_margin_yields_abstain: 4638   addition_flow_eq_margin_yields_flip: 0
addition_margin_plus_one_reverses: 4638        conversion_decisive_worlds: 4638
conversion_reversed_at_or_below_margin: 4638
conversion_min_cost_equals_floor_margin_half_plus_one: 4638
odd_margin_abstentions_via_conversion: 0
```

Reading: T4' holds in `p₀ − p₁` units (addition column). Measured in adversary
**actions**, conversion beat the published budget in **every** decisive world,
at exactly `⌊m/2⌋+1`. The zero in the last row is the parity theorem (T6).

`r1_degradation_curve.py`: exit 0, pooled P(any change) 0.245 / 0.212 / 0.269 /
0.248 and P(full reversal) 0.000 / 0.114 / 0.108 / 0.149 for k = 1..4. This is a
**randomized experiment**, not a proof and not an exhaustive check.

---

## 5. Existing Python suites

```bash
cd <REPO> && <AUDIT>/.venv/bin/python -m pytest -q
cd <GATE> && <AUDIT>/.venv/bin/python -m pytest -q
cd <GATE> && <AUDIT>/.venv/bin/python -m minority_prophet.verify_multivalue
```

**Recorded results:**

| suite | result |
|---|---|
| `minority-prophet` (working copy) | **40 passed** |
| `minority-prophet` (**clean clone**) | **40 passed** — fixed, see step 6 |
| `minority-prophet-gate` | **47 passed, 2 subtests passed** |
| Gate `verify_multivalue` | `worlds=2955 rewirings=11031 violations=0`, exit 0 |

> Gate `verify_multivalue` now reports its coverage split. **Measured: 2,955 of
> 2,955 worlds enumerated exhaustively, 0 sampled** — the sampling fallback never
> fires at the shipped parameters, so the published result was exhaustive in
> fact. The first pass of this audit stated otherwise; ledger entry F3 has been
> corrected. The hazard was latent (any increase to `n` or the alphabet would
> have downgraded the evidence class silently), and is now visible on every run.

---

## 6. Clean-clone reproduction — **fixed**

```bash
git clone <REPO> /tmp/postfix
git -C /tmp/postfix checkout <AUDIT-REVISION>
cd /tmp/postfix && <VENV>/bin/python -m pytest -q
```

**Before the remediation commit:** `2 failed, 38 passed` — exit 1.
`.gitignore:36` excluded `results/*.json`, which
`tests/test_canonical_records.py` requires, so the suite passed only where those
untracked files already existed.

**After:** `40 passed` — exit 0. `.gitignore` now negates
`results/*.manifest.json` and `results/resolved-weather-v0.1.json`. Every
artifact bound by a canonical manifest re-verifies from the clean clone:

```
canonical artifacts verified, failures: 0
```

That includes `aggregation/semantic.py`, whose bytes are unchanged — the
corrected aggregator was added as `aggregation/root_vote.py` rather than
edited in place, precisely so the canonical record stays intact.

The audit fixtures also run from the clean clone: `32 passed`.

---

## 7. Summary of exit codes

| step | command | exit |
|---|---|---|
| 1 | `lake build` (audit worktree) | **0** |
| 1a | `lake build` (clean room) | **0** |
| 1b | axiom audit | **0**, standard axioms only, 0 `sorry` |
| 2 | counterexample regressions | **0** (32 passed) |
| 3 | `falsify.py` | **0** (10 witnesses; CE-09/CE-10 repaired) |
| 4 | `independent_check_2026-08.py` | **0** |
| 4 | `r1_degradation_curve.py` | **0** |
| 5 | `minority-prophet` pytest, working copy | **0** (40 passed) |
| 5 | `minority-prophet-gate` pytest | **0** (47 passed) |
| 5 | Gate `verify_multivalue` | **0** |
| **6** | **`minority-prophet` pytest, clean clone** | **0 (40 passed)** — was 2 failed |

**All checks pass.** The one failure found by the audit (a packaging defect that
made the canonical records unreproducible outside one machine) was fixed by
tracking the manifests, not by weakening the test.
