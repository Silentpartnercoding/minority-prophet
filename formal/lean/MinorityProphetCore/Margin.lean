/-
  T4, T4' and T5 — margin arithmetic.

  Every statement here is about `margin`, and every one is quantified over PAIRS
  of side-consistent worlds with EQUAL ASSERTIONS. That last hypothesis is the
  correction this audit makes to the repository's prose: it is exactly what
  separates a root-integrity error (worth 1 unit of margin) from a side
  conversion (worth 2). See COUNTEREXAMPLES.md CE-02 and CE-03.
-/
import MinorityProphetCore.Immunity

namespace MinorityProphet

variable {n : ℕ}

section Counting

variable {α : Type*} [DecidableEq α]

/-- `(#s - #t) = #(s \ t) - #(t \ s)` over ℤ. -/
theorem card_sub_card (s t : Finset α) :
    (s.card : ℤ) - (t.card : ℤ) = ((s \ t).card : ℤ) - ((t \ s).card : ℤ) := by
  have h1 := Finset.card_sdiff_add_card_inter s t
  have h2 := Finset.card_sdiff_add_card_inter t s
  have h3 : (s ∩ t).card = (t ∩ s).card := by rw [Finset.inter_comm]
  omega

/-- Filtering commutes with set difference. -/
theorem filter_sdiff (s t : Finset α) (p : α → Prop) [DecidablePred p] :
    (s \ t).filter p = s.filter p \ t.filter p := by
  ext x
  simp only [Finset.mem_filter, Finset.mem_sdiff, not_and]
  tauto

end Counting

/-- The two side-filters of any finset partition it. -/
theorem card_filter_true_add_false (W : World n) (s : Finset (Fin n)) :
    (s.filter (fun r => W.assert r = true)).card
      + (s.filter (fun r => W.assert r = false)).card = s.card := by
  rw [← Finset.card_filter_add_card_filter_not (s := s) (fun r => W.assert r = true)]
  congr 2
  ext x
  simp

