/-
  T1 — Immunity.

  Stated in the general (root-set) form rather than the "re-target existing
  edges" form of PROOFS.md. The general form is strictly stronger and does not
  mention edits at all: any two side-consistent worlds with the same assertions
  and the same ROOT SET have the same verdict, however different their lineage.
-/
import MinorityProphetCore.Locality

namespace MinorityProphet

variable {n : ℕ}

/-- Under side-consistency, equal assertions + equal root sets force equal
side-root sets. -/
theorem sideRoots_congr (W W' : World n)
    (hW : SideConsistent W) (hW' : SideConsistent W')
    (hassert : W.assert = W'.assert) (hroots : rootSet W = rootSet W') (a : Bool) :
    sideRoots W a = sideRoots W' a := by
  rw [sideRoots_eq_filter_rootSet W hW a, sideRoots_eq_filter_rootSet W' hW' a,
      hroots, hassert]

/-- **T1 (Immunity).** Lineage may be arbitrarily corrupted — edges added,
deleted or re-targeted in any pattern — and the verdict cannot move, PROVIDED
the corruption (i) keeps every derivation edge on one side, and (ii) neither
manufactures nor destroys a root, and (iii) leaves assertions alone.

Condition (iii) is NOT decorative: dropping it makes the statement false
(COUNTEREXAMPLES.md, CE-02). -/
theorem immunity (W W' : World n)
    (hW : SideConsistent W) (hW' : SideConsistent W')
    (hassert : W.assert = W'.assert) (hroots : rootSet W = rootSet W') :
    F W = F W' := by
  unfold F
  rw [sideRoots_congr W W' hW hW' hassert hroots true,
      sideRoots_congr W W' hW hW' hassert hroots false]

/-- The same statement in the pointwise form PROOFS.md uses ("preserves the set
of roots"), for direct comparison with the prose. -/
theorem immunity_pointwise (W W' : World n)
    (hW : SideConsistent W) (hW' : SideConsistent W')
    (hassert : W.assert = W'.assert)
    (hroots : ∀ i, W.parents i = ∅ ↔ W'.parents i = ∅) :
    F W = F W' := by
  refine immunity W W' hW hW' hassert ?_
  ext r
  simp only [rootSet, Finset.mem_filter, Finset.mem_univ, true_and]
  exact hroots r

end MinorityProphet
