# PROVENANCE-REQUIREMENTS.md — what provenance must (and need not) guarantee

Status: **v3, 2026-08-05.** Supersedes v2. Derived from the compiled theorems in
`formal/lean/` (see `formal/PROOFS.md`) and Experiments 001–006 (001–002
canonical; 003–006 replica, pending canonical re-run). This file is the single
source of truth for what any provider-neutral attestation layer must provide to
the aggregation layer.

v3 changes: **R1.4 is new and is a hard requirement.** R3's unit is now stated
explicitly — the previous wording overstated the attacker's cost by roughly 2×.
R2 now has an enforcement point in code. Corrections are listed in
`formal/PROOFS.md` §7; nothing has been deleted.

---

## The requirement stack

### R1. ROOT INTEGRITY (hard requirement — attestation's job)

**Guarantee:** evidence roots cannot be manufactured or destroyed. No forged
"original observations"; no laundering a copy into an apparent root.

**Threat excluded:** sybil root-manufacturing (Douceur 2002 is the impossibility
this layer escapes by making identity/origin costly or cryptographic).

**Measurement:** root-set accuracy.

**Theorem dependency:** T1 and T5 both assume the root set is preserved; T4/T4′
price the cost of changing it. **If R1 fails, every theorem below is vacuous.**
State this in every application.

---

### R1.4 ROOTS PER IDENTITY (hard requirement — NEW in v3)

**Guarantee:** a bound on how many roots any one attested identity can create per
unit time, and a storage model in which removing one record cannot orphan
arbitrarily many claims (append-only, tombstones that preserve edges — no hard
delete).

**Why this exists.** T5 is stated in **units of root-set change**. Nothing in the
mathematics bounds how many units a single real-world incident produces, and two
ordinary incidents produce unboundedly many:

- deleting **one** claim record orphans every child at once — reversed a
  margin-3 verdict in `formal/COUNTEREXAMPLES.md` CE-04;
- compromising **one** signing key mints as many roots as the attacker likes —
  reversed a margin-3 verdict in CE-05.

Without R1.4, "margin" is not a budget an attacker must pay; it is a number an
attacker with one key can exceed at will, and the compiled T5 **cannot be
converted into any operational claim**.

**Measurement:** roots-minted-per-identity-per-window; orphans-created-per-delete
(must be 0).

**Theorem dependency:** none — this is precisely the gap the theorems do not
cover. It is the bridge between the proved unit and any incident-level statement.

---

### R2. SIDE-SEPARATION (hard requirement — the surprising minimum)

**Guarantee:** a claim can never be attributed to a root of the opposing
assertion. Camps must not blend.

Everything else about lineage may be arbitrarily wrong — **T1 (Immunity)**:
side-preserving, root-preserving, assertion-preserving change of lineage cannot
move any verdict, however the edges are rewired, added or deleted. Compiled as
`MinorityProphet.immunity`; separately checked over 5,912 forest worlds /
116,032 rewirings and 252 DAG worlds / 1,992 rewirings, 0 violations.

**Enforcement (new in v3).** `provenance.EvidenceGraph.add` now rejects
cross-side and cross-proposition edges (`SideConsistencyError`,
`PropositionMismatchError`). Before v3 this hard requirement had **no check
anywhere in the codebase**. Pass `strict=False` to record violations in
`graph.violations` instead of raising; `graph.immunity_applicable` is then
`False` and no theorem applies.

**Two things v2 understated.**

1. **The failure mode is not graceful.** Outside R2 the aggregator does not
   degrade — it *double-counts*: in **44,450 / 44,450** non-side-consistent
   worlds tested at n≤6, some root lands in **both** `S_0` and `S_1`.
2. **In a DAG, R2 forbids synthesis.** A claim derived from evidence on both
   sides violates R2. v2 read R2 off a single-parent forest model, where such a
   claim cannot even be written down, which made R2 look like mild hygiene. It is
   not. See `formal/COUNTEREXAMPLES.md` CE-07 and
   `formal/EXTENSION-SOCKETS.md` §3 — **edge polarity** is the natural repair and
   is the recommended next design step.

**Measurement:** side-confusion (must be 0 for the immunity guarantee); library
diagnostic `immunity_applicable`.

---

### R3. MARGIN SUFFICIENCY (system-level requirement — the defender's lever)

**Guarantee:** maintain enough attested independent roots that the honest margin
exceeds the adversary's capacity.

