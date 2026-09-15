/-
# DependenceRobustness — a robust settlement is the true settlement

`provenance/dependence_robustness.py` settles a decision only when every reading
of the recorded possible dependence gives the same settlement. DRI-3 confirmed
empirically that, under that rule, recorded stacked dependence never produced a
silent false settlement. That result was guaranteed by construction, so it
belongs here as a theorem rather than as an experiment.

Model. Observations `α` each assert a side (`value`). A **reading** `κ` labels
every observation with the root it belongs to. A reading is **admissible** when
any two observations it places on one root are joined by a chain of recorded
shared identities (`share`) that stays inside that root. The true causal grouping
is one admissible reading whenever every real dependence shows up somewhere in
the record, which is the assumption DRI-4 relaxes.

A reading's settlement fails closed on a root carrying both sides, as the kernel's
side-separation check does. Otherwise a side wins with strictly more roots and at
least `k` of them.

The engine does not enumerate readings. For each side it computes the fewest roots
(`fewest`, a count of components under any labelling `comp` that shared identities
on one side cannot split) and the most roots (`most`, one per observation), then
reads the settlement off two corners of that box.

* `reading_mem_reachable`: **every admissible reading's settlement is in the set
  the engine computes.**
* `robust_settlement_is_true`: **so when that set is a single settlement, every
  admissible reading, including the true grouping, settles that way.**

This is soundness only. The converse, that every computed settlement is achieved by
some reading, is checked by brute force in `tests/test_dependence_robustness.py`,
not proved here. The correspondence between these definitions and the Python
implementation is by construction, not proved.

No `sorry`. Standard axioms only.
-/
import Mathlib.Data.Finset.Card
import Mathlib.Data.Fintype.Basic
import Mathlib.Logic.Relation
import Mathlib.Tactic

namespace MinorityProphetCore.DependenceRobustness

open scoped Classical

inductive Settlement
  | settledTrue
  | settledFalse
  | unsettled
  deriving DecidableEq, Repr

/-- Root-vote settlement: a side wins with strictly more roots and at least `k`. -/
def settle (t f k : ℕ) : Settlement :=
  if t > f ∧ t ≥ k then .settledTrue
  else if f > t ∧ f ≥ k then .settledFalse
  else .unsettled

variable {α ι γ : Type*} [Fintype α]

/-- Observations asserting side `b`. -/
noncomputable def side (value : α → Bool) (b : Bool) : Finset α :=
  Finset.univ.filter (fun i => value i = b)

/-- Roots on side `b` under the reading `κ`. -/
noncomputable def sideRoots (value : α → Bool) (κ : α → ι) (b : Bool) : ℕ :=
  ((side value b).image κ).card

/-- The reading puts both sides on one root. -/
def Mixed (value : α → Bool) (κ : α → ι) : Prop :=
  ∃ i j, κ i = κ j ∧ value i ≠ value j

/-- A reading's settlement, failing closed on a mixed root. -/
noncomputable def readingSettlement (value : α → Bool) (κ : α → ι) (k : ℕ) : Settlement :=
  if Mixed value κ then .unsettled
  else settle (sideRoots value κ true) (sideRoots value κ false) k

/-- A reading the record cannot rule out: observations on one root are joined by
recorded shared identities without leaving that root. -/
def Admissible (share : α → α → Prop) (κ : α → ι) : Prop :=
  ∀ i j, κ i = κ j → Relation.ReflTransGen (fun a b => share a b ∧ κ a = κ b) i j

/-- `comp` cannot be split by a shared identity between two observations on the
same side. Connected components of same-side shared identities are one such
labelling, and the one the engine uses. -/
def SideInvariant (share : α → α → Prop) (value : α → Bool) (comp : α → γ) : Prop :=
  ∀ a b, share a b → value a = value b → comp a = comp b

/-- The engine's lower bound on a side's roots. -/
noncomputable def fewest (value : α → Bool) (comp : α → γ) (b : Bool) : ℕ :=
  ((side value b).image comp).card

/-- The engine's upper bound on a side's roots. -/
noncomputable def most (value : α → Bool) (b : Bool) : ℕ :=
  (side value b).card

