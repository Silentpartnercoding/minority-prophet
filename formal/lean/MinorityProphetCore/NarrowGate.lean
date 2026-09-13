/-
# NarrowGate — the formal core of the MP Canon, Phase I

Three results, and the point of the file is that they do not say what the
original brief expected them to say.

1. `gate_preserves_viability` — the Narrow Gate Safety Theorem. It holds, and it
   needs **no** invariance hypothesis at all: one-step containment is enough for
   safety by a two-line induction. Safety is cheap.

2. `demo_gate_one_empty` — and that is exactly the problem. A gate can achieve
   perfect safety by admitting nothing. The witness below is a system whose
   declared-safe set `V` is not controlled-invariant: the gate walks it into a
   state where every available effect leaves `V`, so the gate empties and the
   system is paralysed. It never leaves `V`. It also never does anything.

   So the correction to the brief is not that its safety theorem is unsound —
   it is that safety was never the scarce property. `FalseDenyRate` is.

3. `invariant_gate_nonempty` — controlled invariance is the hypothesis that buys
   back liveness. If `V` is controlled-invariant, the gate is non-empty at every
   state in `V`, so safety and the ability to act coexist. This is the real
   engineering requirement, and it is expensive: someone must compute an
   under-approximation of the viability kernel. Under-approximating is sound
   (it refuses more than necessary); over-approximating is not.

Plus `strict_contraction_inert`, which machine-checks the objection to Law 1:
authority that only ever contracts, strictly, reaches the empty set in finitely
many steps. Monotone contraction is a termination argument, not a safety
property, unless authority may be renewed at an authenticated mandate boundary.

No `sorry`. Standard axioms only.
-/
import Mathlib.Data.Set.Basic
import Mathlib.Data.Finset.Card
import Mathlib.Tactic

namespace MinorityProphetCore.NarrowGate

universe u v
variable {S : Type u} {E : Type v}

/-! ## Part 1 — Law 1, non-expansion of authority -/

/-- An authority chain: each transformation may only shrink the permitted set. -/
def AuthorityChain (M : ℕ → Set E) : Prop := ∀ i, M (i + 1) ⊆ M i

/-- Authority never expands across any number of transformations. -/
theorem no_authority_creation {M : ℕ → Set E} (h : AuthorityChain M) :
    ∀ {i j : ℕ}, i ≤ j → M j ⊆ M i := by
  intro i j hij
  induction hij with
  | refl => exact subset_rfl
  | step _ ih => exact (h _).trans ih

/-- Effects still authorized after `n` transformations. -/
def surviving (M : ℕ → Set E) (n : ℕ) : Set E := {e | ∀ i ≤ n, e ∈ M i}

/-- Along a chain, surviving authority is just the last mandate: the intersection
in the Narrow Gate definition carries no information the chain does not already
give. This is a simplification lemma, not a result. -/
theorem surviving_eq_last {M : ℕ → Set E} (h : AuthorityChain M) (n : ℕ) :
    surviving M n = M n := by
  ext e
  constructor
  · intro he; exact he n le_rfl
  · intro he i hi; exact no_authority_creation h hi he

/-! ## Part 2 — strict contraction terminates the system -/

/-- Each strict contraction spends at least one unit of authority. -/
theorem strict_contraction_budget [DecidableEq E] (M : ℕ → Finset E)
    (hstrict : ∀ i, M (i + 1) ⊂ M i) (n : ℕ) : (M n).card + n ≤ (M 0).card := by
  induction n with
  | zero => simp
  | succ k ih =>
    have hlt : (M (k + 1)).card < (M k).card := Finset.card_lt_card (hstrict k)
    omega

/-- Authority that only ever contracts, strictly, is exhausted in finitely many
steps: the agent becomes inert. Perfectly safe, entirely useless. Law 1 is
therefore sound within one derivation chain and false across mandate epochs. -/
theorem strict_contraction_inert [DecidableEq E] (M : ℕ → Finset E)
    (hstrict : ∀ i, M (i + 1) ⊂ M i) : M (M 0).card = ∅ := by
  have h := strict_contraction_budget M hstrict (M 0).card
  have hz : (M (M 0).card).card = 0 := by omega
  exact Finset.card_eq_zero.mp hz

