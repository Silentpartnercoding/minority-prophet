# EXTENSION-SOCKETS.md

Workstream E. Nothing here is implemented. Each socket states the minimum new
definition, what survives, what breaks, the new failure mode, and the experiment
or proof that would validate it.

**Design rule for all seven:** the kernel in `formal/lean/MinorityProphetCore/`
stays fixed. Extensions are *versioned adapters* that either (a) reduce to the
kernel, or (b) come with their own theorems and their own ledger entries. An
extension that requires editing `Defs.lean` is a kernel version bump
(`core-v4-…`), not an extension, and every downstream claim must be re-audited.

---

## 1. Multivalued propositions

**New definition required.** Replace `assert : Fin n → Bool` with
`assert : Fin n → V` for a finite alphabet `V` with `DecidableEq`. Redefine
`sideRoots W v` for `v : V`, and `F` as an argmax with abstention on any tie for
the maximum.

**Survives unchanged (modulo the alphabet swap):**
- Lemma 1 (side-locality) — the induction is on the lineage order, not on `Bool`.
- T1 (immunity) — `sideRoots_congr` never inspects the value.
- T2 (recorded-copy invariance) — likewise.
- The Gate's `verify_multivalue.py` already exercises this over a 3-letter
  alphabet (2,955 worlds, 0 violations), though not exhaustively (ledger F3).

**Requires generalization:**
- `card_sideRoots_add` becomes `Σ_v |S_v| = |rootSet|`, not a two-term sum.
- **T4 / T4' / T5 do not survive as stated.** `margin` is a *scalar difference
  between two* counts. With `|V| ≥ 3` the right object is the gap between the
  top count and the runner-up, and the flip condition becomes pairwise. Critically,
  the T6 **parity invariant is lost**: with three or more values, a conversion
  moves the top-vs-runner-up gap by 1 or 2 depending on whether the converted
  root leaves or joins the runner-up.

**New failure mode.** *Vote splitting.* An adversary who converts roots to a
**third** value rather than to the opposing value reduces the leader's margin at
cost 1 per root instead of 2, while never increasing any rival. Abstention
becomes reachable at odd gaps, which the binary parity theorem forbids. This is
strictly cheaper than the binary attack and has no analogue in the current model.

**Validation.** Prove the pairwise flip condition in Lean over `Fintype V`; then
a finite exhaustive check that the cheapest attack on a gap-`m` decision costs
`⌈m/2⌉` under conversion-to-runner-up and `m` under conversion-to-third-value.
Fix the Gate verifier's sampling first (F3), or its result cannot be cited.

---

## 2. Weighted evidence

**New definition required.** `weight : Fin n → W` for an ordered commutative
monoid `W` (`ℚ≥0` is the honest first choice; floats are not, because ties —
the abstention condition — are not decidable under rounding). Replace
`(sideRoots W a).card` with `Σ_{r ∈ sideRoots W a} weight r`.

**Survives unchanged:**
- Lemma 1, T1, T2 — all three are set equalities proved *before* any counting.
  Every one of them goes through verbatim, because `sideRoots_congr` establishes
  the sets are equal and any function of equal sets is equal.

**Requires generalization:**
- T4 / T4' / T5 all become weighted. The counting bound
  `margin_diff_le_rootSet_diff` generalizes to
  `|margin W − margin W'| ≤ Σ_{r ∈ rootSet W Δ rootSet W'} weight r`,
  i.e. *k errors* becomes *k weight-units of error*.
- **T6 (parity) is lost outright** — parity is an artefact of unit weights.

**New failure mode.** *Weight concentration.* Under unweighted counting an
attacker must corrupt `⌈m/2⌉` roots. Under weights they must corrupt the
*heaviest* roots, which may be one. Margin in weight-units and margin in
root-count are different security budgets, and the smaller one binds. Related:
zero-weight roots are counted at full strength by `F` and at zero by
`weighted_vote` today (DEFINITION-AUDIT.md §1.14) — the two must be reconciled
before any weighted theorem is stated.

**Validation.** The Lean generalization is mechanical (replace `Finset.card`
with `Finset.sum`); do it and check which proofs still close. Then an experiment
reporting *both* budgets per verdict, and the ratio `max-single-root-weight /
total-margin-weight` as a first-class output alongside `flip_budget`.

