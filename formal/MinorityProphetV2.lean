/- Minority Prophet formal core, v2 — full proof attempts, no sorry.
   UNCOMPILED (sandbox has no toolchain): treat every proof as a strategy
   the compiler must ratify. Restructured from v1 for provability:
   the key lemma is `assert_root` (chains preserve assertion), proved by
   strong induction on the index; side_locality and immunity follow by
   set extensionality. If tactics fail, the induction SHAPE is the content —
   translate, don't redesign.  — for C. He / Codex, Task 4. -/
import Mathlib.Data.Finset.Basic
import Mathlib.Data.Fintype.Basic

structure World (n : ℕ) where
  parent  : Fin n → Option (Fin n)
  assert  : Fin n → Bool
  acyclic : ∀ i j, parent i = some j → j < i   -- time order (Fin.val order)

variable {n : ℕ}

def sideConsistent (W : World n) : Prop :=
  ∀ i j, W.parent i = some j → W.assert j = W.assert i

def root (W : World n) : Fin n → Fin n
  | i => match h : W.parent i with
    | none   => i
    | some j => root W j
  termination_by i => i.val
  decreasing_by exact W.acyclic _ _ h

/-- Unfolding equation for `root` (helper; `simp [root]` may suffice). -/
theorem root_eq (W : World n) (i : Fin n) :
    root W i = match W.parent i with
               | none => i
               | some j => root W j := by
  rw [root]

/-- Roots are fixed points: the root of any claim has no parent. -/
theorem parent_root_eq_none (W : World n) (i : Fin n) :
    W.parent (root W i) = none := by
  induction i using Fin.strongRecOn with
  | ind i ih =>
    rw [root_eq]
    cases h : W.parent i with
    | none => simpa [h] using h
    | some j => simpa [h] using ih j (W.acyclic i j h)

/-- KEY LEMMA: side-consistent chains preserve the assertion. -/
theorem assert_root (W : World n) (hs : sideConsistent W) (i : Fin n) :
    W.assert (root W i) = W.assert i := by
  induction i using Fin.strongRecOn with
  | ind i ih =>
    rw [root_eq]
    cases h : W.parent i with
    | none => simp [h]
    | some j =>
      have hj : j < i := W.acyclic i j h
      calc W.assert (root W j) = W.assert j := ih j hj
        _ = W.assert i := hs i j h

/-- A parentless claim is its own root. -/
theorem root_of_isRoot (W : World n) {r : Fin n} (hr : W.parent r = none) :
    root W r = r := by
  rw [root_eq, hr]

def sideRoots (W : World n) (a : Bool) : Finset (Fin n) :=
  (Finset.univ.filter (fun i => W.assert i = a)).image (root W)

/-- LEMMA 1 (side-locality): under side-consistency, S_a is exactly the
    a-asserting parentless claims. -/
theorem side_locality (W : World n) (hs : sideConsistent W) (a : Bool) :
    sideRoots W a
      = Finset.univ.filter (fun r => W.parent r = none ∧ W.assert r = a) := by
  ext r
  simp only [sideRoots, Finset.mem_image, Finset.mem_filter, Finset.mem_univ,
             true_and]
  constructor
  · rintro ⟨i, hi, rfl⟩
    exact ⟨parent_root_eq_none W i, by rw [assert_root W hs i]; exact hi⟩
  · rintro ⟨hr, ha⟩
    exact ⟨r, ha ▸ (by rw [root_of_isRoot W hr]) ▸ ha, root_of_isRoot W hr⟩
    -- if the anonymous-constructor gymnastics fail, use:
    -- exact ⟨r, by simpa [root_of_isRoot W hr] using ha, root_of_isRoot W hr⟩

inductive Verdict | one | zero | abstain deriving DecidableEq

def F (W : World n) : Verdict :=
  let s1 := (sideRoots W true).card
  let s0 := (sideRoots W false).card
  if s1 > s0 then .one else if s0 > s1 then .zero else .abstain

/-- THEOREM 1 (Immunity): equal assertions + equal root sets + side-
    consistency on both sides ⇒ identical verdicts, regardless of how the
    non-root lineage differs. -/
theorem immunity (W W' : World n)
    (hW : sideConsistent W) (hW' : sideConsistent W')
    (hassert : W.assert = W'.assert)
    (hroots : ∀ i, W.parent i = none ↔ W'.parent i = none) :
    F W = F W' := by
  have hSides : ∀ a, sideRoots W a = sideRoots W' a := by
    intro a
    rw [side_locality W hW a, side_locality W' hW' a]
    apply Finset.filter_congr
    intro r _
    constructor
    · rintro ⟨hr, ha⟩
      exact ⟨(hroots r).mp hr, by rw [← hassert]; exact ha⟩
    · rintro ⟨hr, ha⟩
      exact ⟨(hroots r).mpr hr, by rw [hassert]; exact ha⟩
  unfold F
  rw [hSides true, hSides false]

/-- THEOREM 3 (majority is not copy-invariant): explicit witness. -/
theorem majority_not_copyInvariant :
    ∃ (v dup : List Bool),
      (v.count true > v.count false) ∧
      (dup.count false > dup.count true) ∧
      dup = v ++ [false, false] := by
  exact ⟨[true, true, false], [true, true, false, false, false],
         by decide, by decide, rfl⟩

/- Task 4 remaining after this compiles:
   1. copy_invariant (T2): embed World n → World (n+1) adding a child of c
      with c's assertion; sideRoots are preserved under Fin.castSucc image —
      the paper proof is one line (duplicate's root already counted), the
      Lean cost is the embedding plumbing. Do it AFTER immunity compiles.
   2. T4/T4'/T5: verdict-margin arithmetic; T5's ±1-per-edit lemma is the
      natural next target (pure Finset.card counting, no recursion).
   3. Guard note (C4): all flow accounting is defined ONLY between
      side-consistent worlds; do not state flow for non-SC comparisons
      without multiset semantics — see PROOFS.md scope notes. -/
