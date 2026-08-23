# CLAIM-SCOPE.md

What the formal core establishes, and what it does not. This file exists so that
a later reader — human or agent — cannot confuse the six evidence classes.

Authoritative statements and their statuses live in `THEOREM-LEDGER.json`.
This file is the prose gate.

---

## The six evidence classes, and which artifacts belong to each

| Class | What it means | Where it lives in this audit |
|---|---|---|
| **Mathematical theorem** | Compiled by Lean 4.32.2 against pinned Mathlib `905b958`, zero `sorry`, no axioms beyond `propext`/`Classical.choice`/`Quot.sound` | `formal/lean/MinorityProphetCore/` — 8 ledger entries |
| **Finite exhaustive check** | Every case in a bounded domain enumerated. Says nothing about larger domains | `audit/falsify.py`, `verification/independent_check_2026-08.py` (partly — see F2) |
| **Randomized experiment** | Sampled, not enumerated. Reports a rate, not a guarantee | `verification/r1_degradation_curve.py`; the Gate's `verify_multivalue` above 200 rewirings (F3) |
| **Implementation invariant** | A property of shipped code, true until someone edits the code | `audit/test_counterexamples.py` CE-09…CE-12 |
| **Security assumption** | Imported from a layer these theorems do not model. If it fails, the theorems become vacuous | R1 (root integrity), root identity (U1), acyclicity enforcement |
| **Speculative extension** | Not implemented, not proved | `EXTENSION-SOCKETS.md`, ledger `LEDGER-H1`/`LEDGER-H2` |

A statement never changes class by being repeated. In particular: **a Lean file
that does not compile is not a proof**, and `formal/MinorityProphetV2.lean` does
not compile (ledger F1 — it calls `Fin.strongRecOn`, which does not exist in
Mathlib).

---

## What the core DOES establish

All of the following are compiled proofs about the specified aggregator on
finite, acyclic, side-consistent worlds.

1. **Under side-consistency, `S_a` is exactly the set of `a`-asserting
   parentless claims** (`side_locality`). This is the bridge; everything else is
   counting on top of it.

2. **Lineage may be arbitrarily wrong without moving any verdict**, provided no
   edge crosses sides, no root is created or destroyed, and no assertion changes
   (`immunity`). Attribution accuracy among non-roots is genuinely, provably
   irrelevant. This is the core's strongest and most useful result.

3. **Copies whose parent edge is recorded are free** (`copy_invariance`). Ten
   thousand recorded copies of one root count once. Newly compiled by this audit;
   the repository had left it as future work.

4. **Majority voting does not have property 3** (`majority_not_copy_invariant`).

5. **A verdict flips only if the net per-side root flow reaches the margin**
   (`T4_flip_requires_margin`), flow of exactly the margin gives abstention
   (`T4'_flow_eq_margin_abstains`), and reversal needs margin + 1
   (`T4'_reversal_needs_margin_succ`) — **all measured in units of `p₀ − p₁`**.

6. **With assertions fixed, `k` units of root-set change cannot move a verdict of
   margin > k** (`root_error_tolerance`), and cannot reverse one of margin ≥ k
   (`no_reversal_of_margin_ge`). The compiled form is more general than the
   repository's: it bounds the margin by the root-set symmetric difference, so
   one theorem covers arbitrary simultaneous combinations of edge changes, claim
   insertions and claim deletions.

7. **Pure conversion attacks preserve the margin's parity**
   (`margin_parity_of_rootSet_eq`), so an odd margin cannot be driven to
   abstention by conversion alone (`no_abstention_of_odd_margin`). New in this
   audit.

8. **Three necessity results**, also compiled: unrecorded copies flip verdicts
   (`CE01_…`), the equal-assertions hypothesis cannot be dropped
   (`T5_needs_assert_fixed`), and without side-consistency one root serves both
   sides (`CE06_…`).

---

## What the core DOES NOT establish

### It does not discover truth

`F` compares two integers. It has no access to ground truth, no model of
observation reliability, and no calibration. `FOUNDATIONS.md` already states the
identifiability limit — two worlds can produce the same vote vector with opposite
ground truth — and nothing in this audit changes that. **The theorems are about
an aggregator's invariances, not about accuracy.**

