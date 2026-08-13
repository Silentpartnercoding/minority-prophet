# Hard Gauntlet v1 — invalidation record

Date: 2026-08-10

Status: invalid for AI-capability and Minority Prophet comparisons. Raw records
remain preserved so the error cannot be erased or silently reinterpreted.

## Why it is invalid

1. A, B, and C did not receive identical evidence bytes. The run measured the
   value of added labels and summaries, not contestant capability.
2. C used `mp.js`, a simplified JavaScript root summary, rather than the pinned
   canonical Python implementation.
3. B received normalized provenance fields that A did not receive.
4. Several scenarios required freshness, revocation, authority, shared-control,
   or observation judgments outside the root-counting competition being tested.
5. Metadata values leaked semantic hints such as truth/falsehood-oriented domain
   labels.

## What remains usable

- provider and structured-output plumbing diagnostics;
- the two recorded Sonnet interface failures;
- the lesson that condition-specific information invalidates a capability
  comparison;
- the immutable audit trail demonstrating why a replacement was required.

No score, delta, or conclusion from this run may be promoted as evidence for the
replacement capability tournament.
