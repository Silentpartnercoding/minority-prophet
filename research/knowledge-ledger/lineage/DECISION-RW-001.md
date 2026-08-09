# RW-001 — the identity is not a rewiring

**Owner decision, 2026-08-09.** Recorded in the style of A1, A2 and R5.2: decided,
not derived. Both readings were defensible and the alternative is closed rather
than preserved-and-undecided, because an undecided definition is what has cost
this experiment a round each time.

## The decision

A **rewiring** of a world `W` is a world `W'` with the same claim count, the same
side for every index, and a `parentIndex` vector **differing from `W`'s in at
least one position**. The identity — `W'` equal to `W` — is **not** a rewiring.

This is v0.3's registered definition, now ratified rather than inherited.

## What it costs, stated plainly

`FINDING-BL051.md` and `REGISTRATION-v0.3.md` cite **121,944** as blind
confirmation that this programme read Theorem 1 correctly, on the grounds that it
"matches the paper's own published exhaustive check exactly".

**Under RW-001 that citation is wrong**, and the pre-flight's T5 trap fires on it.
The registered definition yields **116,032**. The difference is exactly 5,912 —
one identity per side-consistent world — because the paper's count includes the
identity and RW-001 excludes it.

The independent implementation confirmed this is the only way to reach the paper's
figure: of the eight combinations of {identity in, out} × {which worlds must be
side-consistent}, exactly one produces 121,944, and it is identity **included**.

## What survives, and it is the part that mattered

The evidence that this programme read Theorem 1 correctly does **not** rest on
121,944. It rests on the paper's own words — *"preserves the **root set**"* —
which is the weak reading, against the strictly stronger reading v0.1 and v0.2
tested and which is an identity under this schema's `S_a`. That argument is
unaffected.

What is lost is a numerical coincidence being used as corroboration. The correct
statement is not "our count matches the paper's" but:

> Our count is the paper's count minus one identity rewiring per side-consistent
> world, because RW-001 excludes what the paper's count includes. `116,032 +
> 5,912 = 121,944.`

That is a reconciliation, not an agreement, and it should never again be written
as one.

## Why exclude, given the cost

Including the identity would buy back the citation and nothing else. A rewiring
that rewires nothing tests nothing: it is guaranteed to preserve the verdict by
the reflexivity of equality, so it inflates every denominator by one per world
while contributing no information. This programme has spent two rounds removing
tests whose outcome is fixed by construction; adding 5,912 of them to reclaim a
round number would be the same error, chosen deliberately.

## Consequences

- `REGISTRATION-v0.3.md` is frozen and keeps the defective sentence. This file
  supersedes it, and v0.4 will carry RW-001's definition with the reconciliation
  stated rather than the agreement claimed.
- `FINDING-BL051.md` is corrected in place.
- The pre-flight's T5 trap must pass on the corrected text. If it does not, the
  correction is wrong rather than the trap.
