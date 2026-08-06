# The formal core: compiler-ratified statements and their exact scope

**Status: v3, 2026-08-05.** Every theorem below is compiled by Lean 4.32.2
against Mathlib `905b95818eb32af7874a58b427f50c1711a5e96c`, with zero `sorry`,
zero `native_decide`, and no axioms beyond `propext`, `Classical.choice` and
`Quot.sound`. Sources: `formal/lean/`. Reproduce: `audit/REPRODUCE.md`.

This file supersedes v2. v2's statements were proofs on paper only; four of
them were wrong or unqualified, and the corrections are recorded in §7 rather
than deleted. Machine-readable status for every claim:
`formal/THEOREM-LEDGER.json`. What the core does *not* establish:
`formal/CLAIM-SCOPE.md`.

---

## 1. Definitions

A **world** `W` on `n` claims is
`(parents : Fin n → Finset (Fin n), assert : Fin n → Bool)` with
`acyclic : ∀ i j, j ∈ parents i → j < i`.

The index doubles as the time order; acyclicity is therefore structural, not an
extra hypothesis to discharge.

> **Changed in v3.** v2 modelled `parent : C → Option C` — a **forest**, in which
> every claim has at most one parent and exactly one root. The implementation
> (`provenance/graph.py`: `copied_from` is a tuple, `roots()` returns a
> frozenset) and `FOUNDATIONS.md` both describe a **DAG**. v3 formalizes the
> DAG. It subsumes the forest, so nothing was weakened to close a proof.
> Re-running the v2 statements in the DAG produced 0 violations across 252
> side-consistent worlds, 1,992 rewirings, 962 duplications and 1,072 single-edge
> edits, so the mismatch never invalidated a result — but it did make R2 look far
> milder than it is (§6, CE-07).

- `SideConsistent W` ⟺ `∀ i j, j ∈ parents i → assert j = assert i`.
- `rootsOf W i` = the parentless ancestors of `i`.
- `rootSet W` = `{ i : parents i = ∅ }`.
- `sideRoots W a` = `⋃ { rootsOf W i : assert i = a }` — the paper's `S_a`.
- `F W` = `one` if `|S_true| > |S_false|`, `zero` if `<`, else `abstain`.
- `margin W` = `|S_true| − |S_false|`, **signed**, over `ℤ`.
- `flow W W'` = `margin W − margin W'`.

**`flow` is measured in units of net per-side root gain (`p₀ − p₁`).** It is not
a count of adversary actions. One action that *converts* a root from one side to
the other contributes **2**. Every use of "flow", "budget" or "margin" below
states its unit, and so must every downstream use (§7 correction C4).

**Not defined anywhere, and load-bearing:** when two roots are *the same root*.
`S_a` is a set, so the verdict is a function of the identity criterion. Lean
makes identity the index; `provenance/graph.py` makes it an opaque
caller-supplied string. Any de-duplication or canonicalisation step is inside the
trusted base. Ledger `U1`.

---

## 2. Lemma 1 — side-locality

> Under side-consistency, `S_a(W)` is exactly the set of `a`-asserting
> parentless claims.

`side_locality` · `formal/lean/MinorityProphetCore/Locality.lean`

This is the only place side-consistency is consumed. Everything below is
counting arithmetic on top of it. Two immediate consequences, also compiled:
`sideRoots_disjoint` (no root supports both sides) and `card_sideRoots_add`
(the side counts sum to the number of roots).

---

## 3. Theorem 1 — immunity

> If `W` and `W'` are side-consistent, have the **same assertions**, and have the
> **same root set**, then `F W = F W'` — however different their lineage.

`immunity`, and `immunity_pointwise` for the phrasing v2 used ·
`formal/lean/MinorityProphetCore/Immunity.lean`

**Generalized from v2.** v2 restricted this to rewirings that "only re-target
existing edges, never delete or create". The compiled form quantifies over pairs
of worlds, so it additionally covers edge additions and deletions that leave the
root set fixed.

**Interpretation.** Who-copied-whom may be arbitrarily wrong without moving any
verdict. Lineage *accuracy* is not load-bearing; side separation and root
integrity are. This remains the core's strongest and most useful result.

