# NOVELTY AUDIT — Phase I seed candidates

Ten seed candidates plus the Narrow Gate construction and its proposed safety
theorem, screened against prior art before any formalization effort is spent.
Screening precedes formalization because it is two orders of magnitude cheaper
and because it changes what is worth formalizing.

**Headline result: eight of ten seeds are established results in existing
literature.** That is the expected and correct outcome. The value of this
program is not in the individual laws — it is in the composition, in making the
laws *checkable* at inference-time rather than assumed, and in one correction to
the safety theorem that changes it from circular to provable.

Fields searched: object-capability security · viability theory · control barrier
functions · safe reinforcement learning · robust and distributionally-robust
optimization · formal verification and runtime monitoring · access control
policy composition · distributed systems and BFT · decision theory · causal
inference · survey statistics · type systems · zero-trust architecture · safety
engineering (IEC 61508, DO-178C) · game theory · mechanism design.

---

## Summary table

| # | Candidate | Verdict | Governing prior art |
|---|---|---|---|
| L1 | Non-expansion of authority, `M_{i+1} ⊆ M_i` | **KNOWN RESULT** → `NOVEL COMBINATION` when applied across inference steps | Capability attenuation (Miller 2006); POLA (Saltzer & Schroeder 1975) |
| L2 | Uncertainty contracts authority | **REJECTED as stated**; `USEFUL REFORMULATION` with tail risk | Robust optimization; CVaR; safe RL |
| L3 | Reversibility expands experiment | **KNOWN RESULT**, `QUALIFY` — proportionality unjustified | Safe exploration; attainable utility preservation; blast radius |
| L4 | Claims have no execution weight without evidence | **KNOWN RESULT** | Proper scoring rules; reputation systems; principal–agent theory |
| L5 | Count independent lineages, not repetitions | **MP INVARIANT** (already ours) with an unresolved transitivity defect | Effective sample size (Kish); clustered variance; entity resolution |
| L6 | Plausibility is not validation | **TRIVIAL as stated**; `USEFUL REFORMULATION` with a strength metric | Popper; mutation testing; adversarial validation |
| L7 | Contradictory authority collapses permission | **KNOWN RESULT** and **exploitable** — see attack | XACML deny-overrides; default-deny |
| L8 | No unbounded undertaking crosses the gate | **KNOWN RESULT** | Admission control; circuit breakers; constrained optimization |
| L9 | Measurement integrity precedes inference | **TRIVIAL but load-bearing** | Measurement error models; W3C PROV; chain of custody |
| L10 | Capability requires proportional accountability | **KNOWN RESULT**, `QUALIFY` — strict inequality too strong | IEC 61508 SILs; DO-178C DALs |
| G | Narrow Gate `G_t` as an intersection | **TRIVIAL** as a construction | Conjunctive policy evaluation; shielding |
| T | Narrow Gate Safety Theorem | **PROVABLE — and weaker than it looks.** Machine-checked | Viability theory (Aubin); controlled invariance; CBFs |

---

## The two findings that matter

Everything above is screening. Two results change the design.

### Finding 1 — The safety theorem is provable, and that is the bad news

*This section was rewritten after formalization. The first draft asserted the
theorem was circular. It is not; the Lean development proved something sharper
and less comfortable. Recording the correction here rather than silently
replacing it, per `PROGRAM.md`.*

The candidate theorem has two conjuncts.

**Conjunct 1 — no executed effect exceeds surviving authority.** True by
construction, and not a theorem. `e ∈ ⋂M_i` is checked at admission; concluding
it afterwards restates the check. Retained as
`NarrowGate.surviving_eq_last`, a simplification lemma. Under an authority
chain, the intersection in the definition of `G_t` carries no information the
chain does not already give — so that part of the Gate formula is decoration.

**Conjunct 2 — the system does not leave the viability region.** This *is*
provable — and it needs strictly fewer hypotheses than the brief supplies. It
requires no controlled-invariance assumption, no soundness assumption on
world-state verification, and no horizon bound. One-step containment plus
induction is the entire proof:

> `NarrowGate.gate_preserves_viability` — if `s₀ ∈ V` and every step passes a
> gate that refuses any `e` with `T(s,e) ∉ V`, then every reachable state is in
> `V`. Two lines. Depends on no axioms whatsoever.

**And that is precisely the problem.** A theorem that cheap is satisfied by a
gate that admits nothing. Safety was never the scarce property.

The machine-checked witness (`NarrowGate.demoSys`) makes it concrete. Three
states `0 → 1 → 2`, declared-safe set `V = {0,1}`. The gate happily admits
`0 → 1`, and then at state `1` every available effect leads outside `V`, so
`Gate = ∅` (`demo_gate_one_empty`). The system never leaves `V`
(`demo_is_safe`) and never acts again. It satisfies the Narrow Gate Safety
Theorem perfectly, by paralysis.

**What controlled invariance actually buys is liveness, not safety.**

> `NarrowGate.invariant_gate_nonempty` — if `V` is controlled-invariant
> (`∀ s ∈ V, ∃ e admissible with T(s,e) ∈ V`), the gate is non-empty at every
> viable state.

So the design requirement is real but differently motivated than the brief
assumes: the gate must be built against the **viability kernel**

> `Viab(V) = { s ∈ V : some admissible action sequence keeps the system in V
> forever }`

not against the declared safe set `V`. The difference is the doomed states — in
`V`, passing every one-step check, already lost. Computing or
under-approximating `Viab(V)` is the expensive engineering, and it should be
surfaced to the owner as a cost before anything is promised. Under-approximation
is sound (refuses more than necessary). Over-approximation is not.