### It does not establish independence

"Independent" is *defined* as "distinct root", and root identity is
**undefined** (ledger U1). Graded or partial independence is not representable
in the model that was formalized before this audit, and is representable but
untheorised in the DAG kernel. Any claim that the system measures genuine
evidential independence is a claim about the identity criterion, which is
currently an opaque caller-supplied string.

The adapter in `provenance/decision_relative.py` does not close this gap. It
requires a caller to name the decision, failure domain and lineage cut, then
reports whether alternative declared cuts materially change settlement. That
makes root-identity policy visible and testable; it neither proves that the
selected cut is causally correct nor extends a theorem. Its constructed fixtures
are implementation invariants, not empirical evidence.

### It does not survive its own headline slogan

**"Adding copied claims cannot change the verdict" is FALSE.** The proved
statement is about copies *whose parent edge is recorded*. An undetected copy is
a parentless claim — a root — and reverses verdicts (CE-01). Since undetected
copying is the threat the project exists to address, this sentence must never be
used without its hypothesis.

### It does not confer operational immunity to incidents

**"min_flip_budget ≥ 2 confers proved immunity to any single key compromise or
ops error" is FALSE** (CE-04, CE-05). The theorem counts *units of root-set
change*. One deleted claim record orphans all of its children at once; one
compromised signing key mints unboundedly many roots. Converting the proved
budget into an incident budget requires a bound on units-per-incident that does
now has a tested reference implementation but remains a deployment requirement
(ledger `LEDGER-H2`).

### The attacker's budget is not the margin, in actions

Measured in root **conversions**, reversal costs `⌊margin/2⌋ + 1`, roughly half
what "the attack budget IS the margin" implies (CE-03). At margin 8: 5 actions,
not 9. The margin *is* the budget in units of `p₀ − p₁`; the two readings of
"flow" differ by a factor of two and the repository uses both.

### Side-consistency is not a mild hygiene condition

It is the single hypothesis the entire stack consumes; it has **no enforcement
point in the implementation** (CE-09); its failure mode is double-counting, not
graceful degradation (CE-06, 100% of non-side-consistent worlds tested); and in
the DAG the implementation actually uses, it **forbids any claim synthesised from
evidence on both sides** (CE-07). Its apparent mildness is an artefact of having
been read off a single-parent forest model.

### Weights, time, multiple values and multiple propositions are not covered

`F` is an unweighted cardinality comparison on a static, single-proposition,
binary world. `weighted_vote`, `semantic_coalition`, `evidence_root_vote`,
proposition IDs, timestamps, confidence, competence, calibration and markets are
all outside the kernel (ledger U3, EXTENSION-SOCKETS.md).

### `evidence_root_vote` is not the aggregator the theorems describe

It takes one `root_id` per claim rather than a root *set*, silently drops claims
with `root_id is None` (CE-12), and resolves duplicate root IDs first-writer-wins,
which makes it **order-dependent** exactly in the side-consistency-violating case
(CE-11). It coincides with `F` only for single-proposition worlds with total,
conflict-free root attribution.

### Simulation is not proof, and finite enumeration is not universality

`r1_degradation_curve.py` is a randomized experiment. `falsify.py` and
`independent_check_2026-08.py` are exhaustive only over the stated bounds
(n ≤ 6 forest, n ≤ 4 DAG). Neither establishes a universally quantified
statement. The Lean proofs do, for all `n`.

### One published finite check does not check what it claims

`check_t4_tightness` never constructs a perturbed world; it applies closed-form
arithmetic to each world's margin. Its "4,638/4,638" cannot fail for any input
(ledger F2). T4' now has a compiled proof instead.

### The empirical evidence is not currently reproducible from a clean clone

38/40 tests pass from `git clone`; the two canonical-record tests require
gitignored artifacts (ledger F4, CE-13). Not fixed here — it is the owner's call
whether to commit the manifests or change the tests.

---

## The one-sentence version

*Given side-consistent lineage, unforgeable root identity, and assertions that do
not change underneath you, the aggregator's verdict is provably insensitive to
everything about who-copied-whom except the identity and count of the parentless
claims on each side — and every one of those three preconditions is an assumption
imported from outside the mathematics, not a result of it.*
