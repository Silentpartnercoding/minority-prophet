/-
  Lemma 1 (side-locality) for the multi-parent DAG model.

  This is the ONLY place side-consistency is consumed. Everything downstream
  (T1, T2, T4, T4', T5) is counting arithmetic on top of this bridge.

  NOTE for the record: `formal/MinorityProphetV2.lean` proves its analogue with
  `induction ... using Fin.strongRecOn`. No such constant exists in Mathlib
  (checked against mathlib4 @ 905b958 / Lean 4.32.2). That file could not have
  compiled as written; the recursion principle is supplied here explicitly.
-/
import MinorityProphetCore.Defs

namespace MinorityProphet

variable {n : ℕ}

/-- Strong induction along the lineage order. Supplied explicitly because
Mathlib has no `Fin.strongRecOn`. -/
theorem lineage_induction (W : World n) (P : Fin n → Prop)
    (step : ∀ i, (∀ j ∈ W.parents i, P j) → P i) : ∀ i, P i := by
  have key : ∀ k : ℕ, ∀ i : Fin n, i.val ≤ k → P i := by
    intro k
    induction k with
    | zero =>
      intro i hi
      refine step i (fun j hj => ?_)
      have h : j.val < i.val := W.acyclic i j hj
      exact absurd h (by omega)
    | succ k ih =>
      intro i hi
      refine step i (fun j hj => ?_)
      have h : j.val < i.val := W.acyclic i j hj
      exact ih j (by omega)
  intro i
  exact key i.val i le_rfl

/-- A parentless claim is its own only root. -/
theorem rootsOf_of_isRoot (W : World n) {i : Fin n} (h : W.parents i = ∅) :
    rootsOf W i = {i} := by
  rw [rootsOf]
  simp [h]

/-- Every element of `rootsOf W i` really is a root. -/
theorem isRoot_of_mem_rootsOf (W : World n) :
    ∀ (i : Fin n), ∀ r ∈ rootsOf W i, W.parents r = ∅ := by
  refine lineage_induction W _ (fun i ih => ?_)
  intro r hr
  rw [rootsOf] at hr
  by_cases hne : (W.parents i).Nonempty
  · rw [dif_pos hne, Finset.mem_biUnion] at hr
    obtain ⟨j, _, hj⟩ := hr
    exact ih j.1 j.2 r hj
  · rw [dif_neg hne, Finset.mem_singleton] at hr
    subst hr
    exact Finset.not_nonempty_iff_eq_empty.mp hne

/-- KEY LEMMA: under side-consistency every root of `i` asserts what `i`
asserts. DAG analogue of V2's `assert_root`. -/
theorem assert_of_mem_rootsOf (W : World n) (hs : SideConsistent W) :
    ∀ (i : Fin n), ∀ r ∈ rootsOf W i, W.assert r = W.assert i := by
  refine lineage_induction W _ (fun i ih => ?_)
  intro r hr
  rw [rootsOf] at hr
  by_cases hne : (W.parents i).Nonempty
  · rw [dif_pos hne, Finset.mem_biUnion] at hr
    obtain ⟨j, _, hj⟩ := hr
    rw [ih j.1 j.2 r hj, hs i j.1 j.2]
  · rw [dif_neg hne, Finset.mem_singleton] at hr
    subst hr
    rfl

/-- LEMMA 1 (side-locality). Under side-consistency, `S_a(W)` is exactly the
set of `a`-asserting roots. -/
theorem side_locality (W : World n) (hs : SideConsistent W) (a : Bool) :
    sideRoots W a
      = Finset.univ.filter (fun r => W.parents r = ∅ ∧ W.assert r = a) := by
  ext r
  simp only [sideRoots, Finset.mem_biUnion, Finset.mem_filter, Finset.mem_univ,
             true_and]
  constructor
  · rintro ⟨i, hi, hr⟩
    exact ⟨isRoot_of_mem_rootsOf W i r hr,
           by rw [assert_of_mem_rootsOf W hs i r hr]; exact hi⟩
  · rintro ⟨hroot, ha⟩
    exact ⟨r, ha, by rw [rootsOf_of_isRoot W hroot]; exact Finset.mem_singleton_self r⟩

/-- `S_a(W)` is a filter of the root set. Used by every counting theorem. -/
theorem sideRoots_eq_filter_rootSet (W : World n) (hs : SideConsistent W) (a : Bool) :
    sideRoots W a = (rootSet W).filter (fun r => W.assert r = a) := by
  rw [side_locality W hs a, rootSet, Finset.filter_filter]

/-- Under side-consistency the two sides partition the root set. In particular
NO root can support both sides — the property that fails outright without it
(see COUNTEREXAMPLES.md, CE-06). -/
theorem sideRoots_disjoint (W : World n) (hs : SideConsistent W) :
    Disjoint (sideRoots W true) (sideRoots W false) := by
  rw [sideRoots_eq_filter_rootSet W hs, sideRoots_eq_filter_rootSet W hs,
      Finset.disjoint_filter]
  intro x _ hx
  simp [hx]

theorem sideRoots_union (W : World n) (hs : SideConsistent W) :
    sideRoots W true ∪ sideRoots W false = rootSet W := by
  rw [sideRoots_eq_filter_rootSet W hs, sideRoots_eq_filter_rootSet W hs]
  ext r
  simp only [Finset.mem_union, Finset.mem_filter]
  constructor
  · rintro (⟨h, _⟩ | ⟨h, _⟩) <;> exact h
  · intro h
    by_cases hb : W.assert r = true
    · exact Or.inl ⟨h, hb⟩
    · exact Or.inr ⟨h, by simpa using hb⟩

/-- The two side-counts sum to the number of roots. -/
theorem card_sideRoots_add (W : World n) (hs : SideConsistent W) :
    (sideRoots W true).card + (sideRoots W false).card = (rootSet W).card := by
  rw [← sideRoots_union W hs]
  exact (Finset.card_union_of_disjoint (sideRoots_disjoint W hs)).symm

end MinorityProphet
