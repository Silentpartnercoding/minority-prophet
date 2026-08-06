# Formal core audit and remediation report — 2026-08-05

> **Two commits.** `bd08868` is the audit (findings only, repository untouched).
> `f64a6a6` applies the corrections. The audit findings below are stated as
> found; §"Remediation" records what was fixed, what was deliberately left, and
> one place where the audit itself was wrong.

**Outcome:** narrowed (with falsifications). Outcome A was not reached, because
three statements as written in the repository are false; outcome B's conditions
are met and exceeded — every gap has a minimal counterexample, and every
statement has a compiled strongest-correct replacement.

**Definitions changed:** yes. Kernel version `core-v2-forest` → `core-v3-dag`.
The kernel now formalizes the multi-parent DAG that `provenance/graph.py`
implements, rather than the single-parent forest that `formal/PROOFS.md` and
`formal/MinorityProphetV2.lean` model. The DAG subsumes the forest, so no
theorem was weakened to make a proof close. T5 additionally gained one
hypothesis (proved necessary) and lost all reference to "edits".

## Theorems compiled

Lean 4.32.2, Mathlib `905b95818eb32af7874a58b427f50c1711a5e96c`, clean-room build
exit 0, zero `sorry`, zero `native_decide`, no axioms beyond
`propext`/`Classical.choice`/`Quot.sound`.

| Ledger | Lean name | Note |
|---|---|---|
| L1 | `side_locality` | the only place side-consistency is consumed |
| T1 | `immunity`, `immunity_pointwise` | generalized to pairs of worlds |
| T2 | `copy_invariance`, `margin_addCopy` | **was future work in the repo** |
| T3 | `majority_not_copy_invariant` | |
| T4 | `T4_flip_requires_margin` | |
| T4' | `T4'_flow_eq_margin_abstains`, `T4'_reversal_needs_margin_succ` | unit corrected |
| T5 | `root_error_tolerance`, `no_reversal_of_margin_ge`, `margin_diff_le_rootSet_diff` | hypothesis added, scope widened |
| T6 | `margin_parity_of_rootSet_eq`, `no_abstention_of_odd_margin` | **new result** |
| — | `CE01_…`, `T5_needs_assert_fixed`, `CE06_…` | necessity witnesses |

## Theorems narrowed

- **T5** now requires `W.assert = W'.assert`. `T5_needs_assert_fixed` proves this
  cannot be dropped. In exchange it dropped all reference to "edits" and now
  bounds the margin by the root-set symmetric difference, so one theorem covers
  arbitrary simultaneous edge changes, insertions and deletions.
- **T4'** now states its unit explicitly (`p₀ − p₁`, not roots-crossing-sides).

## Counterexamples found (13; all pinned as regression fixtures)

| ID | Kind | One line |
|---|---|---|
| CE-01 | refutes theorem | Unrecorded copies are roots and reverse verdicts |
| CE-02 | refutes theorem | One side conversion changes a margin-2 verdict (0 root-set change) |
| CE-03 | refutes theorem | Reversal costs ⌊m/2⌋+1 conversions, not m+1 |
| CE-04 | refutes doctrine | One deleted record orphans a whole subtree; reversed margin 3 |
| CE-05 | refutes doctrine | One compromised key minted 4 roots; reversed margin 3 |
| CE-06 | violates assumption | Without R2, one root serves both sides — 3,410/3,410 worlds |
| CE-07 | violates assumption | In the DAG, R2 forbids synthesis, not just camp blending |
| CE-08 | violates assumption | Root identity is undefined; one merge changes a verdict |
| CE-09 | violates assumption | `EvidenceGraph.add` accepts a cross-side edge |
| CE-10 | violates assumption | Edges may cross propositions |
| CE-11 | violates assumption | `evidence_root_vote` is order-dependent on duplicate root IDs |
| CE-12 | violates assumption | `root_id=None` claims are dropped, not abstained on |
| CE-13 | violates assumption | Clean clone fails the repo's own suite 2/40 |

## Existing claims requiring correction

1. **"Adding copied claims cannot change the verdict."** False (CE-01). Always
   say *"copies whose parent edge is recorded"*. This is the most consequential
   correction: the false form points away from the project's own threat model.
2. **"min_flip_budget ≥ 2 confers proved immunity to any single key compromise
   or ops error."** False (CE-04, CE-05). One incident ≠ one unit.
3. **"k root-integrity errors, accidental or adversarial, cannot change a verdict
   with margin > k."** False without the equal-assertions hypothesis (CE-02).