**T4 (flip condition):** a verdict flips only if net phantom root flow reaches
the true side-count margin. Compiled as `T4_flip_requires_margin`.

> ### ⚠ State the unit. v2 did not, and was ~2× optimistic.
>
> Flow is measured as **`p₀ − p₁`, net per-side root gain** — equivalently, the
> drop in the signed margin. In that unit, the attack budget *is* the margin.
>
> It is **not** a count of adversary actions. One action that **converts** a root
> from the winning side to the losing side is worth **two** units: `−1` to one
> side and `+1` to the other. Measured in conversions, reversal costs
> `⌊margin/2⌋ + 1`, not `margin + 1`. At margin 8 that is **5 actions, not 9**.
>
> Confirmed on constructed worlds: conversion reversed the verdict at or below
> the margin in **4,638 / 4,638** decisive worlds
> (`verification/independent_check_2026-08.py`).

**T6 (parity, new):** with the root set fixed, conversions preserve the margin's
parity, so at **odd** margin a pure conversion attack cannot produce abstention —
it must overshoot into reversal. Compiled as `no_abstention_of_odd_margin`.
Planning that treats denial-of-decision as strictly cheaper than deception is
wrong at odd margins under this attack class.

**Consequence (H5 REJECTED, preregistered):** no margin-independent scalar
corruption statistic predicts failure; defense planning must be margin-relative.

**Measurement:** `flip_budget` (per-verdict `|margin|`, in `p₀ − p₁` units) and
`conversions_to_reverse` (in actions). Both are first-class outputs of
`aggregation.root_vote.verdict`. **Report both** — `flip_budget` alone
overstates the attacker's cost.

---

## Explicitly NOT required (demotions)

- **Accurate who-copied-whom edges.** (T1)
- **Full lineage trees / high attribution accuracy.** (Mode C: attribution
  1.0 → 0.59 with accuracy ≥ 0.98 throughout.) Holds **among non-roots**; a
  single root-set-disturbing edit flips verdicts 33.0% of the time pooled.
- **Copy-count knowledge** — for copies **whose parent edge is recorded**. (T2)
  An *undetected* copy is a root and is governed by R1/T5, not by T2. The
  unqualified form of this demotion is false; see `formal/PROOFS.md` §4.
- **Root-set OVERLAP as a quality metric** — demoted after EXP004 showed it blind
  to attribution damage; superseded by side-confusion and margin metrics.

---

## Field/metric registry

```
attribution accuracy       per-claim true-root match; diagnostic only
side_confusion             R2 gate
signed side_confusion      directional diagnostic; not sufficient (H5)
flip_budget / margin       R3 gate, in p0 - p1 units; verdict output
conversions_to_reverse     R3 gate, in adversary actions   (new in v3)
abstention_reachable       parity flag, T6                 (new in v3)
unattributed               claims with no recorded root    (new in v3)
immunity_applicable        R2 precondition check; verdict output
roots_per_identity_window  R1.4 gate                       (new in v3, unimplemented)
orphans_per_delete         R1.4 gate, must be 0            (new in v3, unimplemented)
edge_confidence, inferred  lineage schema extensions, backward compatible
```

---

## Known limits of the current definition

- **Root identity is undefined.** `S_a` is a set, so the verdict is a function of
  when two roots count as one — a criterion no artifact states. Any semantic
  de-duplication is **inside the trusted base**. Ledger `U1`.
- Binary assertions only; multi-proposition and continuous claims unformalized.
- "Independence" is modeled as **disjoint root sets** — all-or-nothing. Graded
  independence (partially correlated observers) is unrepresentable and untheorised.
- Weights are not in the core at all: `F` is a pure cardinality comparison. No
  theorem covers any weighted aggregator. Ledger `U3`.
- No time: expiry and revocation are outside every theorem.
- R1's cost mechanism is imported from the attestation layer and is outside these
  theorems' scope — the theorems quietly become vacuous if R1 or R1.4 fails.
- Canonical replication of EXP003–006 findings is recorded in
  `CANONICAL-RECORDS.md` and the replication protocol under `experiments/`.

---

**One-line summary:** provenance does not need to reconstruct the family tree; it
needs unforgeable origins (R1) with a bounded blast radius per identity (R1.4),
unblended camps (R2), and a protected lead measured in the right unit (R3) — in
that order, and nothing more.