---

## 3. Causal-dependency hypergraphs (and edge polarity)

**New definition required.** Two separable changes, and they should not be
conflated:

1. **Polarity** (small, high value): `polarity : Edge → {supports, rebuts}`, and
   redefine side-consistency as *"a supporting edge preserves the assertion; a
   rebutting edge inverts it"*. This directly addresses CE-07 — the DAG's
   inability to represent a claim synthesised from conflicting evidence without
   violating R2.
2. **Hyperedges** (large): a parent *set* whose members are jointly, not
   severally, required — `parents : Fin n → Finset (Finset (Fin n))`, read as a
   disjunction of conjunctions.

**Survives unchanged under (1) polarity:** nothing automatically. Lemma 1's
statement must be rewritten (a root now determines its descendants' assertions
only up to the parity of rebutting edges along the path). The *induction shape*
survives: replace `W.assert j = W.assert i` with `W.assert j = xor p (W.assert i)`
and the strong induction `lineage_induction` carries through unchanged.

**Survives unchanged under (2) hyperedges:** T1 and T2, because both are about
the root *set*, and "parentless" is still well defined. T4/T4'/T5/T6 survive
because they are pure margin arithmetic downstream of Lemma 1.

**Requires generalization:** `rootsOf` under hyperedges is no longer a union —
it is a set of *alternative* root sets (one per satisfying conjunct), so
"independence" becomes a question about a family of sets rather than one set.
This is where `EvidenceGraph.independent` (currently `isdisjoint` on one set)
would need real design work.