**Consequence for the success criterion.** `FalseDenyRate` is not a secondary
metric to be reported alongside the safety metrics. It is the only thing
standing between this design and a system that scores perfectly by refusing to
act. That is now a machine-checked statement rather than an intuition.

### Finding 2 — Monotone contraction terminates the system

`M_{i+1} ⊆ M_i` over an unbounded sequence forces `M_n` to a fixed point, and
every practical contraction is strict somewhere. A long-running agent under L1
as literally stated converges to `M_∞ = ∅` and becomes inert. Perfectly safe,
entirely useless — and it will score flawlessly on `UnauthorizedEffectRate`
while `FalseDenyRate` goes to 1.

L1 is sound **within a single derivation chain** — one mandate, expanded into
plans, delegations and tool calls, where no step may invent authority the
mandate did not contain. It is false **across mandate epochs**, where new
authority legitimately enters from outside.

The law therefore requires an epoch index. Authority contracts monotonically
within an epoch; a new epoch begins only at an authenticated mandate boundary,
which is exactly where `E2` from `ASSAYER.md` applies — authority may only be
renewed by something outside the control domain that spent it. Renewal from
inside is the bootstrap.

---

## Selected candidate detail

### L2 — Uncertainty contracts authority · **REJECTED as stated**

Stated as `∂AllowedMagnitude(e)/∂H(e) ≤ 0` with `H` an entropy.

**Counterexample.** Entropy is not monotone in danger. Consider two effects:

- `e₁`: outcome uniform over 256 harmless configurations. `H = 8` bits.
- `e₂`: outcome is "nothing happens" with probability `0.99`, "irrecoverable
  data loss" with probability `0.01`. `H ≈ 0.08` bits.

`H(e₁) ≫ H(e₂)`, so the law grants `e₂` the larger permitted magnitude. It has
the direction exactly backwards, because entropy measures *dispersion*, not
*downside*. Low-entropy catastrophic tails are the characteristic shape of real
disasters.

**Reformulation (`USEFUL REFORMULATION`).** Replace entropy with a coherent tail
risk measure over a loss functional — `CVaR_α(Loss(e))` — and require
`AllowedMagnitude` non-increasing in it. This is standard robust optimization,
so the reformulated law is `KNOWN RESULT` in content; its value to MP is that it
is checkable at the gate. The original entropy formulation must not ship.

### L5 — Independent lineages · **MP INVARIANT with an unresolved defect**

`N_eff = |Sources/∼|` is already MP's core and already machine-checked in Lean.
Prior art in statistics is old and solid (design effect, clustered variance).

**The defect is that `∼` is asserted to be an equivalence relation and real
provenance similarity is not transitive.** Source A shares a passage with B; B
shares a different passage with C; A and C share nothing. Transitive closure
merges all three into one class and drives `N_eff` toward 1 across any
sufficiently connected corpus — the aggregator becomes maximally conservative
and useless, which is the `FalseDenyRate` failure again.

This is the known hard problem in entity resolution, and it was the same gap as
ledger `U1`. **Resolved 2026-09-07, and the answer is neither of the two options
this paragraph offered.** `canon/U1-PROXIMATE-ROOTS.md` declines to make `∼` an
equivalence relation precisely because transitive closure drives `N_eff` toward 1
across a connected corpus, and declines to make it a clustering because the
result would depend on an algorithm rather than on evidence. It declares a *cut*:
an intervening independent re-derivation breaks the chain, graded by how far back
toward the world the re-derivation went (`canon/proximity.py`), and evaluated
relative to a named class of error rather than in the abstract.

What still requires an owner signature, published in advance under `A3`, is the
assignment of particular real procedures to rungs — not the relation itself.

### L7 — Contradictory authority collapses permission · **exploitable**

Deny-on-unresolved-conflict is standard (XACML deny-overrides) and correct as a
default. But the law as stated hands an adversary a denial-of-service primitive:
**anyone who can introduce a mandate can manufacture a conflict and halt the
system.** If mandate `M_B: ¬e` can be injected cheaply, `Execute(e) = 0` follows
for any `e` an attacker chooses.

The law survives only with an authenticity precondition: conflict triggers
denial only between mandates that are *individually authenticated and
in-scope*. Unauthenticated mandates are not counterparties to a conflict; they
are discarded before conflict resolution runs. Without that clause the law is a
vulnerability rather than a control.

### L6 — Plausibility is not validation · **TRIVIAL as stated**

`Unchallenged(H) ⇏ Validated(H)` is a non-implication and therefore carries no
constraint — nothing is forbidden by it. To do work it needs a positive form
with a measurable strength, e.g. a mutation-testing analogue: a challenge set
`C` validates `H` to the degree that `C` distinguishes `H` from its
perturbations. That is `KNOWN RESULT` (mutation adequacy) but produces an
implementable number, which the non-implication does not.

---

## What this audit concluded

- Nothing here should be published as an MP discovery. Eight seeds are known
  results and two are defective as stated.
- The composition is defensible and probably new: capability attenuation applied
  across *inference* steps — where, unlike object-capability systems, nothing
  structurally prevents a model from inventing authority, because authority is
  carried as text rather than as an unforgeable reference. Making
  `M_{i+1} ⊆ M_i` *checkable* at that boundary is the contribution.
- One correction (viability kernel vs declared safe set) turns the central
  theorem from circular into provable, and imposes a real engineering cost that
  should be surfaced to the owner before anything is promised.
