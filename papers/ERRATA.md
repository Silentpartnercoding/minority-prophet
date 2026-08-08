# Errata — "The Minority Prophet Property"

Issued 2026-08-05 following an independent formal-methods and falsification
audit of the mathematical core. Authoritative statuses:
`formal/THEOREM-LEDGER.json`. Corrected statements: `formal/PROOFS.md`.
Minimal witnesses: `formal/COUNTEREXAMPLES.md`. Scope: `formal/CLAIM-SCOPE.md`.

Affected: `minority-prophet-v1.0.md`, `minority-prophet-v1.0.1.md`, and
`MINORITY-PROPHET-PAPER-v0.9.md` where noted.

The corrections below have been applied inline to **v1.0.1** only, each marked
`[E1]`…`[E5]`. v1.0 and v0.9 are left as historical record and carry a banner
pointing here. Nothing has been deleted.

**None of these corrections invalidates Lemma 1, Theorem 1 or Theorem 3.** All
three are now compiler-ratified, along with Theorem 2 in its correct form,
Theorems 4/4′/5, and one new result. The corrections concern *statements* that
were broader than what is true, and one that was never machine-checked despite
being reported as such.

---

## [E1] Theorem 2 — the hypothesis was dropped between v0.9 and v1.0

**v1.0 / v1.0.1 said:**
> **Theorem 2 (Copy invariance).** Duplicating any claim leaves the verdict
> unchanged.

**Status: FALSE as written.**

**Corrected:**
> **Theorem 2 (Recorded-copy invariance).** Duplicating any claim *with its
> parent edge recorded* — same assertion, parent = the original — leaves the
> verdict unchanged.

v0.9 stated this correctly: *"Duplicating any claim (same assertion, parent =
original)"*. The parenthetical was lost in the v1.0 revision. This errata
restores the author's own earlier formulation.

**Why it matters.** A copy whose provenance is *not* recorded is a parentless
claim — an evidence root — and it reverses verdicts:

```
[-1,-1,-1] / [1,1,0]           S₁={0,1} S₀={2}      verdict 1
copies recorded:               [-1,-1,-1,2,2] / [1,1,0,0,0]   verdict 1  ✓
the same copies, unrecorded:   [-1,-1,-1,-1,-1] / [1,1,0,0,0] verdict 0  ✗
```

Undetected copying is the threat this paper is about, so the unqualified form
points away from the paper's own subject. Compiled witness:
`CE01_unrecorded_copies_flip_the_verdict`. Compiled correct form:
`MinorityProphet.copy_invariance`.

---

## [E2] Theorem 4 — "cross-side flow" is a factor of two out

**v1.0 / v1.0.1 said:**
> the verdict flips only if net **cross-side** phantom root flow meets or exceeds
> the honest margin … **The attacker's budget equals the margin** … flow equal to
> the margin forces abstention (denial); reversal (deception) requires margin+1.

**Status: TRUE in one unit, FALSE in the other, and the unit was not stated.**

Flow as defined in the proof is `p₀ − p₁`, net **per-side** root gain. In that
unit every sentence above is correct and now compiled
(`T4_flip_requires_margin`, `T4'_flow_eq_margin_abstains`,
`T4'_reversal_needs_margin_succ`).

Read as "roots crossing sides" — which the phrase *cross-side flow* invites and
which the security sentence "the attacker's budget equals the margin" implies —
it is wrong by 2×. One action that converts a root from the winning to the losing
side is worth **two** units: `−1` to one side, `+1` to the other. Measured in
conversions, reversal costs `⌊margin/2⌋ + 1`. **At margin 8: 5 actions, not 9.**

Confirmed on constructed worlds: conversion reversed the verdict at or below the
margin in **4,638 / 4,638** decisive worlds, and the minimum cost equalled
`⌊m/2⌋+1` in **4,638 / 4,638**
(`verification/independent_check_2026-08.py`).

---

## [E3] Theorem 5 — the universal claim needs a hypothesis, and the doctrine does not follow

**v1.0 / v1.0.1 said:**
> Universally (T5): k root-integrity errors of any kind — accidental or
> adversarial — cannot change a margin>k verdict; **min_flip_budget ≥ 2
> therefore confers proved immunity to any single key compromise or operational
> error.**

**Status: BOTH CLAUSES FALSE.**

*First clause.* T5 requires that **assertions do not change**. Without it, a
single side conversion changes a margin-2 verdict while leaving the root set
completely untouched — zero root-set error, `k = 0 < 2`. Compiled witness:
`T5_needs_assert_fixed`.

*Second clause.* T5 counts **units of root-set change**, and one real-world
incident is not one unit:

- deleting **one** claim record orphans every child at once — reversed a margin-3
  verdict (CE-04);
- compromising **one** signing key mints unboundedly many roots — reversed a
  margin-3 verdict (CE-05).

**Corrected:**
> **Theorem 5.** If two side-consistent worlds have the *same assertions* and
> their root sets differ by at most `k` elements in total, a verdict with
> `|margin| > k` survives unchanged, and one with `|margin| ≥ k` cannot be
> reversed.

