/-
# Junction: where a settlement waits on a new observable

`no_record_rule_is_immune` (ledger DR3) says no rule over a fixed record can
cover a dependence that record does not carry. This file states the operational
side of that result for the robustness engine in `DependenceRobustness.lean`.

* `conflicting_readings_block_settlement`: if the record admits two readings
  that settle differently, the engine reports no single settlement and the
  result is unsettled. Nothing changes that while both readings stay admissible,
  however many observations are added under the same record of possible
  dependence.
* `witness_linked_record_cannot_settle` and
  `witness_separated_record_settles`: on the DR3 witness, the same three
  observations do not settle while a possible shared source is recorded between
  the two true observations, and do settle true once that link is absent from
  the record. The settlement moves only when the record of possible dependence
  changes, which is what a new observable does.

A junction is the possible dependence that keeps the readings apart. A report
that abstains at a junction names it, and names the observation that would
remove it from the record or confirm it. If every obtainable record still admits
both readings, `conflicting_readings_block_settlement` applies to each of them
and the engine never settles. That case is a floor, and the report abstains and
names the assumption.

This file models the engine only. It does not model any physical experiment,
and it does not show that a proposed observable separates the readings in fact.

No `sorry`. Standard axioms only.
-/
import MinorityProphetCore.DependenceRobustness

namespace MinorityProphetCore.DependenceRobustness

open scoped Classical

variable {α ι γ : Type*} [Fintype α]

/-- A junction blocks settlement. If two readings the record allows settle
differently, the engine reports no single settlement. -/
theorem conflicting_readings_block_settlement (share : α → α → Prop)
    (value : α → Bool) (κ₁ κ₂ : α → ι) (comp : α → γ) (k : ℕ)
    (h₁ : Admissible share κ₁) (h₂ : Admissible share κ₂)
    (hinv : SideInvariant share value comp)
    (hdiff : readingSettlement value κ₁ k ≠ readingSettlement value κ₂ k) :
    ∀ s, reachable share value comp k ≠ {s} := by
  intro s hs
  apply hdiff
  rw [robust_settlement_is_true share value κ₁ comp k s h₁ hinv hs,
    robust_settlement_is_true share value κ₂ comp k s h₂ hinv hs]

/-- A record of possible dependence between the two true observations of the
witness, and nothing else. -/
def linkShare : Fin 3 → Fin 3 → Prop :=
  fun a b => (a = 0 ∧ b = 1) ∨ (a = 1 ∧ b = 0)

theorem witness_merged_admissible_linked : Admissible linkShare witnessMerged := by
  intro i j h
  fin_cases i <;> fin_cases j <;>
    first
    | exact Relation.ReflTransGen.refl
    | exact Relation.ReflTransGen.single ⟨by simp [linkShare], by decide⟩
    | exact absurd h (by decide)

theorem witness_distinct_admissible_linked :
    Admissible linkShare (id : Fin 3 → Fin 3) := by
  intro i j h
  rw [show i = j from h]

/-- The engine's labelling for the linked record: the two linked observations
form one component. -/
theorem witness_merged_sideInvariant_linked :
    SideInvariant linkShare witnessValue witnessMerged := by
  rintro a b (⟨rfl, rfl⟩ | ⟨rfl, rfl⟩) _ <;> rfl

/-- While the link is recorded, the witness cannot settle. -/
theorem witness_linked_record_cannot_settle :
    ∀ s, reachable linkShare witnessValue witnessMerged 1 ≠ {s} :=
  conflicting_readings_block_settlement linkShare witnessValue
    (id : Fin 3 → Fin 3) witnessMerged witnessMerged 1
    witness_distinct_admissible_linked witness_merged_admissible_linked
    witness_merged_sideInvariant_linked
    (by rw [witness_distinct_settles, witness_merged_unsettled]; decide)

/-- Once the link is absent from the record, the same observations settle. -/
theorem witness_separated_record_settles :
    reachable noShare witnessValue (id : Fin 3 → Fin 3) 1 = {Settlement.settledTrue} := by
  have hm : ¬ MixedPossible noShare witnessValue := by
    rintro ⟨_, _, h, _⟩; exact h
  unfold reachable fewest most
  rw [witness_true_side, witness_false_side, if_neg hm]
  simp [settle]

end MinorityProphetCore.DependenceRobustness
