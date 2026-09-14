# Safety Was Never the Scarce Property: Liveness Conditions for Narrow Admission Gates

**Status: DRAFT v0.1. Not submitted. Not deposited. No DOI.**
Drafted 2026-09-14. Third companion to *The Minority Prophet Property*
(archival record, all versions: `10.5281/zenodo.21965712`). Recorded in
`papers/ERRATA.md` under `[E9]`.

---

## Abstract

A narrow admission gate admits only effects whose one-step consequence remains
inside a declared-safe set. This paper proves the safety theorem such a gate is
usually built to satisfy, and then shows the theorem is **not worth what it
appears to be worth**: safety needs no invariance hypothesis, follows from
one-step containment by a two-line induction, and is achievable in full by a
gate that admits nothing at all.

The witness is constructed and machine-checked. A system is exhibited that is
**perfectly safe and completely paralysed** — the gate walks it into a state
where every available effect leaves the safe set, the gate empties, and the
system never acts again. It never leaves the safe set either.

The scarce property is therefore **liveness**, and the hypothesis that buys it is
**controlled invariance**. That hypothesis is expensive, and the paper states the
direction in which it must be approximated and why the other direction is
unsound.

A fourth result settles a separate objection: authority that only ever contracts,
strictly, reaches the empty set in finitely many steps. Monotone contraction is a
**termination argument, not a safety property**, unless authority may be renewed
at an authenticated mandate boundary.

All results in `formal/lean/MinorityProphetCore/NarrowGate.lean`. No `sorry`,
standard axioms only.

---

## 1. Safety is cheap

`gate_preserves_viability` — the safety theorem — holds, and it requires **no
invariance hypothesis whatsoever.** One-step containment suffices, by induction
over the reachability relation. Two lines.

That is the first result and it is the least interesting one, which is the point
of the paper. A theorem that cheap should provoke the question of what it is
failing to exclude.

## 2. What it fails to exclude

`demoSys` is a two-state system with declared-safe set `V = {n ≤ 1}`. It is
proved to be:

| | |
| --- | --- |
| `demo_is_safe` | every reachable state is in `V` |
| `demo_stuck_state_reachable` | the gate can reach state `1` |
| `demo_gate_one_empty` | at state `1` the gate admits **nothing** |
| `demo_not_controlled_invariant` | `V` is not controlled-invariant |

So the system satisfies the safety theorem perfectly and does nothing at all,
permanently. **A gate achieves perfect safety by admitting the empty set.**

The correction this forces is not that the safety theorem is unsound. It is
sound. The correction is that **safety was never the scarce property.** What is
scarce — and what a deployed gate is actually judged on — is the false-deny rate.

This is the same failure shape the aggregator has when it always abstains, and
the two were found independently in different halves of the system. An
abstaining aggregator satisfies every invariance theorem; an empty gate satisfies
every safety theorem. Neither is wrong. Both are useless, and in both cases the
proof obligation that excludes them had to be added afterwards.

## 3. The hypothesis that buys liveness back

`invariant_gate_nonempty`: if `V` is **controlled-invariant** — from every state
in `V` some available effect keeps the system in `V` — then the gate is non-empty
at every state in `V`. Safety and the ability to act coexist.

This is the real engineering requirement, and it is expensive: someone must
compute an under-approximation of the viability kernel.

**The direction of approximation is not a matter of taste.**
**Under-approximating is sound** — it refuses more than strictly necessary, which
costs availability. **Over-approximating is not** — it admits effects from states
that cannot be kept safe, which is precisely the failure the gate exists to
prevent. A gate whose safe set is optimistically estimated has the appearance of
the theorem without its content.

## 4. Contraction is termination, not safety

A separate objection, machine-checked. Where authority may only contract:

- `no_authority_creation` — no step introduces authority absent earlier
- `surviving_eq_last` — what survives `n` steps is exactly what the last step permits
- `strict_contraction_budget` — each strict contraction consumes finite budget
- `strict_contraction_inert` — **strict contraction reaches the empty set in finitely many steps**

So a chain that only ever narrows is not a stable safety posture. It is a clock.
Monotone contraction is a **termination argument**, and a system built on it is
inert after a bounded number of hops unless authority may be renewed at an
authenticated mandate boundary. That boundary is therefore not an optional
convenience in the architecture; it is what keeps the system from grinding to a
halt.

## 5. What is not claimed

**This says nothing about whether the declared-safe set is the right set.**
Every result is conditional on `V`. Choosing `V` is a modelling act performed
outside these theorems, and a gate that flawlessly preserves the wrong invariant
is flawlessly wrong.

**Controlled invariance is assumed, not computed.** The paper states the
requirement and the sound direction of approximation. Computing viability kernels
for realistic systems is a substantial separate problem and is not addressed
here.

**The demonstration system is deliberately minimal.** `demoSys` exists to prove
that the empty gate is reachable under the safety theorem's own hypotheses, not
to characterise how often it happens in practice. Frequency is an empirical
question this paper does not answer.

## 6. Relation to the rest of the programme

The two companions to this paper close gaps in the aggregator:
*Independence Without Equivalence* defines what a root is, and the responsiveness
converse stops the aggregator being satisfied by permanent abstention. This paper
does the corresponding work for the gate: it stops the gate being satisfied by
permanent refusal.

Taken together the three make the same point at three layers. **An instrument
that refuses everything satisfies every theorem stated as an upper bound**, and
the obligation that excludes it has to be stated separately, on purpose, in
advance.

## Availability

`formal/lean/MinorityProphetCore/NarrowGate.lean` — 10 results, no `sorry`,
standard axioms only, rebuilt on Lean v4.33.1.