**What it does not say.** "Attribution is irrelevant" holds **among non-roots
only**. A single root-set-disturbing edit changes verdicts 33.0% of the time
pooled (9,364/28,368 at n=6), concentrated entirely on margin-1 decisions.

---

## 4. Theorem 2 — recorded-copy invariance

> Appending a claim that **records a parent edge** to an existing claim `c`, and
> asserts what `c` asserts, leaves both side-root counts and the verdict
> unchanged.

`copy_invariance`, `margin_addCopy` · `formal/lean/MinorityProphetCore/Copy.lean`

v2 listed this as future work ("the Lean cost is the embedding plumbing"). It is
now compiled.

> ### ⚠ Never state this as "adding copied claims cannot change the verdict."
>
> That sentence is **false**, and false in the direction of this project's own
> threat model. A copy whose provenance is *not* recorded is a parentless claim —
> a root — and it reverses verdicts:
>
> ```
> [-1,-1,-1] / [1,1,0]            → S₁={0,1} S₀={2}     verdict 1
> copies of claim 2, recorded:
> [-1,-1,-1,2,2] / [1,1,0,0,0]    → verdict 1           unchanged ✓
> the same copies, unrecorded:
> [-1,-1,-1,-1,-1] / [1,1,0,0,0]  → S₁={0,1} S₀={2,3,4} verdict 0  REVERSED ✗
> ```
>
> Compiled as `CE01_unrecorded_copies_flip_the_verdict`. Undetected copies are
> governed by Theorem 5, not by this theorem. Detection is R1's job and is
> outside the mathematics.

**Theorem 3 (majority voting is not copy-invariant)** —
`majority_not_copy_invariant`. Explicit witness; establishes that root counting
is not vacuously equivalent to head counting.

---

## 5. Theorems 4, 4′, 5, 6 — margin arithmetic

All in `formal/lean/MinorityProphetCore/Margin.lean`.

### T4 — flip condition
> `F W = one` and `F W' ≠ one` implies `flow W W' ≥ margin W`.

`T4_flip_requires_margin`. The attacker's budget, **in units of `p₀ − p₁`**,
equals the true root margin.

### T4′ — tightness
> Flow of exactly the margin yields **abstention**; reversal requires
> `margin + 1`. **Units of `p₀ − p₁`.**

`T4'_flow_eq_margin_abstains`, `T4'_reversal_needs_margin_succ`.

Measured in **root conversions** instead, reversal costs `⌊margin/2⌋ + 1`.
Confirmed on constructed worlds by `verification/independent_check_2026-08.py`:
conversion reversed at or below the margin in **4,638 / 4,638** decisive worlds,
and the minimum cost equalled `⌊m/2⌋+1` in **4,638 / 4,638**.

### T5 — root-error tolerance
> If `W` and `W'` are side-consistent, have the **same assertions**, and their
> root sets differ by at most `k` elements in total, then a verdict with
> `|margin W| > k` survives unchanged; and one with `|margin W| ≥ k` cannot be
> reversed.

`root_error_tolerance`, `no_reversal_of_margin_ge`, and the underlying counting
bound `margin_diff_le_rootSet_diff`.

**Narrowed and generalized from v2.**
- *Narrowed:* the equal-assertions hypothesis is new, and it is **necessary** —
  `T5_needs_assert_fixed` compiles a witness with an identical root set (zero
  root-set error) in which a single side conversion changes a margin-2 verdict.
- *Generalized:* the compiled form says nothing about "edits". It bounds the
  margin by the root-set symmetric difference, so one statement covers arbitrary
  simultaneous edge changes, claim insertions and claim deletions.

### T6 — conversion parity *(new in v3)*
> With the root set held fixed, the margin's parity is invariant. Hence a pure
> conversion attack can never produce abstention from an **odd** margin.

`margin_parity_of_rootSet_eq`, `no_abstention_of_odd_margin`. Confirmed on
constructed worlds: 0 odd-margin abstentions via conversion across all 4,638
decisive worlds.

An attacker restricted to relabelling attested roots cannot force a tie at odd
margin — the cheapest outcome available is full reversal. "Denial costs the
margin, deception costs margin+1" therefore does not hold action-for-action.

---

## 6. Assumption boundaries

These are not refutations. They record how load-bearing each hypothesis is.
Full detail and minimal witnesses: `formal/COUNTEREXAMPLES.md`.

