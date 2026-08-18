/-
  Asymmetric claims — the verdict rules that counting cannot express.

  `F` (Defs.lean) compares two root counts. Every theorem in Margin.lean and
  Copy.lean is about that comparison, and all of them are correct. What none of
  them covers is a claim whose falsifier is SINGULAR:

    universal    "every member of the scope satisfies P"
                 -> one counterexample root settles it AGAINST,
                    whatever the confirming count

    existential  "some member of the scope satisfies P"
                 -> one verified root settles it FOR, and roots reporting an
                    unsuccessful search cannot out-vote a find

  This file defines both and proves what they do and do not depend on. It is
  the formal precondition for implementing either in `aggregation/root_vote.py`:
  the repository's standard is that a proved rule may be implemented, not that
  an implemented rule may be assumed proved.

  Prose narration: formal/COUNTEREXAMPLES.md CE-14.

  CONVENTION. For a universal claim, side `true` is a confirming observation
  and side `false` is a counterexample. For an existential claim, side `true`
  is a successful find and side `false` an unsuccessful search. The convention
  is stated because it is not recoverable from the types.
-/
import MinorityProphetCore.Counterexamples
import Mathlib.Data.Fin.VecNotation

namespace MinorityProphet

variable {n : ℕ}

inductive AsymVerdict | refuted | notRefuted
  deriving DecidableEq, Repr

inductive ExistVerdict | established | notEstablished
  deriving DecidableEq, Repr

/-- Universal verdict: refuted exactly when some root asserts a counterexample.
Note what is absent — no comparison, no margin, no count. -/
def universalF (W : World n) : AsymVerdict :=
  if (sideRoots W false).Nonempty then .refuted else .notRefuted

/-- Existential verdict: established exactly when some root reports a find. -/
def existentialF (W : World n) : ExistVerdict :=
  if (sideRoots W true).Nonempty then .established else .notEstablished

/-! ### U1 — one counterexample root suffices, whatever the confirming count -/

theorem universal_one_counterexample_suffices (W : World n) (i : Fin n)
    (hi : i ∈ sideRoots W false) : universalF W = .refuted := by
  simp [universalF, Finset.nonempty_of_ne_empty, Finset.ne_empty_of_mem hi]

theorem existential_one_find_suffices (W : World n) (i : Fin n)
    (hi : i ∈ sideRoots W true) : existentialF W = .established := by
  simp [existentialF, Finset.nonempty_of_ne_empty, Finset.ne_empty_of_mem hi]

/-! ### U2 — the verdict is INDIFFERENT to the other side

    This is the whole content. `F` is a function of both sides; `universalF` is
    a function of one. So no amount of confirming evidence — and hence no
    margin, and hence no `flip_budget` — bears on a universal verdict. The
    corresponding statement for `F` is false. -/

theorem universal_indifferent_to_confirming_side (W W' : World n)
    (h : sideRoots W false = sideRoots W' false) :
    universalF W = universalF W' := by
  simp [universalF, h]

theorem existential_indifferent_to_unsuccessful_search (W W' : World n)
    (h : sideRoots W true = sideRoots W' true) :
    existentialF W = existentialF W' := by
  simp [existentialF, h]

/-- Immunity, for these verdicts, needs only ONE side's roots preserved — a
strictly weaker hypothesis than `immunity` in Immunity.lean requires. Copy
invariance for `universalF` is the special case where copies are recorded and
so create no root. -/
theorem universal_immunity_of_counterexample_roots (W W' : World n)
    (h : sideRoots W false = sideRoots W' false) :
    universalF W = universalF W' :=
  universal_indifferent_to_confirming_side W W' h

/-! ### U3 — the margin is not a budget here, and the statement is NOT vacuous

    U2 alone would be satisfied by a rule that never returns `refuted`. What
    makes it content is that a refuted verdict coexists with an ARBITRARILY
    LARGE margin. Constructed rather than assumed, because a theorem whose
    hypothesis is unreachable proves nothing (BL-060's discipline, applied to a
    proof rather than to a population). -/

/-- `k+1` confirming roots and exactly one counterexample root. -/
def wideWorld (k : ℕ) : World (k + 2) :=
  flatWorld (fun i => decide (i.val ≤ k))

theorem wideWorld_false_side (k : ℕ) :
    sideRoots (wideWorld k) false = {Fin.last (k + 1)} := by
  rw [wideWorld, flatWorld_sideRoots]
  ext i
  simp [Fin.ext_iff, Fin.last]
  omega

theorem wideWorld_true_side_card (k : ℕ) :
    (sideRoots (wideWorld k) true).card = k + 1 := by
  rw [wideWorld, flatWorld_sideRoots]
  have hneg :
      Finset.filter (fun i : Fin (k + 2) => ¬ (decide (i.val ≤ k) = true)) Finset.univ
      = {Fin.last (k + 1)} := by
    ext i
    simp [Fin.ext_iff, Fin.last]
    omega
  have hsplit := Finset.card_filter_add_card_filter_not
      (s := (Finset.univ : Finset (Fin (k + 2))))
      (fun i : Fin (k + 2) => decide (i.val ≤ k) = true)
  rw [hneg, Finset.card_singleton, Finset.card_univ, Fintype.card_fin] at hsplit
  omega

theorem universal_refuted_at_arbitrarily_large_margin (k : ℕ) :
    margin (wideWorld k) = (k : ℤ) ∧ universalF (wideWorld k) = .refuted := by
  constructor
  · unfold margin
    rw [wideWorld_true_side_card, wideWorld_false_side]
    simp
  · apply universal_one_counterexample_suffices _ (Fin.last (k + 1))
    rw [wideWorld_false_side]
    exact Finset.mem_singleton_self _

/-! ### CE-14 — machine-checked: the counting aggregator returns the other side

    Three confirming roots, one counterexample root. `F` reports the confirming
    side with margin 2 and `flip_budget` 2. The universal verdict is refuted.
    Same world, same roots, opposite answers — because they are answers to
    different questions, and only one of them is the question a universal claim
    asks. -/

def CE14_world : World 4 := flatWorld ![true, true, true, false]

theorem CE14_counting_reports_the_confirming_side :
    F CE14_world = Verdict.one
    ∧ margin CE14_world = 2
    ∧ universalF CE14_world = AsymVerdict.refuted := by
  refine ⟨?_, ?_, ?_⟩
  · unfold F CE14_world
    rw [flatWorld_sideRoots, flatWorld_sideRoots]
    decide
  · unfold margin CE14_world
    rw [flatWorld_sideRoots, flatWorld_sideRoots]
    decide
  · unfold universalF CE14_world
    rw [flatWorld_sideRoots]
    decide

/-- The mirror. One find, three unsuccessful searches: `F` reports that the
claim is false; the existential verdict is established. `F` is wrong in the
opposite direction, for the same reason. -/
def CE14_mirror_world : World 4 := flatWorld ![true, false, false, false]

theorem CE14_mirror_counting_reports_absence :
    F CE14_mirror_world = Verdict.zero
    ∧ margin CE14_mirror_world = -2
    ∧ existentialF CE14_mirror_world = ExistVerdict.established := by
  refine ⟨?_, ?_, ?_⟩
  · unfold F CE14_mirror_world
    rw [flatWorld_sideRoots, flatWorld_sideRoots]
    decide
  · unfold margin CE14_mirror_world
    rw [flatWorld_sideRoots, flatWorld_sideRoots]
    decide
  · unfold existentialF CE14_mirror_world
    rw [flatWorld_sideRoots]
    decide

end MinorityProphet
