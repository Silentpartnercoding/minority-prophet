# GATE-01 — `origin` is documented as collapsing roots and never collapses anything

**Identifier:** GATE-01
**Classification:** DOCUMENTATION GAP (with a concrete misuse path)
**Severity:** medium — no shipped code is wrong; an integrator relying on the
documented behaviour manufactures independence, which is the threat this package
names as central
**Affected commit:** minority-prophet-gate `88a9f471f79e`
**Type:** documentation / claim scope

## Claim affected

`minority_prophet/adapter_acp.py`, the envelope contract:

    "origin": "scan-7f2c",        # root id this claim descends from

and the security model, ten lines below:

    Default-derived rule: a claim WITHOUT a verified fresh-root attestation
    is treated as an echo. If it names a parent/origin, it collapses into
    that family; ...

Also `SECURITY.md`: *"The central threat is manufactured independence. Different
names, keys, services, signatures, or network locations do not prove independent
control."*

## What the code does

Every executable use of `origin` in the package, enumerated:

    adapter_acp.py:115-124   _freshness_policy  — classify for freshness decay
    reconcile.py:49-51       _freshness_policy  — same

`aggregator.py` never mentions `origin`. No code path uses it for root identity,
deduplication, or collapse. **Collapse is implemented only via
`attest.derived_from`**, and only when the verifier returns status `derived`.

So the field documented as "root id this claim descends from" does not identify a
root, and the documented collapse-by-origin does not exist in shipped code.

## Minimal reproduction

    tie 1v1                                  -> escalate
    tie + 50 PROPERLY DERIVED copies         -> escalate   (derived_from works)
    tie + 50 roots SHARING origin "safe-0"   -> proceed    (origin does nothing)

Fifty claims that all declare `origin: "safe-0"`, with distinct `claim_id`s and no
`derived_from`, are counted as fifty independent roots and convert a tie — which
correctly escalates — into a proceed.

Reproduction in `reproductions/gate-01.py`.

## Expected and observed

Expected, from the docstring: claims naming the same origin collapse into one
family and contribute one root.
Observed: they contribute fifty roots.

## Why this is not simply a bug

The security model in the same docstring says **"THE GUARANTEE IS ONLY AS STRONG
AS THE VERIFIER"**, and the only shipped verifiers are `TrustAllVerifier`
(*"Provides NO security"*, testing only) and `CallbackVerifier` (bring your own).
Collapse is delegated to the verifier by design.

That is defensible. The gap is that **neither shipped verifier implements the
documented collapse**, and the docstring states it as the package's behaviour
rather than as a requirement the integrator must satisfy. A reader who populates
`origin` faithfully, omits `derived_from`, and supplies a verifier that
authenticates signatures but does not deduplicate by origin gets exactly the
manufactured independence `SECURITY.md` warns about — while believing they
declared shared provenance.

## Smallest fix

Either wording or code, not both:

1. Change the contract comment to say `origin` is used **only** for freshness
   classification, and that collapse requires `derived_from`; and restate the
   default-derived rule as a requirement on the verifier rather than as adapter
   behaviour. **or**
2. Collapse same-`origin` root-status claims in the adapter, which changes
   behaviour and needs its own registration.

## Smallest regression test

    def test_same_origin_roots_do_not_multiply_independence():
        tie = [root("s0","safe-0","SAFE"), root("u0","unsafe-0","UNSAFE")]
        many = tie + [root(f"x{i}","safe-0","SAFE") for i in range(50)]
        assert decide(many).action == decide(tie).action

This test fails today. Whether it *should* pass is the owner's call — it encodes
option 2.

## Corrections to this finding's own working

Two earlier attempts were invalid and are recorded rather than deleted:

1. I first tested lineage with a top-level `parent` key I invented. The real
   field is `attest.derived_from`. The "counterexample to T2" that produced was
   my error, not a defect. **T2 copy invariance holds**: 50 properly derived
   copies leave the verdict unchanged.
2. I ran the first pass entirely under `TrustAllVerifier` without registering
   that its own docstring says it provides no security. Results obtained under a
   test double cannot by themselves establish a weakness in the library.

The finding above survives both corrections because it is about what the shipped
code does with `origin` in every path, which does not depend on the verifier.