/-- **Central counting bound.** With assertions held fixed, the margin moves by
at most the size of the symmetric difference of the root sets. This is the
strongest correct form of T5, and it makes no reference to "edits" at all: it
covers any combination of edge changes, claim additions and claim deletions. -/
theorem margin_diff_le_rootSet_diff (W W' : World n)
    (hW : SideConsistent W) (hW' : SideConsistent W')
    (hassert : W.assert = W'.assert) :
    |margin W - margin W'|
      ≤ ((rootSet W \ rootSet W').card : ℤ) + ((rootSet W' \ rootSet W).card : ℤ) := by
  set R := rootSet W with hR
  set R' := rootSet W' with hR'
  have hS : ∀ a : Bool, sideRoots W a = R.filter (fun r => W.assert r = a) :=
    fun a => sideRoots_eq_filter_rootSet W hW a
  have hS' : ∀ a : Bool, sideRoots W' a = R'.filter (fun r => W.assert r = a) := by
    intro a
    rw [sideRoots_eq_filter_rootSet W' hW' a, hassert]
  -- the four sdiff blocks
  have e1 : (R.filter (fun r => W.assert r = true)) \ (R'.filter (fun r => W.assert r = true))
      = (R \ R').filter (fun r => W.assert r = true) := (filter_sdiff R R' _).symm
  have e0 : (R.filter (fun r => W.assert r = false)) \ (R'.filter (fun r => W.assert r = false))
      = (R \ R').filter (fun r => W.assert r = false) := (filter_sdiff R R' _).symm
  have f1 : (R'.filter (fun r => W.assert r = true)) \ (R.filter (fun r => W.assert r = true))
      = (R' \ R).filter (fun r => W.assert r = true) := (filter_sdiff R' R _).symm
  have f0 : (R'.filter (fun r => W.assert r = false)) \ (R.filter (fun r => W.assert r = false))
      = (R' \ R).filter (fun r => W.assert r = false) := (filter_sdiff R' R _).symm
  have splitA := card_filter_true_add_false W (R \ R')
  have splitB := card_filter_true_add_false W (R' \ R)
  have d1 := card_sub_card (R.filter (fun r => W.assert r = true))
                           (R'.filter (fun r => W.assert r = true))
  have d0 := card_sub_card (R.filter (fun r => W.assert r = false))
                           (R'.filter (fun r => W.assert r = false))
  rw [e1, f1] at d1
  rw [e0, f0] at d0
  unfold margin
  rw [hS true, hS false, hS' true, hS' false]
  rw [abs_le]
  constructor <;> omega

/-- **T5 (root-error tolerance), strongest correct form.**
`k` root-set errors cannot change a verdict whose margin exceeds `k` —
PROVIDED the errors do not touch assertions. -/
theorem root_error_tolerance (W W' : World n)
    (hW : SideConsistent W) (hW' : SideConsistent W') (k : ℕ)
    (hassert : W.assert = W'.assert)
    (herr : (rootSet W \ rootSet W').card + (rootSet W' \ rootSet W).card ≤ k)
    (hmargin : (k : ℤ) < |margin W|) :
    F W' = F W := by
  have hb := margin_diff_le_rootSet_diff W W' hW hW' hassert
  have hk : ((rootSet W \ rootSet W').card : ℤ) + ((rootSet W' \ rootSet W).card : ℤ)
      ≤ (k : ℤ) := by exact_mod_cast herr
  have hd : |margin W - margin W'| ≤ (k : ℤ) := le_trans hb hk
  rw [abs_le] at hd
  have hkn : (0 : ℤ) ≤ (k : ℤ) := Int.natCast_nonneg k
  rcases lt_trichotomy (margin W) 0 with h | h | h
  · rw [abs_of_neg h] at hmargin
    have h1 : margin W' < 0 := by omega
    rw [(F_zero_iff W').mpr h1, (F_zero_iff W).mpr h]
  · exfalso
    rw [h] at hmargin
    simp only [abs_zero] at hmargin
    omega
  · rw [abs_of_pos h] at hmargin
    have h1 : 0 < margin W' := by omega
    rw [(F_one_iff W').mpr h1, (F_one_iff W).mpr h]

/-- **T5, reversal form.** `k` root-set errors with `k ≤ margin` cannot REVERSE
a decision; the most they can buy is abstention. -/
theorem no_reversal_of_margin_ge (W W' : World n)
    (hW : SideConsistent W) (hW' : SideConsistent W') (k : ℕ)
    (hassert : W.assert = W'.assert)
    (herr : (rootSet W \ rootSet W').card + (rootSet W' \ rootSet W).card ≤ k)
    (hmargin : (k : ℤ) ≤ margin W) :
    F W' ≠ .zero := by
  have hb := margin_diff_le_rootSet_diff W W' hW hW' hassert
  have hk : ((rootSet W \ rootSet W').card : ℤ) + ((rootSet W' \ rootSet W).card : ℤ)
      ≤ (k : ℤ) := by exact_mod_cast herr
  have hd : |margin W - margin W'| ≤ (k : ℤ) := le_trans hb hk
  rw [abs_le] at hd
  intro hcon
  rw [F_zero_iff] at hcon
  omega

/-- Net phantom flow, as defined in PROOFS.md T4: the net root gain of side 0
minus the net root gain of side 1. Equivalently the drop in the margin.

WARNING for downstream readers: one adversarial ACTION need not equal one unit
of `flow`. Converting a root from one side to the other contributes 2. -/
def flow (W W' : World n) : ℤ := margin W - margin W'

/-- **T4 (margin flip condition).** A verdict of `one` can only fail to survive
if the flow reaches the margin. -/
theorem T4_flip_requires_margin (W W' : World n)
    (_h1 : F W = .one) (h2 : F W' ≠ .one) :
    margin W ≤ flow W W' := by
  rw [F_one_iff] at _h1
  have : ¬ (0 < margin W') := fun hx => h2 ((F_one_iff W').mpr hx)
  unfold flow
  omega

/-- **T4' (tightness), corrected.** Flow of exactly the margin yields
ABSTENTION, and reversal requires margin + 1 — where `flow` is measured in the
units of T4 (net per-side gain), NOT in units of adversary actions. -/
theorem T4'_flow_eq_margin_abstains (W W' : World n) (h : flow W W' = margin W) :
    F W' = .abstain := by
  rw [F_abstain_iff]
  unfold flow at h
  omega

theorem T4'_reversal_needs_margin_succ (W W' : World n)
    (_h1 : F W = .one) (h2 : F W' = .zero) :
    margin W + 1 ≤ flow W W' := by
  rw [F_one_iff] at _h1
  rw [F_zero_iff] at h2
  unfold flow
  omega

/-- **PARITY (new; not present in the repository).** If the root set is held
fixed and only assertions move — a pure CONVERSION attack — the margin's parity
is invariant. -/
theorem margin_parity_of_rootSet_eq (W W' : World n)
    (hW : SideConsistent W) (hW' : SideConsistent W')
    (hroots : rootSet W = rootSet W') :
    (2 : ℤ) ∣ (margin W - margin W') := by
  have hW1 := card_sideRoots_add W hW
  have hW2 := card_sideRoots_add W' hW'
  rw [hroots] at hW1
  unfold margin
  omega

/-- **Consequence.** A pure conversion attack can never force abstention out of
an ODD margin: it must overshoot into full reversal. Denial-of-decision and
deception are therefore not separated by one unit at odd margins, contrary to
the repository's "denial costs the margin; deception costs margin+1" reading. -/
theorem no_abstention_of_odd_margin (W W' : World n)
    (hW : SideConsistent W) (hW' : SideConsistent W')
    (hroots : rootSet W = rootSet W') (hodd : ¬ (2 : ℤ) ∣ margin W) :
    F W' ≠ .abstain := by
  intro hcon
  rw [F_abstain_iff] at hcon
  have := margin_parity_of_rootSet_eq W W' hW hW' hroots
  rw [hcon] at this
  simp at this
  exact hodd this

end MinorityProphet
