# Correction — the R1.4 quota-denomination finding was wrong

`preregistration-v0.4.json` registered, under `securityConsequenceRegisteredNow`:

> If the unit is producer-declared (U-C), R1.4 currently bounds the wrong
> quantity. R1.4 caps roots per authenticated issuer per window. An issuer
> inside its quota can still inflate its evidential mass by declaring more units
> inside one artifact, because the quota counts issuance events rather than
> observation units.

**That is false.** Tested against the shipped `RootRegistry` on 2026-08-13.

The preregistration is not edited: it is pinned by `PROTOCOL-COMMIT-v0.4.txt`
and `scripts/check_registration_chain.py` verifies it byte-identical to that
commit. Retracting by rewriting the record would break the chain and would be
the retrofitting the whole apparatus exists to prevent. The claim stands in the
registration; this file is its correction.

## What is actually true

`RootRequest` carries an issuer-scoped `observation_id`, and `root_identity`
digests it. One issuance request mints exactly one root. So an artifact
declaring N separable observations needs **N distinct requests**, consuming
**N units of quota**.

Demonstrated with a quota of 2 per window:

```
sample-0: issued  mp-root-v1:2d88ce1d58a37fcbf06...
sample-1: issued  mp-root-v1:527e10bdd735903fd51...
sample-2: REFUSED -- issuer root budget exhausted for this window
sample-3: REFUSED -- issuer root budget exhausted for this window
```

**The quota already binds observation units, not artifacts.** The denomination
was correct before this audit raised it, and no change is warranted.

## Where the concern does survive, in weakened form

The quota bounds how many roots an issuer may *declare*. It cannot bound how
many *real observations* those declarations correspond to: an issuer may supply
125 distinct `observation_id`s for one real observation and stay inside a
sufficiently large quota.

That is not a denomination defect, and no quota design fixes it — it is the
verification problem (does this identifier correspond to a distinct real
observation?), which is ledger U1's territory and remains open. Conflating the
two is what produced the wrong claim: a correct mechanism was blamed for a gap
that sits one layer above it.

## What was done instead of a fix

A regression test, `test_quota_is_denominated_in_observation_units`, so the
property is *guarded* rather than re-argued the next time someone reads the
quota code and reaches the same wrong conclusion I did.
