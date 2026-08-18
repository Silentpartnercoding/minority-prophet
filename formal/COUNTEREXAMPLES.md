# COUNTEREXAMPLES.md

Workstream C. Every witness below is reproducible by
`python3 audit/falsify.py` and pinned by a regression test in
`audit/test_counterexamples.py`. CE-01, CE-02 and CE-06 are additionally
**machine-checked in Lean** (`formal/lean/MinorityProphetCore/Counterexamples.lean`),
as is CE-14 and its mirror
(`formal/lean/MinorityProphetCore/Asymmetric.lean`, ledger AC4/AC5).

## Fix status as of 2026-08-17

| ID | Status | Where the repair landed |
|---|---|---|
| CE-01 | **documented** | `formal/PROOFS.md` §4, `papers/ERRATA.md` [E1]; detection remains R1's job |
| CE-02 | **fixed in the mathematics** | hypothesis added to T5, proved necessary (`T5_needs_assert_fixed`) |
| CE-03 | **fixed in the mathematics** | unit stated; circular check rewritten to construct worlds |
| CE-04 | **requirement added** | R1.4 (no hard delete) — not yet enforced in code |
| CE-05 | **requirement added** | R1.4 (roots-per-identity bound) — not yet enforced in code |
| CE-06 | **enforced** | `EvidenceGraph.add` raises `SideConsistencyError` |
| CE-07 | **open by design** | scope limit; edge polarity proposed, `formal/EXTENSION-SOCKETS.md` §3 |
| CE-08 | **open** | root identity still undefined; now named as trusted-base, ledger `U1` |
| CE-09 | **fixed** | `EvidenceGraph.add` raises; `strict=False` records instead |
| CE-10 | **fixed** | `EvidenceGraph.add` raises `PropositionMismatchError` |
| CE-11 | **fixed in new module; legacy retained** | `aggregation.root_vote.verdict` is order-independent and fails closed. `semantic.evidence_root_vote` is unchanged — its sha256 is bound by a canonical manifest |
| CE-12 | **fixed in new module; legacy retained** | explicit `unattributed_policy`, defaulting to fail-closed |
| CE-13 | **fixed** | canonical manifests are now tracked; clean clone passes 40/40 |
| CE-14 | **fixed in a new function; `verdict` fenced** | `asymmetric_verdict` implements the compiled rule (AC1–AC5); `verdict(..., claim_shape=)` refuses these shapes. The ledger's `presence` branch is an open semantic question, not a pending fix |

Two witnesses (CE-09, CE-10) no longer reproduce: `audit/falsify.py` now emits
**10** witnesses rather than 12, and `audit/test_counterexamples.py` pins the
repaired behaviour instead. The descriptions below are retained unchanged as the
record of what was wrong.

---

## How to read the `kind` field

- **`refutes_theorem`** — a statement as written in the repository is FALSE.
  A single witness settles it.
- **`refutes_doctrine`** — the theorem is true but the security sentence
  attached to it does not follow, because the theorem's unit of "error" is not
  the real world's unit of error.
- **`violates_assumption`** — the theorem is true and correctly hypothesised;
  the witness shows how load-bearing the hypothesis is, or that nothing
  enforces it.

Nothing here refutes T1, Lemma 1 or the proved form of T2.

---

## CE-01 — "Adding copied claims cannot change the verdict" is false
**kind:** `refutes_theorem` · **target:** T2, plain-English form (as restated in
the assignment brief) · **Lean:** `CE01_unrecorded_copies_flip_the_verdict`

```
before:  parent = [-1,-1,-1]            assert = [1,1,0]
         S1 = {0,1}  S0 = {2}           verdict = 1   margin = 1

two copies of claim 2, provenance RECORDED (the proved T2):
         parent = [-1,-1,-1, 2, 2]      assert = [1,1,0,0,0]
         verdict = 1                    unchanged ✓

the same two copies, provenance NOT recorded:
         parent = [-1,-1,-1,-1,-1]      assert = [1,1,0,0,0]
         S1 = {0,1}  S0 = {2,3,4}       verdict = 0   REVERSED ✗
```