/-- Some recorded shared identity joins observations on opposite sides. -/
def MixedPossible (share : α → α → Prop) (value : α → Bool) : Prop :=
  ∃ a b, share a b ∧ value a ≠ value b

/-- The settlements the engine reports as reachable, read off the corners. -/
noncomputable def reachable (share : α → α → Prop) (value : α → Bool) (comp : α → γ)
    (k : ℕ) : Finset Settlement :=
  (if settle (most value true) (fewest value comp false) k = .settledTrue
    then ({Settlement.settledTrue} : Finset Settlement) else ∅) ∪
  (if settle (fewest value comp true) (most value false) k = .settledFalse
    then ({Settlement.settledFalse} : Finset Settlement) else ∅) ∪
  (if settle (fewest value comp true) (most value false) k ≠ .settledTrue ∧
      settle (most value true) (fewest value comp false) k ≠ .settledFalse
    then ({Settlement.unsettled} : Finset Settlement) else ∅) ∪
  (if MixedPossible share value
    then ({Settlement.unsettled} : Finset Settlement) else ∅)

/-- Settlement is monotone in each count, so the corners of the count box decide it. -/
theorem settle_corners {t f tmin tmax fmin fmax k : ℕ}
    (ht1 : tmin ≤ t) (ht2 : t ≤ tmax) (hf1 : fmin ≤ f) (hf2 : f ≤ fmax) :
    (settle t f k = .settledTrue → settle tmax fmin k = .settledTrue) ∧
    (settle t f k = .settledFalse → settle tmin fmax k = .settledFalse) ∧
    (settle t f k = .unsettled →
      settle tmin fmax k ≠ .settledTrue ∧ settle tmax fmin k ≠ .settledFalse) := by
  refine ⟨?_, ?_, ?_⟩
  · intro h
    unfold settle at h ⊢
    by_cases h1 : t > f ∧ t ≥ k
    · rw [if_pos (by omega)]
    · rw [if_neg h1] at h
      split_ifs at h
  · intro h
    unfold settle at h ⊢
    by_cases h1 : t > f ∧ t ≥ k
    · rw [if_pos h1] at h; exact absurd h (by decide)
    · by_cases h2 : f > t ∧ f ≥ k
      · rw [if_neg (by omega), if_pos (by omega)]
      · rw [if_neg h1, if_neg h2] at h; exact absurd h (by decide)
  · intro h
    unfold settle at h
    by_cases h1 : t > f ∧ t ≥ k
    · rw [if_pos h1] at h; exact absurd h (by decide)
    · by_cases h2 : f > t ∧ f ≥ k
      · rw [if_neg h1, if_pos h2] at h; exact absurd h (by decide)
      · constructor
        · unfold settle
          rw [if_neg (by omega)]
          split_ifs <;> decide
        · unfold settle
          by_cases h3 : tmax > fmin ∧ tmax ≥ k
          · rw [if_pos h3]; decide
          · rw [if_neg h3, if_neg (by omega)]; decide

theorem sideRoots_le_most (value : α → Bool) (κ : α → ι) (b : Bool) :
    sideRoots value κ b ≤ most value b :=
  Finset.card_image_le

omit [Fintype α] in
/-- Without a mixed root, `comp` is constant along any admissible chain. -/
theorem comp_eq_of_chain {share : α → α → Prop} {value : α → Bool} {κ : α → ι}
    {comp : α → γ} (hmix : ¬ Mixed value κ) (hinv : SideInvariant share value comp)
    {i j : α} (h : Relation.ReflTransGen (fun a b => share a b ∧ κ a = κ b) i j) :
    comp i = comp j := by
  induction h with
  | refl => rfl
  | @tail b c _ hbc ih =>
    have hv : value b = value c := by
      by_contra hne
      exact hmix ⟨b, c, hbc.2, hne⟩
    exact ih.trans (hinv b c hbc.1 hv)

