/-
# RootIdentity — U1, closed by a doctrine of remoteness

The open problem: "what counts as one evidence root?" Every attempt to answer it
by tracing ancestry fails the same way. Ancestry is transitive and unbounded —
every claim descends from earlier claims forever — so any relation of the form
"shares an ancestor" has a transitive closure that swallows the whole corpus.
Force it to be an equivalence relation and `N_eff → 1`. The aggregator refuses
to believe anything.

The error was demanding an equivalence relation at all.

Criminal and tort law solved the identical problem centuries ago and did not
solve it by tracing harder. Cause-in-fact is unbounded and transitive; every
event has infinite ancestry. **Proximate cause** is a declared cut: beyond a
certain remoteness the chain no longer carries liability. Not because causation
stopped, but because responsibility did. `Novus actus interveniens` — an
intervening independent act breaks the chain.

Applied here: shared ancestry between two sources is **cut** by an intervening
independent re-derivation. Two sources descending from a common ancestor are
still independent witnesses if each re-established the claim through a channel
not passing through that ancestor.

Dependence is therefore a *graph relation relative to a proposition*, not an
equivalence, and the count is not a quotient. This file proves the consequence:

* `independent_card_le_lineages` — the **soundness** direction. Any set of
  pairwise-independent witnesses contains at most one member per true lineage,
  so counting a maximum independent set can never over-report independence
  relative to the detected dependence graph.

* `path_indep_two` — the witness that broke the old definition now gives the
  right answer. `A—B—C` with `A` and `C` unrelated: transitive closure reports
  1 independent witness; the independent-set count reports 2.

* `clique_indep_one` — and the count still collapses correctly when dependence
  really is transitive, so this generalizes the quotient definition rather than
  replacing it.

No `sorry`. Standard axioms only.
-/
import Mathlib.Data.Finset.Card
import Mathlib.Data.Fintype.Basic
import Mathlib.Tactic

namespace MinorityProphetCore.RootIdentity

variable {α ι : Type*} [DecidableEq α] [DecidableEq ι] [Fintype α]

/-- `S` is a set of witnesses no two of which are proximately dependent. -/
def Independent (dep : α → α → Prop) (S : Finset α) : Prop :=
  ∀ i ∈ S, ∀ j ∈ S, i ≠ j → ¬ dep i j

/-- Detection is *complete within a lineage*: two distinct witnesses sharing a
true lineage `κ` are always detected as dependent. This is the assumption the
soundness theorem rests on, and it is the assumption an adversary attacks by
laundering provenance — see `U1-PROXIMATE-ROOTS.md`. -/
def DetectsLineage (κ : α → ι) (dep : α → α → Prop) : Prop :=
  ∀ i j, κ i = κ j → i ≠ j → dep i j

omit [DecidableEq ι] [Fintype α] in
/-- Distinct members of an independent set have distinct lineages. -/
theorem independent_injOn_lineage {κ : α → ι} {dep : α → α → Prop}
    (hdet : DetectsLineage κ dep) {S : Finset α} (hS : Independent dep S) :
    Set.InjOn κ S := by
  intro i hi j hj hk
  by_contra hne
  exact hS i hi j hj hne (hdet i j hk hne)

/-- **Soundness.** An independent set never over-counts lineages: its cardinality
is at most the number of distinct true lineages present. Counting a maximum
independent set is therefore a safe replacement for the quotient count. -/
theorem independent_card_le_lineages {κ : α → ι} {dep : α → α → Prop}
    (hdet : DetectsLineage κ dep) {S : Finset α} (hS : Independent dep S) :
    S.card ≤ (Finset.univ.image κ).card := by
  have hinj := independent_injOn_lineage hdet hS
  have hcard : S.card = (S.image κ).card :=
    (Finset.card_image_of_injOn hinj).symm
  rw [hcard]
  exact Finset.card_le_card (Finset.image_subset_image (Finset.subset_univ S))

/-! ## The witness that broke the quotient definition

Three sources. `A` shares provenance with `B`; `B` shares different provenance
with `C`; `A` and `C` share nothing. Transitive closure merges all three into
one lineage and reports `N_eff = 1`. The correct answer is 2 — `A` and `C` are
genuinely independent witnesses. -/

/-- `dep` on `Fin 3`: the path `0 — 1 — 2`. -/
def pathDep (i j : Fin 3) : Prop := (i = 0 ∧ j = 1) ∨ (i = 1 ∧ j = 0) ∨
                                    (i = 1 ∧ j = 2) ∨ (i = 2 ∧ j = 1)

instance : DecidablePred fun p : Fin 3 × Fin 3 => pathDep p.1 p.2 := by
  intro p; unfold pathDep; infer_instance

/-- `{0, 2}` is independent: the endpoints of the path share nothing. -/
theorem path_indep_two : Independent pathDep {0, 2} := by
  intro i hi j hj hne
  fin_cases hi <;> fin_cases hj <;> simp_all [pathDep]

/-- So the independent-set count is 2, not the 1 that transitive closure gives. -/
theorem path_indep_card : ({0, 2} : Finset (Fin 3)).card = 2 := by decide

/-! ## And it still collapses when dependence really is transitive -/

/-- Total dependence: every pair is dependent, as inside one true lineage. -/
def cliqueDep (i j : Fin 3) : Prop := i ≠ j

/-- Under total dependence no two witnesses can be chosen together, so any
independent set has at most one member — the quotient answer. -/
theorem clique_indep_one {S : Finset (Fin 3)} (hS : Independent cliqueDep S) :
    S.card ≤ 1 := by
  rw [Finset.card_le_one]
  intro a ha b hb
  by_contra hne
  exact hS a ha b hb hne hne

end MinorityProphetCore.RootIdentity
