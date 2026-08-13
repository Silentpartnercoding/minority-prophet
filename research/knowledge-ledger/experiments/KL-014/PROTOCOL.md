# KL-014 — protocol

Hypothesis: **HRI-1**, root identity under shared observation.
Collection rule: `preregistration-v0.1.json`, frozen at the commit recorded in
`PROTOCOL-COMMIT-v0.1.txt`.

These two filenames are load-bearing, not stylistic: `scripts/check_registration_chain.py`
pairs `PROTOCOL-COMMIT-vX.Y.txt` with `preregistration-vX.Y.json` and verifies
nothing else. KL-012's `COLLECTION-SPEC`/`COLLECTION-COMMIT` pair is outside that
pattern and is therefore unverified by the control — its freeze is asserted in
prose rather than checked. KL-014 uses the checked names so that "frozen before
any data" is a machine-verified property of history.

Not listed in `EXPERIMENT-REGISTRY.json`: that registry is the frozen seeded
program KL-000…KL-011, pinned by
`tests/test_knowledge_ledger_program.py::test_every_experiment_is_seeded_with_required_fields`.
KL-012 onward are registered by their own frozen collection rule, as here.

This file describes the human procedure. Everything decidable mechanically is in
the spec; what is here is the part a script cannot enforce, which is exactly the
part most able to bias the result.

---

## The question in one paragraph

`margin` counts distinct evidence roots. `mp-root-v1` makes a root identity
unforgeable by binding the authenticated issuer into the digest. Unforgeable and
*meaningful* are different properties: because issuer is in the hash, two
issuers reporting the same event necessarily produce two identities. If that
happens routinely in real reporting, every `flip_budget` the system publishes is
inflated by that ratio, and nothing in the current stack would notice — no key
is compromised, no quota exceeded, no signature invalid. KL-014 measures the
ratio.

## Order of operations — this order is the experiment

1. **Freeze the rule.** Commit the preregistration. Record its commit SHA in
   `PROTOCOL-COMMIT-v0.1.txt`. Nothing below starts before this.
2. **Sensitivity check the instrument.** Run the identity computation over
   constructed cases whose observation count is known by construction. It must
   recover the constructed value exactly. This is a check on the instrument and
   is never reported as a finding.
3. **Declare the corpus.** Source set and proposition list written into the
   manifest. Not extended afterwards, for any reason, including "the sample was
   thin".
4. **Compute and seal identities.** `mp-root-v1` for every claim, via the
   shipped implementation. Sealed — hashed and committed — before step 5, so the
   labelling cannot be reconciled to them after the fact.
5. **Label, blinded.** Three labellers, independently. See step "Labelling"
   below.
6. **Check inter-rater agreement.** Krippendorff alpha ≥ 0.67. If it is below,
   **stop and report that**. Do not adjust the rule, the labellers, or the
   corpus.
7. **Only now** compute the split factor and merge rate.
8. **Apply the registered decision rule.** It is in the spec. It was written
   before the number existed. Apply it as written.

Steps 4 and 5 are inverted at your peril: identities visible during labelling
turns a measurement into a confirmation.

## Labelling

Labellers see, per claim: the claim text, its cited sources, and its timestamp.

Labellers do **not** see: any `mp-root-v1` identity, any issuer digest, any root
count, any other labeller's work, or the hypothesis being tested.

The judgement is a partition of the claims for one proposition into groups.
Two claims go in the same group when neither could have been produced without
the other's source, or without a common source they both cite.

Worked guidance:

- Two outlets both citing the same wire report → **same** observation.
- Two outlets citing each other, one clearly downstream → **same**.
- Two field reporters at the same event, filing separately → **different**.
  They witnessed independently; the correlation is in the world, not the
  evidence chain.
- Two analyses of the same public dataset → **same** observation, different
  interpretation. The evidence is the dataset.
- Cannot tell → mark **unresolved**. Do not guess. Unresolved items are reported
  in a declared sensitivity band; they are not dropped, because dropping the
  hard cases is how a split factor gets talked down to 1.0.

## What a negative result looks like, and why it is welcome

If the median split factor comes back at or near 1.0, that is the strongest
statement this project could truthfully make about its independence claim —
stronger than any proof, because it is the one link in the chain no proof can
reach. It should be published as prominently as a positive finding.

If it comes back materially above 1.0, the correction is arithmetic and the
decision rule is already written. The failure mode to guard against is not a bad
number; it is a number quietly reframed as a corpus limitation after the fact.

If inter-rater agreement fails, the honest report is "we could not establish the
ground truth on this corpus", and `flip_budget` keeps its narrower description.
That is a real outcome of a real run.

## Boundaries

- This measures **independence**, not truth. A split factor of 1.0 says nothing
  about whether any claim is correct.
- This is not HVI-1. HVI-1 asks whether one controller can inflate mass by
  splitting identities — an adversary. HRI-1 asks what happens with no adversary
  at all, when honest issuers share an upstream source. A control-domain
  collapse correctly counts five separate organisations as five, and is still
  wrong for evidence purposes if all five read one wire.
- This does not measure whether any deployment uses `RootRegistry`. That is a
  deployment property, carried as `deployment_status` on LEDGER-H2.