4. **"Net cross-side phantom root flow of exactly the margin forces abstention;
   reversal requires margin+1."** False under the cross-side reading (CE-03);
   true and compiled under the `p₀ − p₁` reading.
5. **"The attestation budget an attacker must defeat equals the true root
   margin."** True in `p₀ − p₁` units, ~2× overstated in adversary actions.
6. **"`MinorityProphetV2.lean` contains an uncompiled Lean proof candidate."**
   Honest as far as it goes, but it *cannot* compile: `Fin.strongRecOn` does not
   exist in Mathlib. "Translate, don't redesign" was not achievable; a
   replacement induction principle (`lineage_induction`) was required.
7. **"Exhaustive: flow==margin yielded abstain in 4,638/4,638 decisive worlds."**
   The computation never constructs a second world and cannot fail. Not evidence.
8. **"Attribution is irrelevant."** True *among non-roots* only — the repo's own
   scope note already says this; it should be inseparable from the headline.
9. **Gate `verify_multivalue` docstring says "Exhaustively check".** It samples
   200 seeded-random rewirings above 200 combinations.

## Tests and exact results

| Check | Result | Exit |
|---|---|---|
| `lake build` (audit worktree) | 3,004 jobs, warnings only | **0** |
| `lake build` (clean room, pins only) | 3,004 jobs | **0** |
| Axiom audit, 18 theorems | standard axioms only; 0 `sorry` | **0** |
| `audit/test_counterexamples.py` | **27 passed** | **0** |
| `audit/falsify.py` | 12 witnesses; DAG: 0 violations across 252 worlds / 1,992 rewirings / 962 duplications / 1,072 edge edits (max movement 1) | **0** |
| `verification/independent_check_2026-08.py` | reproduces published figures exactly (5,912 / 116,032 / 4,166 / 0 violations) | **0** |
| `verification/r1_degradation_curve.py` | randomized; P(reversal) 0.000/0.114/0.108/0.149 for k=1..4 | **0** |
| `minority-prophet` pytest (working copy) | **40 passed** | **0** |
| `minority-prophet` pytest (**clean clone**) | **2 failed, 38 passed** | **1** |
| `minority-prophet-gate` pytest | **47 passed, 2 subtests** | **0** |
| Gate `verify_multivalue` | worlds=2955 rewirings=11031 violations=0 | **0** |

One check fails: CE-13, a pre-existing packaging defect unrelated to the
mathematical core. Not worked around, not silenced.

**Audited baselines:** `minority-prophet` at `e1403a7` and
`minority-prophet-gate` at `a120274`. The Gate follow-up changed verifier
coverage reporting only; it did not change Gate or Border action semantics.

**Files produced:** `formal/{DEFINITION-AUDIT,COUNTEREXAMPLES,EXTENSION-SOCKETS,CLAIM-SCOPE}.md, audit/{HYPOTHESIS,REPRODUCE,HANDOFF}.md`, `formal/THEOREM-LEDGER.json`, `audit/{core_models,falsify,test_counterexamples}.py`, `formal/lean/` (6 Lean modules + 3 pin files)

## Recommended next assignment

1. **Correct the nine statements above** in `PROOFS.md`,
   `PROVENANCE-REQUIREMENTS.md` and the papers. Highest priority is #1 — it is
   the one a reader will repeat.
2. **Add R1.4 to the requirement stack: bound roots-per-attested-identity per
   unit time.** Without it the margin is not a budget an attacker must pay
   (CE-05), and the compiled T5 cannot be converted into any operational claim.
3. **Make R2 an enforced invariant** at `EvidenceGraph.add`, and decide whether
   the right answer is edge rejection or edge *polarity* (CE-07,
   EXTENSION-SOCKETS §3.1 — polarity is cheap and repairs a real gap).
4. **Decide what absent provenance means** (ledger U2). `PROOFS.md` promotes it
   to a root; `evidence_root_vote` deletes it. The two readings differ by the
   entire undetected-copy attack.
5. **Define root identity** (ledger U1) and declare it part of the trusted base.
6. **Fix CE-13** so the empirical evidence is reproducible; then §7 of
   EXTENSION-SOCKETS (evidence-aware memory) is nearly free — T1 already gives
   the guarantee for any root-preserving memory policy.


---

## Remediation (commit `f64a6a6`)

### Fixed