/-- An admissible reading with no mixed root never has fewer roots on a side than
the engine's lower bound. -/
theorem fewest_le_sideRoots {share : α → α → Prop} {value : α → Bool} {κ : α → ι}
    {comp : α → γ} (hadm : Admissible share κ) (hmix : ¬ Mixed value κ)
    (hinv : SideInvariant share value comp) (b : Bool) :
    fewest value comp b ≤ sideRoots value κ b := by
  unfold fewest sideRoots
  rcases (side value b).eq_empty_or_nonempty with hS | ⟨x0, _⟩
  · simp [hS]
  · let g : ι → γ := fun y =>
      if h : ∃ x ∈ side value b, κ x = y then comp h.choose else comp x0
    have hg : ∀ s ∈ side value b, g (κ s) = comp s := by
      intro s hs
      have h : ∃ x ∈ side value b, κ x = κ s := ⟨s, hs, rfl⟩
      have hspec := h.choose_spec
      show (if h : ∃ x ∈ side value b, κ x = κ s then comp h.choose else comp x0) = comp s
      rw [dif_pos h]
      exact comp_eq_of_chain hmix hinv (hadm _ _ hspec.2)
    calc ((side value b).image comp).card
        = (((side value b).image κ).image g).card := by
          congr 1
          ext c
          simp only [Finset.mem_image]
          constructor
          · rintro ⟨s, hs, rfl⟩
            exact ⟨κ s, ⟨s, hs, rfl⟩, hg s hs⟩
          · rintro ⟨y, ⟨s, hs, rfl⟩, rfl⟩
            exact ⟨s, hs, (hg s hs).symm⟩
      _ ≤ ((side value b).image κ).card := Finset.card_image_le

omit [Fintype α] in
/-- A mixed admissible reading forces a recorded shared identity across sides. -/
theorem mixedPossible_of_mixed {share : α → α → Prop} {value : α → Bool} {κ : α → ι}
    (hadm : Admissible share κ) (hmix : Mixed value κ) : MixedPossible share value := by
  obtain ⟨i, j, hk, hv⟩ := hmix
  have hchain := hadm i j hk
  clear hk
  revert hv
  induction hchain with
  | refl => intro hv; exact absurd rfl hv
  | @tail b c _ hbc ih =>
    intro hv
    by_cases hib : value i = value b
    · exact ⟨b, c, hbc.1, fun h => hv (hib.trans h)⟩
    · exact ih hib

/-- **Every admissible reading's settlement is among those the engine computes.** -/
theorem reading_mem_reachable (share : α → α → Prop) (value : α → Bool) (κ : α → ι)
    (comp : α → γ) (k : ℕ) (hadm : Admissible share κ)
    (hinv : SideInvariant share value comp) :
    readingSettlement value κ k ∈ reachable share value comp k := by
  unfold readingSettlement reachable
  by_cases hmix : Mixed value κ
  · have hp := mixedPossible_of_mixed hadm hmix
    simp [hmix, hp]
  · rw [if_neg hmix]
    obtain ⟨c1, c2, c3⟩ := settle_corners (k := k)
      (fewest_le_sideRoots hadm hmix hinv true) (sideRoots_le_most value κ true)
      (fewest_le_sideRoots hadm hmix hinv false) (sideRoots_le_most value κ false)
    generalize hs : settle (sideRoots value κ true) (sideRoots value κ false) k = s at c1 c2 c3
    cases s with
    | settledTrue => simp [c1 rfl]
    | settledFalse => simp [c2 rfl]
    | unsettled =>
      obtain ⟨u1, u2⟩ := c3 rfl
      simp [u1, u2]

/-- **Soundness.** If the engine reports a single settlement, every admissible
reading settles that way. In particular the true causal grouping does, whenever
the record carries every real dependence. -/
theorem robust_settlement_is_true (share : α → α → Prop) (value : α → Bool)
    (κ : α → ι) (comp : α → γ) (k : ℕ) (s : Settlement)
    (hadm : Admissible share κ) (hinv : SideInvariant share value comp)
    (hrobust : reachable share value comp k = {s}) :
    readingSettlement value κ k = s := by
  have h := reading_mem_reachable share value κ comp k hadm hinv
  rw [hrobust] at h
  simpa using h

end MinorityProphetCore.DependenceRobustness