- **Without side-consistency the aggregator does not degrade — it
  double-counts.** In **44,450 / 44,450** non-side-consistent worlds at n≤6, the
  literal `S_a` places some root in *both* side sets. Compiled witness:
  `CE06_root_supports_both_sides`.
- **In the DAG, side-consistency forbids synthesis**, not merely "camp
  blending": a claim that weighs evidence from both sides violates R2. In the
  single-parent forest this case cannot be written down, which is why R2 looked
  mild. Enforced at ingest since v3 by `provenance.EvidenceGraph`
  (`SideConsistencyError`); pass `strict=False` to record instead of reject.
- **One real-world incident is not one unit.** Deleting one claim record orphans
  every child at once; one compromised signing key mints unboundedly many roots.
  Converting T5's units into an incident budget requires **R1.4** in
  `PROVENANCE-REQUIREMENTS.md`, which is a requirement, not a theorem.
- **Root identity is undefined** (ledger `U1`) and **the meaning of absent
  provenance was contradictory** across modules (ledger `U2`); the latter is now
  an explicit, named policy on `aggregation.root_vote.verdict`.

---

## 7. Corrections against v2 — recorded, not erased

| ID | v2 said | Status | Correct form |
|---|---|---|---|
| **C1** | "Adding a duplicate claim … leaves `S_a` and `F` unchanged", restated downstream as *"adding copied claims cannot change the verdict"* | Restatement **falsified** (CE-01) | Copies **whose parent edge is recorded**. §4 |
| **C2** | T5: "k root-integrity errors, accidental or adversarial, cannot change a verdict with margin > k" | **Falsified** (CE-02) | Add the equal-assertions hypothesis; count units of root-set change. §5 |
| **C3** | T5 doctrine: "min_flip_budget ≥ 2 confers proved immunity to any single key compromise or ops error" | **Falsified** (CE-04, CE-05) | No such implication. Needs R1.4. §6 |
| **C4** | T4′: "net **cross-side** phantom root flow of exactly the margin forces abstention; reversal requires margin+1" | **Falsified under the cross-side reading** (CE-03) | True in units of `p₀ − p₁`; conversions cost `⌊m/2⌋+1`. §5 |
| **C5** | "the attestation budget an attacker must defeat equals the true root margin" | Unit unstated | True in `p₀ − p₁`; ~2× overstated in actions. §5 |
| **C6** | "`MinorityProphetV2.lean` contains an uncompiled Lean proof candidate … translate, don't redesign" | **Cannot compile as written** | It calls `Fin.strongRecOn`, which does not exist in Mathlib. A replacement principle (`lineage_induction`) was required. |
| **C7** | "Exhaustive: flow==margin yielded abstain in 4,638/4,638 decisive worlds" | **Not evidence** | The check never constructed a second world and could not fail. Rewritten; the corrected version does construct worlds and is reported in §5. |
| **C8** | "Attribution is irrelevant" | True with a qualifier that must not be dropped | Among **non-roots** only. §3 |

Two structural findings with no v2 counterpart: the forest/DAG model mismatch
(§1) and the clean-clone reproducibility defect (CE-13, fixed in v3 by tracking
the canonical manifests).

**Negative result, kept:** the audit's own opening hypothesis — that the
forest/DAG mismatch would break T1/T2/T5 — was **refuted**. All four survive in
the DAG. The mismatch costs expressiveness, not soundness.

---

## 8. Evidence classes — do not mix these

| Class | Meaning | Here |
|---|---|---|
| **Theorem** | compiled from a pinned clean environment | §2–§5, `formal/lean/` |
| **Finite exhaustive check** | every case in a bounded domain | `verification/independent_check_2026-08.py`, `audit/falsify.py` |
| **Randomized experiment** | sampled; reports a rate | `verification/r1_degradation_curve.py` |
| **Implementation invariant** | true until the code changes | `provenance/graph.py`, `aggregation/root_vote.py` |
| **Security assumption** | imported; theorems go vacuous without it | R1, R1.4, root identity |
| **Speculative extension** | not implemented, not proved | `formal/EXTENSION-SOCKETS.md` |

A statement does not change class by being repeated. **A Lean file that does not
compile is not a proof** — which is exactly what `formal/MinorityProphetV2.lean`
was, and it is retained only as a historical record.