| Finding | Repair |
|---|---|
| C1 / CE-01 — T2 slogan | `formal/PROOFS.md` §4, `papers/ERRATA.md` [E1]. v0.9 had the hypothesis; it was dropped in v1.0 and is restored. |
| C2 / CE-02 — T5 missing hypothesis | Corrected statement in PROOFS.md v3; necessity compiled as `T5_needs_assert_fixed`. |
| C4 / CE-03 — "flow" unit | Unit stated everywhere; `conversions_to_reverse` is now a first-class output. |
| C7 / F2 — circular check | `check_t4_tightness` rewritten to construct worlds. Conversion beat the published budget in **4,638/4,638** decisive worlds at exactly `⌊m/2⌋+1`; odd-margin abstention via conversion **0/4,638** (T6 confirmed). |
| C6 / F1 — uncompilable Lean | `MinorityProphetV2.lean` marked SUPERSEDED, retained unmodified; `formal/lean/` is the compiling core. |
| CE-06 / CE-09 / CE-10 — R2 unenforced | `provenance.EvidenceGraph.add` rejects cross-side and cross-proposition edges. `strict=False` records them and flips `immunity_applicable` rather than hiding them. `roots()` memoised and cycle-guarded; `from_dict()` added as a validating loader. |
| CE-11 / CE-12 — aggregator defects | New `aggregation/root_vote.py`: order-independent, fails closed on conflicting roots, explicit `unattributed_policy` defaulting to fail-closed, reports both attack units and the parity flag. |
| CE-13 / F4 — clean clone failed | Canonical manifests tracked. Clean clone now **40 passed**, all canonical hashes verify. |
| U2 — absent provenance undecided | Decided and named: default `abstain_if_decisive`; both previously-contradictory readings retained as explicit policies. |

### Deliberately not changed

- **`aggregation/semantic.py` is byte-identical.** Its sha256 is bound by
  `results/los-inspired-v0.1.manifest.json` as canonical evidence for
  EXPERIMENT-001. Correcting it in place would falsify a canonical record, so the
  corrected aggregator was added alongside and the legacy defects are pinned by
  tests that state why they remain.
- **R1.4 is specified but not enforced.** No roots-per-identity limiter and no
  tombstone storage model exist. **CE-04 and CE-05 remain reachable in a
  deployment** — this is the single most important open item.
- **Root identity (U1) is still undefined**, now explicitly declared part of the
  trusted base rather than silently assumed.
- **CE-07** (side-consistency forbids synthesis in a DAG) is a scope limit, not a
  bug. Edge polarity is proposed in `formal/EXTENSION-SOCKETS.md` §3, not built.

### A correction to this audit

Ledger **F3 was overstated**. The first pass reported that the Gate multivalue
verifier "samples 200 seeded-random rewirings above 200 combinations", implying
its published result was partly randomized. Instrumenting it shows the sampling
branch **never fires** at the shipped parameters: **2,955 of 2,955 worlds
enumerated, 0 sampled**. The published result was exhaustive in fact. The real
defect is latent — any increase to `n` or the alphabet would have silently
downgraded the evidence class with no change to the output line. F3 has been
rewritten and the verifier now prints its coverage split on every run.

### Post-remediation results

| Check | Result | Exit |
|---|---|---|
| `lake build` | 3,004 jobs, zero `sorry`, standard axioms only | **0** |
| repo pytest, working copy | **40 passed** | **0** |
| repo pytest, **clean clone** | **40 passed** (was 2 failed) | **0** |
| canonical artifact hashes from clean clone | **0 failures** | **0** |
| audit fixtures | **32 passed** (was 27) | **0** |
| `falsify.py` | **10 witnesses** (CE-09/CE-10 no longer reproduce) | **0** |
| `independent_check_2026-08.py` | all prior counts reproduce; T4' section rebuilt | **0** |
| Gate pytest | **47 passed, 2 subtests** | **0** |
| Gate `verify_multivalue` | 2,955 worlds enumerated, 0 sampled, 0 violations | **0** |

Gate changes are on branch `audit/verifier-accuracy-2026-08` in a separate
worktree — docstring and reporting only. **No Gate or Border action semantics
were touched.**

## Publication recommendation

**Owner review, then publishable — with one blocker.**

The three publication blockers identified by the audit are resolved: the statements are
corrected and carry an errata trail, the two non-verifying "verifications" have
been rewritten or reclassified, and the repository passes its own suite from a
clean clone with every canonical hash intact.

**The remaining blocker is R1.4.** It is written down as a hard requirement but
nothing enforces it, so CE-04 and CE-05 are still reachable in a real
deployment. Until there is a roots-per-identity bound and a no-hard-delete
storage model, no operational immunity claim should be made in public — the
proved theorems are about units of root-set change, and nothing yet bounds how
many units one incident produces.

Everything else is technically ready for your review. Nothing has been pushed,
posted or shared.