Compiled as `root_error_tolerance` and `no_reversal_of_margin_ge`. The corrected
form is also *more general* than the original: it makes no reference to "edits",
so one statement covers arbitrary simultaneous edge changes, claim insertions and
claim deletions.

**No operational immunity claim follows from T5 alone.** Converting proved units
into an incident budget requires a bound on roots-per-identity and a no-hard-delete
storage model — added as **R1.4** in `PROVENANCE-REQUIREMENTS.md` v3.

---

## [E4] Verification status — one Lean claim and one machine-check claim were wrong

**v1.0 / v1.0.1 said:**
> Lean 4: Theorem 3 fully proved; Lemma 1 and Theorem 1 stated with proofs in
> progress.

**Status: the Lean file could not compile at all.** `formal/MinorityProphetV2.lean`
uses `Fin.strongRecOn` in two proofs; no such constant exists in Mathlib
(checked at `905b958` / Lean 4.32.2). The paper's phrasing ("no claim herein
depends on their completion beyond the paper proofs") was appropriately hedged,
but "Theorem 3 fully proved" implied a compiling artifact and there was none.

**Now true:** Lemma 1, Theorems 1, 2, 3, 4, 4′, 5, a new parity theorem, and
three necessity witnesses all compile from a pinned clean environment
(`formal/lean/`, Lean 4.32.2, Mathlib `905b958`, zero `sorry`, no added axioms).

**Separately**, the reported check *"flow == margin yielded abstain in
4,638/4,638 decisive worlds"* was not evidence for anything: the function
enumerated worlds only to read off the margin, then evaluated `d − flow` in
closed form. It never constructed a second world and could not fail for any
input. It has been rewritten to construct worlds explicitly; the corrected
version reproduces the abstention result **and** exposes the conversion cost in
[E2].

---

## [E5] "Attribution accuracy is irrelevant" — qualifier must travel with the claim

The papers already state the qualifier correctly in Theorem 1 (*"among
non-roots"*, with the 33.0% figure). It is flagged here only because the
unqualified form circulates in summaries. **Attribution is irrelevant among
non-roots. Root-set integrity is load-bearing.**

---

## Not a correction, but recorded

- **Model mismatch.** The formal artifacts modelled a single-parent *forest*;
  `provenance/graph.py` and `FOUNDATIONS.md` describe a multi-parent *DAG*. The
  core has been re-formalized on the DAG, which subsumes the forest. Re-running
  every statement in the DAG produced **0 violations**, so the mismatch never
  invalidated a published result — but it made side-separation (R2) look far
  milder than it is: in a DAG, R2 forbids any claim synthesised from evidence on
  both sides.
- **Reproducibility.** Until v3, a clean clone of the repository failed 2 of its
  own 40 tests because the canonical manifests were gitignored. Fixed by tracking
  them.
- **A refuted audit hypothesis, kept:** the audit predicted the forest/DAG
  mismatch would break Theorems 1, 2 and 5. It did not. All three survive.


---

# Additions — 2026-08-08 (KL-000 conformance program, RUN-20260807-10)

Issued from the specification-to-paper traceability audit (TRC-101,
`research/knowledge-ledger/experiments/KL-000/TRACEABILITY-v1.3.0.json`).
Applied inline to **v1.0.4** only, each marked `[E6]`…`[E8]`. These are
scope declarations and one gap closure, not corrections of false statements;
no theorem, proof, or result changes. v1.0.3 and earlier are preserved.

## [E6] Section 3 — the abstention threshold was an undeclared scope condition

Section 3 permits abstention "optionally below a margin threshold". Every
experimental result in the paper and its conformance program was produced at
**τ = 0** (abstention on exact ties only), and no document declared that
until TRC-101's audit (rule CF-threshold, RUN-20260807-9). v1.0.4 states the
evaluated configuration. Scope condition on all published results; no claim
changes.

## [E7] Section 9 — search-ledger identifier uniqueness was a gap in the paper's own thesis

The theorems prove copies do not multiply evidence on the **evidence**
ledger. The identical attack on the **search** ledger — padding with
duplicate entries for an already-searched location to inflate coverage — had
no paper coverage; section 9 was silent. Both independently written
implementations refused duplicate identifiers unprompted (neither was told
to by any document), and KL-000 registered the rule as hard invariant I11
(protocol v1.1.0, repair R3). v1.0.4 closes the gap with a MUST.

## [E8] Theorem 1 — proved, but only shadow-tested in the evaluated schema

Immunity to root-preserving, side-consistent rewiring is proved and
compiler-ratified. The schema the conformance program evaluates (v0.1)
carries no parent edges, so the theorem's structure does not exist in the
tested model; KL-000's I7 (permutation invariance) is a strictly weaker
shadow, declared as such in the traceability map. v1.0.4 records this where
a reader of the theorem will find it. An end-to-end test requires a
lineage-bearing schema.