**New failure mode.** *Polarity laundering.* An adversary who can flip one edge's
polarity converts a supporting citation into a rebutting one and thereby moves a
whole subtree's side without touching any assertion or any root. This is a
**third** unit of attack, distinct from root creation (1 unit) and root
conversion (2 units), and the corrected T5's `W.assert = W'.assert` hypothesis
would silently *fail to cover it* — the assert function is unchanged, but the
side-root sets move. Any polarity extension must re-derive T5 from scratch.

**Validation.** Formalize polarity first; it is cheap and it repairs a real
expressiveness gap. Prove or refute a polarity analogue of T5 before writing any
security doctrine. Hyperedges should wait.

---

## 4. Dynamic evidence, expiry and revocation

**New definition required.** Re-introduce the `τ` that `FOUNDATIONS.md`'s
abstract aggregator already has and the formalized `F` does not: make a world a
function of evaluation time, `W : Time → World n`, with each claim carrying a
validity interval and each root a revocation status.

**Survives unchanged:** every theorem, *pointwise in time*. `F(W(τ))` is the
compiled `F` applied to one world. Nothing breaks as long as no claim is made
*across* time points.

**Requires generalization:** every claim about *stability*. T5 currently bounds
the verdict's response to `k` units of root-set change; under expiry, the root
set changes on its own, with no adversary and no error. "Margin > k implies the
verdict survives k errors" becomes "margin > (k + expected natural root
attrition over the horizon)". `FOUNDATIONS.md` desideratum 6 (Revision) and
desideratum 3 (Evidence monotonicity) are in direct tension here and the
document already says so.

**New failure mode.** *Timing attacks on the abstention band.* An adversary who
knows expiry schedules can wait rather than act: schedule an attestation to lapse
so the margin crosses zero unaided. Under T6's parity result the binary system
cannot be pushed from odd margin to abstention by conversion — but attrition
changes the root set, so parity is not preserved and the abstention band becomes
reachable for free. Revocation also makes the system's history non-monotone,
which breaks any audit that assumes append-only.

**Validation.** Prove `F(W(τ))` stability under a bounded attrition rate; then a
replay experiment over the existing canonical records with synthetic expiry, to
measure how often verdicts cross the abstention band with no adversary at all.
Fix the clean-clone reproducibility defect (ledger F4) first, or the replay
cannot be independently checked.

---

## 5. Semantic proposition identity

**New definition required.** A quotient: `≈` on propositions, and separately `≈`
on roots (ledger U1). The kernel then operates on equivalence classes.

**Survives unchanged:** every theorem, *given the quotient*. All of them are
already stated over an abstract index type; nothing inspects what an index means.

**Requires generalization:** none of the theorems. What changes is the **trust
boundary**, and that is the entire point. Today `proposition_id` is never
compared across an edge (CE-10) and root identity is an opaque caller-supplied
string (CE-08). Introducing `≈` does not add a theorem — it *names* a component
that is already silently load-bearing.

**New failure mode.** *Adversarial paraphrase, in both directions.* Splitting:
an attacker states one observation in `k` paraphrases and, if the quotient is too
fine, gains `k` roots for one observation — exactly the sybil-root attack R1 is
meant to exclude, but committed at the semantic layer where R1's cryptography
does not reach. Merging: if the quotient is too coarse, an attacker collapses `k`
genuinely independent roots into one and destroys the defender's margin (CE-08 is
the two-root instance). **Both directions are one-action, unbounded-effect
attacks**, which puts the identity function in the same risk class as the
root-signing key.

**Validation.** This is the highest-leverage socket and the one most likely to be
mis-sold. Required before any claim: (i) state `≈` explicitly; (ii) measure
split-rate and merge-rate against a human-labelled gold set; (iii) report both as
first-class outputs next to `flip_budget`. A theorem is not what is missing here —
a measurement is.

---

## 6. Active information gathering

**New definition required.** A policy `π` mapping a world to a query, plus a cost
model. This turns a static aggregator into a sequential decision problem.

**Survives unchanged:** every theorem, at each step. `F` is still `F`.

**Requires generalization:** nothing in the kernel — but note that this is where
**Gate PR #1's separation of action-neutral evidence assessment from action
policy becomes load-bearing**, and that separation must be preserved. The moment
a query policy is allowed to depend on the current verdict, the evidence
assessment stops being action-neutral.

**New failure mode.** *Endogenous evidence / feedback loops.* If queries are
chosen to confirm the leading side, the root set becomes a function of past
verdicts and "independent evidence roots" are no longer independent of the
aggregator. `FOUNDATIONS.md` already flags this for competence estimates; it
applies with more force here. No theorem in the kernel detects it, because the
kernel sees only the graph it is handed.

**Validation.** A preregistered experiment comparing a verdict-blind query policy
against a verdict-aware one on identical worlds, reporting margin trajectories.
The hypothesis to test is that verdict-aware querying inflates margin without
improving accuracy — i.e. it manufactures apparent confidence.

---

## 7. Evidence-aware memory

**New definition required.** A retention function deciding which claims persist,
plus a summarization operator mapping a set of claims to a smaller set.

**Survives unchanged:** T1 and T2, *if and only if* the retention function is
root-preserving. That is exactly T1's hypothesis, so the socket has a clean
statement: **any memory policy that preserves the root set and the assertions is
verdict-neutral by T1, regardless of which non-root claims it discards.** This is
a genuinely useful and immediate consequence of the compiled T1.

**Requires generalization:** none, given the above.

**New failure mode.** *Compaction as unintentional deletion.* Discarding a
non-root claim that has children orphans them — this is CE-04, arriving as a
routine memory operation rather than as an ops error. A summarizer that merges
claims also merges root sets, which is CE-08 arriving as a routine memory
operation. Both of the audit's unbounded-effect witnesses are reachable by an
ordinary garbage-collection pass.

**Validation.** Cheapest and most valuable item on this list: state the
root-preservation invariant as a property test over the memory policy, reusing
`audit/test_counterexamples.py` fixtures directly. If the policy is
root-preserving, T1 already gives the guarantee — no new proof needed.

---

## Recommended order

1. **§7 evidence-aware memory** — the guarantee already exists; only the
   invariant test is missing.
2. **§3(1) edge polarity** — repairs a real expressiveness gap (CE-07), cheap
   to formalize, and the induction shape carries over.
3. **§5 semantic identity** — highest risk, currently silently trusted; needs
   measurement before claims.
4. **§2 weighted evidence** — mechanical Lean generalization, but retire the
   parity result and reconcile the two weight conventions first.
5. **§1 multivalued** — needs a new flip condition; the Gate verifier's sampling
   caveat must be fixed first.
6. **§4 dynamic evidence** — blocked on reproducibility (ledger F4).
7. **§6 active gathering** — blocked on §4, and on preserving the Gate PR #1
   action/evidence separation.
