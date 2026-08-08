# Methodology notes — RUN-20260807-2

Continuing RUN-20260807-1's M1–M6, which remain in force. These were paid for
by this run's findings.

## M7 — Every output field is invariant-constrained, fixture-pinned, or declared unspecified

Two implementations passed all ten invariants over the identical 176,120-world
enumeration while disagreeing on the `conclusion` of 22,440 receipt-producing
worlds (SPEC-101). Nothing in the test surface — fixtures, enumeration,
randomization, adversarial suite, baselines — could see the divergence,
because no invariant constrained the field. A conformance suite certifies
exactly what its invariants and pinned fixtures constrain, and silently
nothing else. Rule: for every field a downstream consumer reads, the
registration either states an invariant over it, pins it in a fixture, or
declares it unspecified in so many words. An undeclared-unspecified field is
a divergence not yet observed.

## M8 — "Reproduction" and "replication" are different words and the record uses the right one

The exhaustive phases ran the same worlds (independently derived, count- and
decomposition-verified) and may be compared value-for-value: reproduction.
The randomized phases ran different worlds from the same declared bounds,
because a frozen seed without a frozen draw schedule freezes nothing across
implementations (F11, SPEC-102): replication, comparable only in shape.
Calling a replication a reproduction overstates the evidence in exactly the
direction this program exists to prevent. The record says which one it means,
every time.

## M9 — Owner decisions are labelled as decisions, with the road not taken preserved

R1 could defensibly have gone the other way, and the registration says so:
`decidedBy: owner`, `ownerDecision: true`, the contrary reading preserved
verbatim in the imported FINDINGS.md, and the surface of the decision
quantified (16,320 ties directly, 6,120 minorities a fortiori). A
specification that presents choices as derivations cannot be re-litigated
honestly when the choice turns out wrong, because the record no longer shows
a choice was made. Derived repairs (R2–R4) are labelled with what they were
derived from and the evidence both implementations already conformed.

## M10 — "This change changes nothing" is a falsifiable claim, registered before the run that tests it

The documentation-only claim for R1–R4 was registered as an exact-equality
prediction table (`expectedIdenticalToRun1`) with a halt-and-report condition,
then tested by re-running everything. Asserting it from code inspection would
have been cheaper and worthless: inspection is how the vacuous-antecedent hole
in I2 survived v1.0.0. The re-run costs ~90 seconds; the claim it buys —
every number identical across 1,176,120 evaluated worlds and four ablations —
is not obtainable any other way.

## M11 — A registration and its report use one vocabulary

The registrations spell two baseline ids one way, the runner's report spells
them another (NAM-101), and this run's first comparison script crashed on the
mismatch before comparing a single number. It failed loudly; the same split
could as easily make a check compare nothing and pass. Identifiers that name
the same object in a registration and in the artifact verifying it must be
byte-equal, or the mapping must itself be committed and tested — never held
in a script's head.

## M12 — Imported evidence is copied with digests; the original is never edited, even to fix it

The independent implementation's artifacts entered the repository by copy,
with SHA-256 digests binding copies to originals recorded at import time, and
the originals untouched — including their errors (the disclosure note
understating its own leak). Correcting an imported document in place would
destroy the very property (someone else wrote this, before we looked) that
makes it evidence. Corrections live beside the copy, attributed to this run.
