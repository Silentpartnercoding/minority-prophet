/-
  Minority Prophet — immutable formal kernel, v3.

  Deliberate difference from `formal/MinorityProphetV2.lean`:
  V2 modelled lineage as `parent : Fin n → Option (Fin n)`, i.e. a FOREST
  (at most one parent, exactly one root per claim). The implementation
  (`provenance/graph.py`: `copied_from : tuple[str, ...]`, `roots() -> frozenset`)
  and FOUNDATIONS.md both describe a DAG. This file formalizes the DAG, which
  subsumes the forest, so no theorem here is a weaker substitute for a V2 claim.

  Acyclicity is imposed structurally by the time order (every parent index is
  strictly below the child index), exactly as PROOFS.md assumes.
-/
import Mathlib.Data.Finset.Basic
import Mathlib.Data.Finset.Card
import Mathlib.Data.Fintype.Basic
import Mathlib.Data.Fintype.BigOperators
import Mathlib.Tactic

namespace MinorityProphet

/-- A world: `n` claims, a multi-parent acyclic lineage, one binary assertion
each. `acyclic` is the time order assumption: a claim may only be derived from
strictly earlier claims. -/
structure World (n : ℕ) where
  parents : Fin n → Finset (Fin n)
  assert  : Fin n → Bool
  acyclic : ∀ i j, j ∈ parents i → j < i

variable {n : ℕ}

/-- Side consistency: no derivation edge crosses sides. -/
def SideConsistent (W : World n) : Prop :=
  ∀ i j, j ∈ W.parents i → W.assert j = W.assert i

/-- `rootsOf W i` = the parentless ancestors of `i`. Mirrors
`EvidenceGraph.roots` in `provenance/graph.py`. -/
def rootsOf (W : World n) (i : Fin n) : Finset (Fin n) :=
  if _h : (W.parents i).Nonempty then
    (W.parents i).attach.biUnion (fun j => rootsOf W j.1)
  else
    {i}
termination_by i.val
decreasing_by
  exact W.acyclic i j.1 j.2

/-- The claims that are roots: those with no recorded parent. -/
def rootSet (W : World n) : Finset (Fin n) :=
  Finset.univ.filter (fun i => W.parents i = ∅)

/-- `S_a(W)`: the roots supporting side `a`, defined exactly as in PROOFS.md —
the union of the root sets of the `a`-asserting claims. -/
def sideRoots (W : World n) (a : Bool) : Finset (Fin n) :=
  (Finset.univ.filter (fun i => W.assert i = a)).biUnion (rootsOf W)

inductive Verdict | one | zero | abstain
  deriving DecidableEq, Repr

/-- The specified aggregator: more roots wins, equality abstains. -/
def F (W : World n) : Verdict :=
  let s1 := (sideRoots W true).card
  let s0 := (sideRoots W false).card
  if s1 > s0 then .one else if s0 > s1 then .zero else .abstain

/-- Signed side-count margin. All of T4/T4'/T5 are statements about this. -/
def margin (W : World n) : ℤ :=
  ((sideRoots W true).card : ℤ) - ((sideRoots W false).card : ℤ)

/-- FACTORISATION: `F` sees nothing but the signed margin. This is definitional
and is the reason T1/T2/T4/T4'/T5 are all corollaries of counting arguments.
Recording it explicitly is the point: the content of the system lives in the
ASSUMPTIONS that control the margin, not in the theorems about it. -/
theorem F_eq_of_margin_eq (W W' : World n) (h : margin W = margin W') :
    F W = F W' := by
  unfold F
  unfold margin at h
  have h1 : (sideRoots W true).card > (sideRoots W false).card
          ↔ (sideRoots W' true).card > (sideRoots W' false).card := by omega
  have h0 : (sideRoots W false).card > (sideRoots W true).card
          ↔ (sideRoots W' false).card > (sideRoots W' true).card := by omega
  by_cases hc : (sideRoots W true).card > (sideRoots W false).card
  · simp [hc, h1.mp hc]
  · have hc' : ¬ ((sideRoots W' true).card > (sideRoots W' false).card) := by
      intro hx; exact hc (h1.mpr hx)
    by_cases hd : (sideRoots W false).card > (sideRoots W true).card
    · simp [hc, hc', hd, h0.mp hd]
    · have hd' : ¬ ((sideRoots W' false).card > (sideRoots W' true).card) := by
        intro hx; exact hd (h0.mpr hx)
      simp [hc, hc', hd, hd']

theorem F_one_iff (W : World n) : F W = .one ↔ 0 < margin W := by
  unfold F margin
  by_cases hc : (sideRoots W true).card > (sideRoots W false).card
  · simp [hc]
  · by_cases hd : (sideRoots W false).card > (sideRoots W true).card
    · simp [hc, hd]
    · simp [hc, hd]

theorem F_zero_iff (W : World n) : F W = .zero ↔ margin W < 0 := by
  unfold F margin
  by_cases hc : (sideRoots W true).card > (sideRoots W false).card
  · simp [hc]; omega
  · by_cases hd : (sideRoots W false).card > (sideRoots W true).card
    · simp [hc, hd]
    · simp [hc, hd]

theorem F_abstain_iff (W : World n) : F W = .abstain ↔ margin W = 0 := by
  unfold F margin
  by_cases hc : (sideRoots W true).card > (sideRoots W false).card
  · simp [hc]; omega
  · by_cases hd : (sideRoots W false).card > (sideRoots W true).card
    · simp [hc, hd]; omega
    · simp [hc, hd]; omega

end MinorityProphet
