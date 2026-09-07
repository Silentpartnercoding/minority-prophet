/-
  RESPONSIVENESS — the missing half of the attractor requirement.

  The requirement is two-sided: an irrelevant presentation change must leave the
  answer invariant, AND a material change must move it. The core proved only the
  first half. `immunity`, `copy_invariance` and `margin_parity_of_rootSet_eq` are
  all invariance statements; `margin_diff_le_rootSet_diff` is an upper bound. The
  only statement of the form `F W ≠ F W'` anywhere is `T5_needs_assert_fixed`,
  which is an EXISTENCE claim — there exist two worlds that differ — not a
  guarantee that a material change must register.

  Why that gap matters: an aggregator that ALWAYS ABSTAINS satisfies every
  invariance theorem in the core. It is perfectly immune to lineage corruption,
  perfectly copy-invariant, perfectly parity-preserving, and perfectly useless.
  Nothing proved so far excludes it.

  This file closes that hole. The key observation is that
  `margin_diff_le_rootSet_diff` discards information by taking an absolute value
  and weakening to `≤`. The underlying fact is an EQUALITY, and an equality
  constrains from both sides at once: it forbids the margin moving too much
  (invariance) and forbids it moving too little (responsiveness).
-/
import MinorityProphetCore.Margin

namespace MinorityProphet

variable {n : ℕ}

/-- The signed evidential weight of a set of roots: `a`-asserting minus
`¬a`-asserting. `margin` is exactly this over the whole root set. -/
def signedCount (W : World n) (S : Finset (Fin n)) : ℤ :=
  ((S.filter (fun r => W.assert r = true)).card : ℤ)
    - ((S.filter (fun r => W.assert r = false)).card : ℤ)

/-- Under side-consistency the margin is the signed count of the root set. -/
theorem margin_eq_signedCount (W : World n) (hW : SideConsistent W) :
    margin W = signedCount W (rootSet W) := by
  unfold margin signedCount
  rw [sideRoots_eq_filter_rootSet W hW true, sideRoots_eq_filter_rootSet W hW false]

/-- **THE EXACT IDENTITY.** With assertions fixed, the change in margin is
determined *exactly* by the signed weight of the roots that appeared and
disappeared — not merely bounded by it.

This strengthens `margin_diff_le_rootSet_diff` from `≤` to `=`, and it is the
whole content of this file: an equality pins the margin from both directions. -/
theorem margin_diff_eq_signedCount (W W' : World n)
    (hW : SideConsistent W) (hW' : SideConsistent W')
    (hassert : W.assert = W'.assert) :
    margin W - margin W'
      = signedCount W (rootSet W \ rootSet W')
        - signedCount W (rootSet W' \ rootSet W) := by
  set R := rootSet W
  set R' := rootSet W'
  have hS : ∀ a : Bool, sideRoots W a = R.filter (fun r => W.assert r = a) :=
    fun a => sideRoots_eq_filter_rootSet W hW a
  have hS' : ∀ a : Bool, sideRoots W' a = R'.filter (fun r => W.assert r = a) := by
    intro a; rw [sideRoots_eq_filter_rootSet W' hW' a, hassert]
  -- filtering commutes with set difference, so each side-count difference is
  -- itself a difference over the symmetric difference
  have e1 : (R.filter (fun r => W.assert r = true)) \ (R'.filter (fun r => W.assert r = true))
      = (R \ R').filter (fun r => W.assert r = true) := (filter_sdiff R R' _).symm
  have e0 : (R.filter (fun r => W.assert r = false)) \ (R'.filter (fun r => W.assert r = false))
      = (R \ R').filter (fun r => W.assert r = false) := (filter_sdiff R R' _).symm
  have f1 : (R'.filter (fun r => W.assert r = true)) \ (R.filter (fun r => W.assert r = true))
      = (R' \ R).filter (fun r => W.assert r = true) := (filter_sdiff R' R _).symm
  have f0 : (R'.filter (fun r => W.assert r = false)) \ (R.filter (fun r => W.assert r = false))
      = (R' \ R).filter (fun r => W.assert r = false) := (filter_sdiff R' R _).symm
  have d1 := card_sub_card (R.filter (fun r => W.assert r = true))
                           (R'.filter (fun r => W.assert r = true))
  have d0 := card_sub_card (R.filter (fun r => W.assert r = false))
                           (R'.filter (fun r => W.assert r = false))
  rw [e1, f1] at d1
  rw [e0, f0] at d0
  unfold margin signedCount
  rw [hS true, hS false, hS' true, hS' false]
  omega

/-- **RESPONSIVENESS.** If the roots that changed carry non-zero signed weight,
the margin MUST move. Contrapositive of the identity, and the statement the
attractor requirement was missing. -/
theorem margin_must_move (W W' : World n)
    (hW : SideConsistent W) (hW' : SideConsistent W')
    (hassert : W.assert = W'.assert)
    (hmaterial : signedCount W (rootSet W \ rootSet W')
               ≠ signedCount W (rootSet W' \ rootSet W)) :
    margin W ≠ margin W' := by
  intro hcon
  have h := margin_diff_eq_signedCount W W' hW hW' hassert
  rw [hcon] at h
  omega

/-- **NO INERT AGGREGATOR.** Adding `k` fresh roots that all assert one side
moves the margin by exactly `k`. A constant or always-abstaining rule cannot
satisfy this, which is what every invariance theorem alone failed to exclude. -/
theorem margin_shifts_by_added_roots (W W' : World n)
    (hW : SideConsistent W) (hW' : SideConsistent W')
    (hassert : W.assert = W'.assert)
    (K : Finset (Fin n))
    (hgrow : rootSet W' = rootSet W ∪ K)
    (hfresh : Disjoint (rootSet W) K)
    (hside : ∀ r ∈ K, W.assert r = true) :
    margin W' = margin W + (K.card : ℤ) := by
  have hlost : rootSet W \ rootSet W' = ∅ := by
    rw [hgrow]; exact Finset.sdiff_eq_empty_iff_subset.mpr Finset.subset_union_left
  have hgained : rootSet W' \ rootSet W = K := by
    rw [hgrow, Finset.union_sdiff_left]
    exact Finset.sdiff_eq_self_of_disjoint hfresh.symm
  have hK : signedCount W K = (K.card : ℤ) := by
    unfold signedCount
    have ht : K.filter (fun r => W.assert r = true) = K :=
      Finset.filter_true_of_mem hside
    have hf : K.filter (fun r => W.assert r = false) = ∅ := by
      apply Finset.filter_false_of_mem
      intro r hr; rw [hside r hr]; simp
    rw [ht, hf]; simp
  have h := margin_diff_eq_signedCount W W' hW hW' hassert
  rw [hlost, hgained, hK] at h
  simp only [signedCount, Finset.filter_empty, Finset.card_empty] at h
  omega

end MinorityProphet