**Violates a theorem or an assumption?** A theorem — but only the informal
restatement. `PROOFS.md`'s own T2 says "adding a duplicate claim `d` with
`parent(d) = c`", which is correct and is now compiled as `copy_invariance`.

**Why it matters more than a wording nit.** The system exists to be robust to
copying. It is robust to copying *that has been detected and recorded*. An
undetected copy is indistinguishable from an independent observation and is
governed by T5, not T2. The theorem is about the aggregator's treatment of
*known* lineage; the threat is about *unknown* lineage. These are opposite ends
of the pipeline.

**Where the repair belongs:** input validation and attestation (R1). Not
mathematics — the mathematics is already correct.

---

## CE-02 — One side conversion changes a margin-2 verdict
**kind:** `refutes_theorem` · **target:** T5's corollary, "k root-integrity
errors, ACCIDENTAL OR ADVERSARIAL, cannot change a verdict with margin > k" ·
**Lean:** `CE02_conversion_moves_margin_by_two`, `T5_needs_assert_fixed`

```
base:     parent = [-1,-1,-1,-1]   assert = [1,1,1,0]
          S1 = {0,1,2}  S0 = {3}   verdict = 1   margin = 2

one action: root 0 is converted to the other side
          assert = [0,1,1,0]
          S1 = {1,2}   S0 = {0,3}  verdict = ABSTAIN     ← changed, with k=1 < 2
          p₀ = +1, p₁ = −1  ⇒  p₀ − p₁ = 2
```

The root set is **identical** in both worlds — zero roots created, zero
destroyed. The conversion is side-consistency-preserving (in general: convert
the root together with its descendant subtree; here it has none).

