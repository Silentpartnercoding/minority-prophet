/-
  Machine-checked counterexamples.

  These are not decorations. Each one proves that a hypothesis appearing in
  `Margin.lean` or `Copy.lean` is NECESSARY: delete it and the theorem is false.
  Together with the theorems they pin the statements from both sides.

  Prose narration lives in COUNTEREXAMPLES.md; the identifiers CE-nn match.
-/
import MinorityProphetCore.Copy
import Mathlib.Data.Fin.VecNotation

namespace MinorityProphet

/-- A world in which nothing is derived from anything: every claim is a root.
This is what an evidence set with NO recorded provenance looks like. -/
def flatWorld {n : ℕ} (a : Fin n → Bool) : World n where
  parents := fun _ => ∅
  assert := a
  acyclic := by intro i j hj; simp at hj

theorem flatWorld_sideConsistent {n : ℕ} (a : Fin n → Bool) :
    SideConsistent (flatWorld a) := by
  intro i j hj
  simp [flatWorld] at hj

theorem flatWorld_rootSet {n : ℕ} (a : Fin n → Bool) :
    rootSet (flatWorld a) = Finset.univ := by
  ext i
  simp [rootSet, flatWorld]

theorem flatWorld_sideRoots {n : ℕ} (a : Fin n → Bool) (s : Bool) :
    sideRoots (flatWorld a) s = Finset.univ.filter (fun i => a i = s) := by
  rw [sideRoots_eq_filter_rootSet _ (flatWorld_sideConsistent a) s,
      flatWorld_rootSet]
  rfl

/-! ### CE-01 — "adding copied claims cannot change the verdict" is FALSE
    when the copy's provenance is not recorded.

    T2 (`copy_invariance`) requires the copy to record a parent. Two copies of
    the losing side's single claim, entered WITHOUT provenance, reverse the
    verdict. This is the undetected-copy threat the project exists to address,
    so the slogan must never be stated without its hypothesis. -/

def CE01_before : World 3 := flatWorld ![true, true, false]
def CE01_after : World 5 := flatWorld ![true, true, false, false, false]

theorem CE01_unrecorded_copies_flip_the_verdict :
    F CE01_before = Verdict.one ∧ F CE01_after = Verdict.zero
    -- the two added claims assert exactly what claim 2 asserts …
    ∧ CE01_after.assert 3 = CE01_before.assert 2
    ∧ CE01_after.assert 4 = CE01_before.assert 2
    -- … and are entered with no recorded parent, i.e. as roots
    ∧ CE01_after.parents 3 = ∅
    ∧ CE01_after.parents 4 = ∅ := by
  refine ⟨?_, ?_, rfl, rfl, rfl, rfl⟩
  · unfold F CE01_before
    rw [flatWorld_sideRoots, flatWorld_sideRoots]
    decide
  · unfold F CE01_after
    rw [flatWorld_sideRoots, flatWorld_sideRoots]
    decide

/-! ### CE-02 — the `hassert` hypothesis of T5 is NECESSARY.

    Here the root set is IDENTICAL in both worlds, so the root-set error count
    is ZERO and `root_error_tolerance` with `k = 0` would predict an unchanged
    verdict for any margin > 0. The verdict changes anyway, because one root was
    CONVERTED to the other side rather than created or destroyed.

    A conversion is worth 2 units of margin, not 1. The repository's T5
    corollary ("k root-integrity errors cannot change a verdict with margin > k")
    and T4' ("reversal requires margin+1") both measure the adversary in the
    wrong unit. -/

def CE02_before : World 4 := flatWorld ![true, true, true, false]
def CE02_after : World 4 := flatWorld ![false, true, true, false]

theorem CE02_conversion_moves_margin_by_two :
    rootSet CE02_before = rootSet CE02_after
    ∧ margin CE02_before = 2
    ∧ margin CE02_after = 0
    ∧ F CE02_before = Verdict.one
    ∧ F CE02_after = Verdict.abstain := by
  refine ⟨by rw [CE02_before, CE02_after, flatWorld_rootSet, flatWorld_rootSet], ?_, ?_, ?_, ?_⟩
  · unfold margin CE02_before
    rw [flatWorld_sideRoots, flatWorld_sideRoots]
    decide
  · unfold margin CE02_after
    rw [flatWorld_sideRoots, flatWorld_sideRoots]
    decide
  · unfold F CE02_before
    rw [flatWorld_sideRoots, flatWorld_sideRoots]
    decide
  · unfold F CE02_after
    rw [flatWorld_sideRoots, flatWorld_sideRoots]
    decide

/-- CE-02 stated as an explicit necessity claim: there is no theorem of the
form "zero root-set errors and margin > 0 implies the verdict survives" once
assertions are allowed to move. -/
theorem T5_needs_assert_fixed :
    ∃ (W W' : World 4), SideConsistent W ∧ SideConsistent W'
      ∧ rootSet W = rootSet W'
      ∧ 0 < margin W
      ∧ F W ≠ F W' := by
  refine ⟨CE02_before, CE02_after, flatWorld_sideConsistent _,
          flatWorld_sideConsistent _, ?_, ?_, ?_⟩
  · rw [CE02_before, CE02_after, flatWorld_rootSet, flatWorld_rootSet]
  · have h := CE02_conversion_moves_margin_by_two
    rw [h.2.1]; norm_num
  · have h := CE02_conversion_moves_margin_by_two
    rw [h.2.2.2.1, h.2.2.2.2]
    exact fun hx => Verdict.noConfusion hx

/-! ### CE-06 — side-consistency is NECESSARY for Lemma 1.

    Without it the literal definition `S_a = ⋃ {rootsOf c : assert c = a}` puts
    the SAME root in both side sets, so the two "independent evidence counts"
    are not counts of disjoint evidence at all. -/

def CE06 : World 2 where
  parents := ![∅, {0}]
  assert := ![false, true]
  acyclic := by decide

theorem CE06_root_supports_both_sides :
    ¬ SideConsistent CE06
    ∧ (0 : Fin 2) ∈ sideRoots CE06 true
    ∧ (0 : Fin 2) ∈ sideRoots CE06 false := by
  have hp0 : CE06.parents 0 = ∅ := rfl
  have hp1 : CE06.parents 1 = {0} := rfl
  have hr0 : rootsOf CE06 0 = {0} := rootsOf_of_isRoot CE06 hp0
  have hr1 : rootsOf CE06 1 = {0} := by
    rw [rootsOf]
    rw [dif_pos (by rw [hp1]; exact Finset.singleton_nonempty 0)]
    rw [hp1]
    decide +kernel
  refine ⟨?_, ?_, ?_⟩
  · intro hs
    have := hs 1 0 (by rw [hp1]; exact Finset.mem_singleton_self 0)
    exact absurd this (by decide)
  · rw [sideRoots, Finset.mem_biUnion]
    exact ⟨1, by decide, by rw [hr1]; exact Finset.mem_singleton_self 0⟩
  · rw [sideRoots, Finset.mem_biUnion]
    exact ⟨0, by decide, by rw [hr0]; exact Finset.mem_singleton_self 0⟩

end MinorityProphet