/-! ## Part 3 — the Narrow Gate -/

/-- A system: a transition function and the technically-possible effects at each
state. `adm` is capability; it is deliberately *not* permission. -/
structure System (S : Type u) (E : Type v) where
  T : S → E → S
  adm : S → Set E

/-- The gate at state `s`: admissible effects whose successor stays in `V`. -/
def Gate (sys : System S E) (V : Set S) (s : S) : Set E :=
  {e | e ∈ sys.adm s ∧ sys.T s e ∈ V}

/-- States reachable from `s₀` when every step passes the gate. -/
inductive Reachable (sys : System S E) (V : Set S) (s₀ : S) : S → Prop
  | init : Reachable sys V s₀ s₀
  | step {s : S} {e : E} :
      Reachable sys V s₀ s → e ∈ Gate sys V s → Reachable sys V s₀ (sys.T s e)

/-- **Narrow Gate Safety Theorem.** Every gated-reachable state is viable.

Note what is absent: no controlled-invariance hypothesis, no soundness
assumption on world-state verification, no bound on the horizon. One-step
containment suffices. This is why safety is not the property worth paying for. -/
theorem gate_preserves_viability (sys : System S E) (V : Set S) (s₀ : S)
    (h₀ : s₀ ∈ V) : ∀ s, Reachable sys V s₀ s → s ∈ V := by
  intro s hs
  induction hs with
  | init => exact h₀
  | step _ he _ => exact he.2

/-! ## Part 4 — why safety alone is worthless -/

/-- `V` is controlled-invariant: from every viable state some admissible effect
keeps the system viable. This is the viability-kernel condition. -/
def ControlledInvariant (sys : System S E) (V : Set S) : Prop :=
  ∀ s ∈ V, ∃ e ∈ sys.adm s, sys.T s e ∈ V

/-- Controlled invariance is exactly what makes the gate non-empty — it buys
liveness, which the safety theorem does not provide. -/
theorem invariant_gate_nonempty (sys : System S E) (V : Set S)
    (h : ControlledInvariant sys V) {s : S} (hs : s ∈ V) :
    (Gate sys V s).Nonempty := by
  obtain ⟨e, he, hTe⟩ := h s hs
  exact ⟨e, he, hTe⟩

/-! ### Witness: safety by paralysis

States `0 → 1 → 2`. `V = {0, 1}` is declared safe. From `1` the only effect goes
to `2 ∉ V`, so `V` is not controlled-invariant. The gate admits the step `0 → 1`
and then has nothing to admit at all. -/

def demoSys : System ℕ Unit where
  T := fun s _ => if s = 0 then 1 else 2
  adm := fun _ => Set.univ

def demoV : Set ℕ := {n | n ≤ 1}

theorem demo_not_controlled_invariant : ¬ ControlledInvariant demoSys demoV := by
  intro h
  obtain ⟨e, _, he⟩ := h 1 (by simp [demoV])
  simp [demoSys, demoV] at he

/-- The gate lets the system walk into the doomed state. -/
theorem demo_stuck_state_reachable : Reachable demoSys demoV 0 1 := by
  have hg : () ∈ Gate demoSys demoV 0 := ⟨Set.mem_univ _, by simp [demoSys, demoV]⟩
  have h := Reachable.step (Reachable.init) hg
  simpa [demoSys] using h

/-- And there the gate is empty: perfectly safe, completely inert. -/
theorem demo_gate_one_empty : Gate demoSys demoV 1 = ∅ := by
  ext e
  simp [Gate, demoSys, demoV]

/-- Safety still holds throughout — which is the point. A safety theorem that a
paralysed system satisfies is not evidence that the gate is well designed. -/
theorem demo_is_safe : ∀ s, Reachable demoSys demoV 0 s → s ∈ demoV :=
  gate_preserves_viability demoSys demoV 0 (by simp [demoV])

end MinorityProphetCore.NarrowGate