**Violates a theorem or an assumption?** The corollary as stated is false. The
underlying edge lemma ("one side-consistent edge edit that disturbs the root set
changes exactly one side's count by exactly 1") is **true**, and was verified
exhaustively here in both the forest and the DAG (1,072 DAG single-edge edits,
maximum total root-count movement = 1).

**Exact changed assumption.** T5 must additionally require that **assertions do
not change**. The strongest correct replacement is compiled as:

```
root_error_tolerance :
  SideConsistent W → SideConsistent W' →
  W.assert = W'.assert →                               ← THE MISSING HYPOTHESIS
  #(rootSet W \ rootSet W') + #(rootSet W' \ rootSet W) ≤ k →
  (k : ℤ) < |margin W| →
  F W' = F W
```

This is strictly more general than the repository's T5 in every other respect:
it says nothing about "edits", so it covers any combination of edge changes,
claim insertions and claim deletions in one step.

`T5_needs_assert_fixed` proves the hypothesis cannot be dropped.

**Where the repair belongs:** mathematics (state the hypothesis) **and**
security doctrine (price a conversion at 2 units, not 1).

---

## CE-03 — Reversal costs ⌊margin/2⌋+1 conversions, not margin+1
**kind:** `refutes_theorem` · **target:** T4' ("flow of exactly the margin
forces ABSTENTION; reversal requires margin+1") and R3 ("the attack budget IS
the margin")

```
base:  assert = [1,1,1,0]  margin = 2  verdict = 1
two conversions: assert = [0,0,1,0]  S1 = {2}  S0 = {0,1,3}  verdict = 0
```

Doctrine predicts reversal needs `margin + 1 = 3`. Two actions suffice.

Budget scan (`conversion_budget_scan`, and `test_conversion_budget_*`):

| margin | conversions to abstain | conversions to reverse | doctrine says reverse at |
|---|---|---|---|
| 1 | unreachable (parity) | 1 | 2 |
| 2 | 1 | 2 | 3 |
| 3 | unreachable (parity) | 2 | 4 |
| 4 | 2 | 3 | 5 |
| 6 | 3 | 4 | 7 |
| 8 | 4 | 5 | 9 |

**Violates a theorem or an assumption?** T4' is *true under Meaning A of "flow"*
(net per-side gain, `p₀ − p₁`) and *false under Meaning B* (number of roots
crossing sides) — which is the reading its own name, "net **cross-side** phantom
root flow", invites. See DEFINITION-AUDIT.md §1.9. Both the corrected
statements are compiled: `T4'_flow_eq_margin_abstains`,
`T4'_reversal_needs_margin_succ`.

**Two further findings in the same place.**

1. **The repository's own check for T4' is arithmetically circular.**
   `verification/independent_check_2026-08.py::check_t4_tightness` enumerates
   worlds only to read off `d` and `m`, then computes
   `d_after = d − flow` in closed form and reports the verdict of `d_after`.
   It never constructs a second world. "4,638/4,638 decisive worlds" therefore
   cannot fail for any input; it restates the definition rather than testing it.
   It is not evidence for T4'; the compiled proof is.

2. **A parity invariant nobody noticed** (new, proved:
   `margin_parity_of_rootSet_eq`, `no_abstention_of_odd_margin`). Conversions
   move the margin by exactly 2, so with the root set fixed the margin's parity
   is invariant. At **odd** margin a pure conversion attack can never produce
   abstention — it must overshoot into full reversal. The doctrine "denial costs
   the margin; deception costs margin+1" presumes the two are separated by one
   unit; at odd margins under conversion they are not separated at all.

**Where the repair belongs:** mathematics (fix the unit) and doctrine.

---

## CE-04 — One deleted record orphans a whole subtree
**kind:** `refutes_doctrine` · **target:** "min_flip_budget >= 2 confers proved
immunity to any single key compromise or ops error"

```
before:  claim 0 is a root asserting 0, with 5 recorded copies hanging off it;
         4 independent roots assert 1.
         parent = [-1,0,0,0,0,0,-1,-1,-1,-1]   assert = [0,0,0,0,0,0,1,1,1,1]
         S1 = 4  S0 = 1   verdict = 1   margin = 3

one ops error: claim 0's record is lost. Its 5 children are orphaned.
         S1 = 4  S0 = 5   verdict = 0   REVERSED
```

**Violates a theorem or an assumption?** Neither — it refutes the *doctrine*.
T5's lemma is about a single **edge** edit. Deleting one **node** is one ops
error and, simultaneously, as many root-set changes as the node had children.
The map from "real-world error" to "unit of the theorem" is not a bijection, and
the doctrine sentence assumes it is.

Note this is fully covered by the corrected T5 (`root_error_tolerance`): the
root-set symmetric difference here is 5, and `margin = 3 < 5`, so the corrected
theorem correctly declines to protect this case. The old wording did not.

**Where the repair belongs:** trusted infrastructure (append-only storage, no
hard delete, tombstones that preserve edges) — and doctrine (state the budget in
root-set units, then bound how many units one operational failure can produce).

---

## CE-05 — One compromised root-signing key mints unbounded roots
**kind:** `refutes_doctrine` · **target:** immunity to "any single key compromise"

```
before:  3 roots assert 1.   verdict = 1   margin = 3
one key compromise mints 4 roots asserting 0:
         verdict = 0   REVERSED
```

**Violates a theorem or an assumption?** The doctrine. R1 (root integrity) is
declared to be the attestation layer's job, and `PROVENANCE-REQUIREMENTS.md`
correctly notes the theorems "quietly become vacuous if R1 fails". The doctrine
sentence attached to T5 does not carry that caveat.

**Where the repair belongs:** trusted infrastructure. Specifically, R1 needs a
sub-requirement it does not currently have: **a bound on roots per attested
identity per unit time**. Without it, "margin" is not a budget an attacker must
pay — it is a number an attacker with one key can exceed at will.

---

## CE-06 — Without side-consistency, one root serves both sides
**kind:** `violates_assumption` · **target:** Lemma 1 and everything downstream ·
**Lean:** `CE06_root_supports_both_sides`

```
smallest witness:  parent = [-1, 0]   assert = [0, 1]
                   S1 = {0}   S0 = {0}      ← the same root, on both sides
```

Frequency: **3,410 / 3,410** non-side-consistent worlds at n ≤ 5 (this audit);
**44,450 / 44,450** at n ≤ 6 (the repository's own check). Not "some" — all.

**Violates a theorem or an assumption?** An assumption, explicitly hypothesised.
The finding is that the aggregator does **not degrade gracefully** outside R2:
it double-counts, so `|S_1| + |S_0|` can exceed the number of roots and the
"independent evidence count" stops counting independent evidence.

**Where the repair belongs:** input validation. R2 must fail closed, not
silently.

---

## CE-07 — Side-consistency forbids synthesis (DAG only)
**kind:** `violates_assumption` · **target:** R2 as *described* ("camps must not
blend")

```
claim 2 asserts 1, derived from claim 0 (asserts 1) AND claim 1 (asserts 0)
   parents = [∅, ∅, {0,1}]   assert = [1, 0, 1]
   side_consistent = False
   if admitted:  S1 = {0,1}  S0 = {1}   ← root 1 on both sides
```

**Why this is not visible in the repository.** In a single-parent forest, a
claim that weighs evidence from both sides **cannot be written down**. R2 was
read off the forest model, where it looks like a mild hygiene condition. In the
DAG that `provenance/graph.py` actually implements, R2 excludes the ordinary act
of forming a conclusion from conflicting evidence.

**Violates a theorem or an assumption?** Neither — it is a **scope limit on
applicability**. Every theorem remains true. What changes is the honest answer
to "how often will R2 hold in practice?"

**Where the repair belongs:** definitions (see EXTENSION-SOCKETS.md §3 — an
edge-polarity extension that distinguishes *supports* from *rebuts* is the
natural generalisation).

---

## CE-08 — Root identity is an unstated parameter of every theorem
**kind:** `violates_assumption` · **target:** all counting theorems

```
three observations, assertions [1,1,0]
  distinct IDs  [r1,r2,r3] → |S1|=2 |S0|=1 → verdict 1
  merged  IDs   [r1,r1,r3] → |S1|=1 |S0|=1 → ABSTAIN
```

One identity decision, one verdict change. Because `S_a` is a **set**, the
verdict is a function of the identity criterion — and no artifact in the
repository defines that criterion. Lean makes it the index (assuming the
question away); Python makes it an opaque caller-supplied string.

**Where the repair belongs:** definitions (name the criterion) **and** the
trust boundary (any canonicalisation or semantic de-duplication step is inside
the trusted base, and must be declared as such).

---

## CE-09 — `EvidenceGraph.add` accepts a cross-side edge
**kind:** `violates_assumption` · **target:** R2, a declared *hard requirement*

```python
g.add(node("r", value=True))
g.add(node("c", value=False, copied_from=("r",)))   # accepted today
g.roots("c") == frozenset({"r"})
```

The single hypothesis every theorem rests on has **no enforcement point** in the
implementation. **Repair: input validation** — reject, or explicitly quarantine
and mark, an edge whose endpoints disagree.

---

## CE-10 — Edges may cross propositions
**kind:** `violates_assumption` · **target:** single-proposition worlds

A claim about proposition `p` may record as its parent a claim about proposition
`DIFFERENT`. Every theorem is stated for one proposition; the graph is global.
Subject substitution is unconstrained at the data layer. **Repair: input
validation.**

---

## CE-11 — `evidence_root_vote` is order-dependent
**kind:** `violates_assumption` · **target:** implementation determinism

```
claims: (root "R", asserts True), (root "R", asserts False), (root "B", asserts False)
  forward order → assignment None
  reversed order → assignment (False,)
```

`roots.setdefault(root_id, claim)` makes the first writer win. The situation in
which this triggers — one root ID carrying two different assignments — is
exactly an R2 violation, so the aggregator resolves a violated hard requirement
**silently and non-deterministically** instead of failing closed.

**Repair: implementation.** Detect the conflict; raise or abstain.

---

## CE-12 — Claims with no root are dropped, not abstained on
**kind:** `violates_assumption` · **target:** `FOUNDATIONS.md` desideratum 5

`evidence_root_vote` discards every claim with `root_id is None`. Two
unattributable claims yield `roots_used = 0` and `assignment = None` — the right
answer by accident, via an empty-input path, not via an abstention rule.

Combined with CE-01 this is the whole undetected-copy threat, and the two halves
of the codebase **disagree about what "no provenance" means**: `PROOFS.md`
promotes it to a root (maximum influence), `evidence_root_vote` deletes it (zero
influence). Neither abstains.

**Repair: implementation** — and a definition decision about which of the two
readings is intended.

---

## CE-13 — The canonical repository cannot pass its own test suite from a clean clone
**kind:** `violates_assumption` · **target:** reproducibility of the empirical
evidence class

```
git clone <repo> fresh && pytest -q
→ 2 failed, 38 passed
FAILED tests/test_canonical_records.py::test_every_canonical_manifest_binds_every_declared_artifact
FAILED tests/test_canonical_records.py::test_exp002_does_not_overclaim_mutable_source_replay
FileNotFoundError: results/resolved-weather-v0.1.manifest.json
```

`.gitignore:36` excludes `results/*.json`, but `tests/test_canonical_records.py`
requires those manifests. In a developer's working copy the files are present
and the suite reports 40/40; from a clean clone it is 38/40.

**Why this belongs in a formal-methods report.** The project's own standard —
"do not treat a Lean file as formal verification unless it compiles from a
pinned clean environment" — applies with equal force to its empirical evidence.
Two of the checks that back the canonical-records claims are currently
unreproducible outside one machine.

**Repair: infrastructure** — commit the manifests, or make the test skip
explicitly and loudly when they are absent. Do not weaken the assertion.

---

## CE-14 — The counting aggregator returns the wrong side on a universal claim
**kind:** `refutes_doctrine` · **target:** `aggregation/root_vote.verdict` applied
to universal claims, and every `flip_budget` presented beside an absence verdict

A universal claim — *every* member of a scope has property P — is falsified by
**one** counterexample, whatever the confirming count. The repository ships two
verdict paths and only one of them knows this.

```
PYTHONPATH=. python3 audit/ce14_asymmetric_claims.py

One ATTESTED counterexample against 999 confirmations of a universal claim:
  aggregation/root_vote  -> verdict='true'    margin=998 flip_budget=998
                            attested_margin=998 immunity_applicable=True
  knowledge_ledger v0.2  -> conclusion='present'  opposing_roots=1
```

Two shipped components, one input, opposite sides. `root_vote` is the aggregator
the compiled theorems are about (`formal/CLAIM-SCOPE.md`); it holds an **attested**
counterexample, reports the crowd's side, and attaches `immunity_applicable=True`
— which is not a claim that the verdict is right, but reads as one.

**Nothing here refutes a theorem.** T4 and T5 are about margins over root counts
and they are correct. What does not follow is the doctrine attached to them:
that `flip_budget` measures what it costs to overturn the verdict. On an
absence claim the margin decides nothing. Every branch of the rule reads
`(opposing evidence present, coverage complete)` and consults the margin in none
of them — so the number describes a quantity that did not determine the outcome,
and in the `present` case describes **the side that lost**. Measured on the run
above: `flipBudget: 998` presented for a conclusion carried by **one** root.

**Why no existing check caught it.** Every synthetic world in the programme is a
symmetric binary proposition where more roots is the right answer, so a
counting aggregator and an asymmetric rule never disagree. The divergence needs
a claim whose falsifier is singular, and the corpus contains none. This is
BL-060's failure shape one level up: not a population that cannot exhibit the
effect, but a **claim type** that cannot.

**Consequence for the copy-collapse result.** On an absence claim, copy collapse
is recorded and cannot reach the conclusion — 1 record and 20 records of the same
opposing root both yield `present`, differing only in
`repeatedRecordsCollapsed`. The repository's central mechanism is inert on
exactly the claim shape where a lone dissenter matters most. That is a scope
statement, not a defect in the mechanism.

### The mirror: existential claims fail the same way, in the other direction

"Does ANY member of the scope satisfy P?" is settled by **one verified find**,
and roots reporting an *unsuccessful search* are absence of evidence — they
cannot out-vote a find. `F` counts them, so it fails here too, symmetrically.
Compiled as AC5: three unsuccessful searches out-count one find, `F` reports
the claim false at margin −2, and the existential verdict is established.

Measured in `knowledge_ledger` v0.2's `presence` branch, which also counts:

```
found-it roots   looked-didn't-find   -> conclusion
             1                    0   -> supported
             1                    2   -> not_established
             1                  999   -> not_established
```

**This is registered as an open question, not as a defect.** Whether it is wrong
depends on what `oppose` means for a presence claim: *positive evidence that the
thing does not exist* (in which case counting is defensible) or *an unsuccessful
search* (in which case it is not). The evaluator does not distinguish the two,
and that ambiguity is the finding. It is the same kind of semantic decision the
owner made explicitly as A2 for the absence branch and has not made for this
one. Pinned by
`tests/test_asymmetric_claims.py::test_the_ledger_presence_branch_counts_pinned_as_an_open_question`
so that settling it is a visible change rather than a silent one.

**Repair, in two halves.**

*Done — the fence.* `aggregation.root_vote.verdict` takes `claim_shape` and
raises `AsymmetricClaimError` for `universal` and `existential`, before any
counting. The message names the evaluator that decides the universal direction
correctly, and states that no evaluator here decides the existential direction
correctly yet. Presentation is gated too (`knowledge_ledger/presentation.py`:
`budgetApplies`, `decidedByRootCount`).

**The fence is a declaration, not a detector.** Nothing in a claim iterable
reveals which question it answers, so a caller who mislabels a universal claim
as symmetric still gets the wrong answer and this does not catch it. The default
is `symmetric` because that is what every existing caller asks — it is not a
claim that an undeclared proposition has been checked. Pinned by
`test_the_fence_is_a_declaration_not_a_detector`.

*Done — the rule, proved.* `universalF` and `existentialF` are defined and
proved in `formal/lean/MinorityProphetCore/Asymmetric.lean` (AC1–AC5): one
counterexample suffices; the verdict is indifferent to the other side; and the
indifference is non-vacuous, since a refuted verdict coexists with an
arbitrarily large margin. Zero `sorry`, axioms `[propext, Classical.choice,
Quot.sound]` only, rebuilt clean at 3005 jobs.

*Done — the implementation.* `aggregation.root_vote.asymmetric_verdict`
implements AC1–AC5. It is a **separate function**, not a mode of `verdict`,
mirroring the Lean where `universalF` is a separate definition from `F` rather
than a special case of it — so no public signature changed, and the cost
originally quoted for this repair did not materialise. `verdict` still refuses
these shapes, because it is *proved* that counting does not answer them.

`AsymmetricVerdict` has no `margin`, no `flip_budget` and no
`conversions_to_reverse`. AC2 proves the outcome does not read the other side,
so those fields are **omitted rather than computed and ignored** — the CE-14
misreading has nothing to attach to. In their place, `roots_to_reverse`: every
decisive root must be removed to undo a positive outcome, and one new root
creates one.

`test_python_agrees_with_lean_on_the_ce14_worlds` encodes the two worlds AC4 and
AC5 are proved about and asserts the Python matches, so the ledger's
`lean_theorem` reference cannot drift into decoration.

**One branch is outside the proof, and is labelled as such.** `INDETERMINATE` —
returned for conflicting roots, and for a negative outcome when an unattributed
claim could itself be the decisive root — has no theorem behind it. The Lean
assumes side-consistency and an attributed root set. That branch is
implementation policy of the same evidence class as `unattributed_policy`, and
it fails closed. Note the asymmetry it encodes: an unattributed claim can create
a refutation but can never undo one, which is AC1 read in the direction of
missing data.

*Still open — the ledger's presence branch.* Unchanged by this repair. See the
mirror note above: it is an unmade semantic decision, not a defect awaiting
code.

---

## Negative result: the audit's own opening hypothesis was wrong

`audit/HYPOTHESIS.md` H0a predicted that the forest-vs-DAG mismatch would break
T5's ±1 edge lemma. **It does not.** Re-run in the multi-parent DAG:

| statement | domain | violations |
|---|---|---|
| Lemma 1 (side-locality) | 252 side-consistent DAG worlds, n ≤ 4 | 0 |
| T1 (immunity) | 1,992 root-preserving DAG rewirings | 0 |
| T2 (recorded copy) | 962 DAG duplications | 0 |
| ±1 per single edge edit | 1,072 DAG single-edge edits | 0 (max movement 1) |

The mismatch matters for **expressiveness** (CE-07, and partial dependence),
not for the truth of these four statements. Recorded here rather than deleted.
