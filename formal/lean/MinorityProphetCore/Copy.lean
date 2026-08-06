/-
  T2 — copy invariance, and T3 — majority is not copy-invariant.

  `formal/MinorityProphetV2.lean` left T2 as future work ("the Lean cost is the
  embedding plumbing"). It is done here.

  READ THE HYPOTHESIS. `addCopy` attaches the new claim to an EXISTING claim.
  A copy whose provenance is NOT recorded is a parentless claim, i.e. a root,
  and is governed by T5, not by this theorem. The plain-English slogan "adding
  copied claims cannot change the verdict" is false; see COUNTEREXAMPLES.md
  CE-01. This is the single most consequential wording correction in the audit.
-/
import MinorityProphetCore.Margin

namespace MinorityProphet

variable {n : ℕ}

/-- The time-order embedding of an `n`-claim world into an `(n+1)`-claim world.
Defined locally rather than reusing `Fin.castSuccEmb` because `simp` normalises
the latter to `Fin.castAdd 1`, which then fails to match `Fin.castSucc`. -/
def castEmb (n : ℕ) : Fin n ↪ Fin (n + 1) :=
  ⟨Fin.castSucc, Fin.castSucc_injective n⟩

@[simp] theorem castEmb_apply (i : Fin n) : castEmb n i = i.castSucc := rfl

/-- Append one claim at the end of time, derived from an existing claim `c` and
asserting whatever `c` asserts. Appending (rather than inserting) is forced by
the time-order encoding and is without loss of generality up to relabelling. -/
def addCopy (W : World n) (c : Fin n) : World (n + 1) where
  parents := Fin.lastCases {c.castSucc} (fun i => (W.parents i).map (castEmb n))
  assert := Fin.lastCases (W.assert c) (fun i => W.assert i)
  acyclic := by
    intro i j hj
    induction i using Fin.lastCases with
    | last =>
      simp only [Fin.lastCases_last, Finset.mem_singleton] at hj
      subst hj
      exact Fin.castSucc_lt_last c
    | cast k =>
      simp only [Fin.lastCases_castSucc, Finset.mem_map] at hj
      obtain ⟨j', hj', rfl⟩ := hj
      have h := W.acyclic k j' hj'
      simp only [castEmb_apply, Fin.lt_def, Fin.val_castSucc]
      exact h

@[simp] theorem addCopy_parents_last (W : World n) (c : Fin n) :
    (addCopy W c).parents (Fin.last n) = {c.castSucc} := by
  simp [addCopy]

@[simp] theorem addCopy_parents_castSucc (W : World n) (c : Fin n) (i : Fin n) :
    (addCopy W c).parents i.castSucc = (W.parents i).map (castEmb n) := by
  simp [addCopy]

@[simp] theorem addCopy_assert_castSucc (W : World n) (c : Fin n) (i : Fin n) :
    (addCopy W c).assert i.castSucc = W.assert i := by
  simp [addCopy]

@[simp] theorem addCopy_assert_last (W : World n) (c : Fin n) :
    (addCopy W c).assert (Fin.last n) = W.assert c := by
  simp [addCopy]

/-- A copy with a recorded, same-side parent preserves side-consistency. -/
theorem addCopy_sideConsistent (W : World n) (hs : SideConsistent W) (c : Fin n) :
    SideConsistent (addCopy W c) := by
  intro i j hj
  induction i using Fin.lastCases with
  | last =>
    rw [addCopy_parents_last, Finset.mem_singleton] at hj
    subst hj
    simp
  | cast k =>
    rw [addCopy_parents_castSucc, Finset.mem_map] at hj
    obtain ⟨j', hj', rfl⟩ := hj
    simpa using hs k j' hj'

/-- The copy is not a root, and every old root stays a root. -/
theorem addCopy_rootSet (W : World n) (c : Fin n) :
    rootSet (addCopy W c) = (rootSet W).map (castEmb n) := by
  ext x
  simp only [rootSet, Finset.mem_filter, Finset.mem_univ, true_and, Finset.mem_map]
  induction x using Fin.lastCases with
  | last =>
    simp only [addCopy_parents_last]
    constructor
    · intro h
      exact absurd h (by simp)
    · rintro ⟨i, _, hi⟩
      exact absurd hi (Fin.castSucc_ne_last i)
  | cast k =>
    simp only [addCopy_parents_castSucc, Finset.map_eq_empty]
    constructor
    · intro h
      exact ⟨k, h, rfl⟩
    · rintro ⟨i, hi, he⟩
      have : i = k := Fin.castSucc_injective n (by simpa using he)
      subst this
      exact hi

/-- Side-root sets are preserved (up to the index shift). -/
theorem addCopy_sideRoots (W : World n) (hs : SideConsistent W) (c : Fin n) (a : Bool) :
    sideRoots (addCopy W c) a = (sideRoots W a).map (castEmb n) := by
  rw [sideRoots_eq_filter_rootSet _ (addCopy_sideConsistent W hs c) a,
      sideRoots_eq_filter_rootSet W hs a, addCopy_rootSet]
  ext x
  simp only [Finset.mem_filter, Finset.mem_map, Finset.mem_filter]
  constructor
  · rintro ⟨⟨i, hi, he⟩, hassert⟩
    refine ⟨i, ⟨hi, ?_⟩, he⟩
    subst he
    simpa using hassert
  · rintro ⟨i, ⟨hi, ha⟩, he⟩
    refine ⟨⟨i, hi, he⟩, ?_⟩
    subst he
    simpa using ha

/-- **T2 (copy invariance).** Adding a claim that records a same-side parent
leaves both side-root counts, and therefore the verdict, unchanged. -/
theorem copy_invariance (W : World n) (hs : SideConsistent W) (c : Fin n) :
    F (addCopy W c) = F W := by
  unfold F
  rw [addCopy_sideRoots W hs c true, addCopy_sideRoots W hs c false,
      Finset.card_map, Finset.card_map]

/-- Copy invariance in margin form, for chaining with T4/T5. -/
theorem margin_addCopy (W : World n) (hs : SideConsistent W) (c : Fin n) :
    margin (addCopy W c) = margin W := by
  unfold margin
  rw [addCopy_sideRoots W hs c true, addCopy_sideRoots W hs c false,
      Finset.card_map, Finset.card_map]

/-- **T3 (majority voting is NOT copy-invariant).** Explicit witness: a
2-vs-1 true majority becomes a 2-vs-3 false majority after duplicating the
single dissenting claim twice. -/
theorem majority_not_copy_invariant :
    ∃ v dup : List Bool,
      v.count true > v.count false ∧
      dup.count false > dup.count true ∧
      dup = v ++ [false, false] :=
  ⟨[true, true, false], [true, true, false, false, false], by decide, by decide, rfl⟩

end MinorityProphet
