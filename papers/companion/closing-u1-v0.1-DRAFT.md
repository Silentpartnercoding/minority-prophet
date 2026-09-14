# Closing U1: Root Identity by Proximate Cause

**Status: DRAFT v0.1. Not submitted. Not deposited. No DOI.**
Drafted 2026-09-14. Recorded in `papers/ERRATA.md` under `[E9]` and in the
publication sequence at `papers/README.md`.

This is the companion to *The Minority Prophet Property: Copy-Invariant Evidence
Aggregation in Rooted Claim Graphs* (archival record, all versions:
`10.5281/zenodo.21965712`; v1.2.0: `10.5281/zenodo.21997434`). That paper is
correct as deposited and is not revised by this one. It is a **new version or a
new record**, not an edit, because others may already cite it.

---

## Abstract

The foundation paper states in four places that root identity is primitive,
unresolved, and not solved: the model treats root equality as given. This paper
closes it, and closes a second gap the foundation paper did not identify — that
every invariance theorem in its core is satisfied by an aggregator that always
abstains.

Both closures are Lean-checked, with no `sorry` and standard axioms only:
`formal/lean/MinorityProphetCore/RootIdentity.lean` (5 results) and
`Responsiveness.lean` (4 results).

The first result is negative and is the reason the problem stood open. **The
error was demanding an equivalence relation at all.**

---

## 1. Why every previous attempt failed

Ancestry is transitive and unbounded. Every claim descends from earlier claims
without end, so any relation of the form *shares an ancestor* has a transitive
closure that swallows the corpus. Force it to be an equivalence relation and the
effective witness count tends to one: the aggregator refuses to believe anything,
which is the `FalseDenyRate` failure rather than a solution.

The alternative usually proposed is clustering. That trades the problem for a
different one: the count then depends on a clustering algorithm rather than on
evidence, and must be pinned and published before it means anything.

Neither horn is taken here.

## 2. The move: a declared cut, not a relation

Criminal and tort law met the identical problem and did not solve it by tracing
harder. Cause-in-fact is unbounded and transitive; every event has infinite
ancestry. **Proximate cause is a declared cut** — beyond a certain remoteness the
chain no longer carries liability, not because causation stopped but because
responsibility did. The mechanism is `novus actus interveniens`: an intervening
independent act breaks the chain.

Applied to evidence: shared ancestry between two sources is **cut by an
intervening independent re-derivation**. Two sources descending from a common
ancestor remain independent witnesses if each re-established the claim through a
channel that does not pass through that ancestor.

Dependence is therefore a **graph relation relative to a proposition**, not an
equivalence, and the count is **not a quotient**.

Re-derivation is graded rather than boolean. `canon/proximity.py` ranks how far
back toward the world a witness actually went — from an independent measurement,
through a re-measurement by a different method, down to a restatement of the text
— and independence is evaluated **relative to a named class of error**. Two
analysts working from one published table are fully independent for arithmetic
slips and not independent at all for a miscalibrated instrument. The module
exposes `independent_for(a, b, error)` and no aggregate, because a single number
would hide exactly that distinction.

## 3. Results — root identity

**Soundness.** `independent_card_le_lineages`: any set of pairwise-independent
witnesses contains at most one member per true lineage, so counting a maximum
independent set can never **over-report** independence relative to the detected
dependence graph. The direction matters: the theorem bounds the error on the side
that would otherwise manufacture confidence.

**The witness that broke the old definition now gives the right answer.**
`path_indep_two`: for `A — B — C` with `A` and `C` unrelated, transitive closure
reports one independent witness; the independent-set count reports two.

**It generalises rather than replaces.** `clique_indep_one`: where dependence
genuinely is transitive, the count still collapses to one. The quotient
definition is recovered as a special case rather than discarded.

## 4. Results — responsiveness

The attractor requirement is two-sided. An irrelevant presentation change must
leave the answer invariant, **and a material change must move it.** The
foundation paper proves only the first half: `immunity`, `copy_invariance` and
`margin_parity_of_rootSet_eq` are all invariance statements, and
`margin_diff_le_rootSet_diff` is an upper bound. The only statement of the form
`F W ≠ F W'` anywhere is an *existence* claim — there exist two worlds that
differ — not a guarantee that a material change registers.

**Consequently an aggregator that always abstains satisfies every invariance
theorem in the core.** It is perfectly immune to lineage corruption, perfectly
copy-invariant, perfectly parity-preserving, and perfectly useless. Nothing
proved before this file excludes it.

The repair is available in the existing algebra rather than requiring new
machinery. `margin_diff_le_rootSet_diff` discards information by taking an
absolute value and weakening to `≤`. The underlying fact is an **equality**, and
an equality constrains from both sides at once: it forbids the margin moving too
much, which is invariance, and forbids it moving too little, which is
responsiveness. `margin_eq_signedCount`, `margin_diff_eq_signedCount`,
`margin_must_move` and `margin_shifts_by_added_roots` state it.

## 5. What is not claimed

**The residual is detection, not definition.** An adversary who launders the
provenance record *and* scrubs the shared idiosyncratic markers removes edges
from the graph, and a sparser graph admits a *larger* independent set, so the
count over-reports relative to reality. This is pinned deliberately as
`test_ATTACK_laundered_provenance_inflates_the_count`, which asserts that three
copies with erased ancestry are counted as three.

No counting rule closes this; only detection does. It is **bounded rather than
solved**, by R3 margin sufficiency: require a margin *above* the effective
witness count rather than trusting the count itself. U1 and R3 were always the
same problem seen from two ends.

Per `ASSAYER.md` A5, a report may only ever state *"no dependence trace was
found"* — never *"these are independent."*

The framework can **represent** a shared blind spot and **count** under one. It
cannot **discover** one. Naming the error class is an owner judgment published in
advance under `A3`, before any sample is drawn, as is the assignment of
particular real procedures to proximity rungs.

**The foundation paper's warning stands unchanged:** *root*, *independent
evidence* and *truth* are not interchangeable terms.

## 6. Scope

Deliberately excluded. `Asymmetric.lean` — claims whose falsifier is singular,
where comparing root counts is the wrong instrument entirely — is the subject of
*When Counting Is the Wrong Instrument*, drafted alongside this one.
`NarrowGate.lean` remains unwritten up.

## Availability

`formal/lean/MinorityProphetCore/RootIdentity.lean`,
`formal/lean/MinorityProphetCore/Responsiveness.lean`,
`canon/U1-PROXIMATE-ROOTS.md`, `canon/proximity.py`.
Prose narration of the counterexamples: `formal/COUNTEREXAMPLES.md`.
Rebuilt on Lean v4.33.1; `#print axioms` read; no `sorry`.
