# LIN-000 v0.3.1 — two defects in v0.3's conformance clause

Registered by RUN-20260809-1. Amends **only** the generator-conformance phase and
its invalidation condition. Everything else in `REGISTRATION-v0.3.md` — the T1
readings, L1, the ablations, the schema change, the traceability — stands
unchanged and is not restated here. v0.3 is preserved.

Both defects were found by running the v0.3 reference against v0.3 within an hour
of registering it. Neither was found by review.

## E1 — two stated rejection regions are wrong

v0.3 says the three large moduli have `2**32 mod n` equal to 1,431,655,765,
1,717,986,164 and 1,431,655,763. Computed:

| modulus | v0.3 states | actual | actual rejection rate |
|---|---|---|---|
| 2863311531 | 1,431,655,765 | 1,431,655,765 | 32.7% |
| 2576980378 | 1,717,986,164 | **1,717,986,918** | 40.0% |
| 1717986919 | 1,431,655,763 | **858,993,458** | 19.6% |

The moduli are correct and the clause's purpose is met — the rejection rule is
exercised at 19.6–40.0% instead of never. Only the arithmetic in the prose was
wrong. The stated figure "roughly 33%" for the third modulus should read roughly
20%.

Arithmetic in a registration is a normative statement, so this is an erratum
rather than a typo.

## E2 — the invalidation condition fires on correct behaviour

v0.3 invalidates a run on *"any conformance modulus whose word count equals 1,000
for a modulus with a non-empty rejection region."*

`uniform_below(20)` has a rejection region of 16 values out of 2³² — a rejection
probability of about 3.7 × 10⁻⁹. Over 1,000 draws the expected number of
rejections is 0.0000037. **Observing zero is the correct outcome**, and the
condition invalidates every honest run. `uniform_below(10)` is the same at
1.4 × 10⁻⁹.

Run against the v0.3 reference, the condition fired on both, on a run in which
every substantive test passed.

This is the defect BL-049 repaired in the registration chain — a control that is
red on a correct system — committed by the same author in a registration written
hours later. Recorded rather than smoothed over, because a control that cannot
distinguish correct from incorrect trains its readers to ignore it.

**Replacement condition.** A run is invalid if any modulus whose rejection
probability exceeds **1 in 1,000** consumes exactly 1,000 words. Equivalently:
`2**32 mod n > 2**32 / 1000`. Under the registered list that is exactly the three
large moduli, and the small ones are exempt by construction rather than by
exception.

The small moduli remain in the vector. Their word counts are still reported and
are still evidence — that `uniform_below(1)` consumes one word rather than zero
is precisely the degenerate case v0.2 was written to pin, and it is observable in
the count.

## Status of the v0.3 reference run

Under v0.3's condition as written, that run is **invalid**. The registration
governs even when the registration is wrong; reinterpreting a MUST clause to fit
a result is the failure this programme exists to refuse.

The run is therefore reported as invalid-as-registered, its numbers are recorded
as provisional, and it is re-run under v0.3.1. No result is carried across on the
strength of "the condition obviously meant something else."
