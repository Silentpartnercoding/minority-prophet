# TRC-101 — specification-to-paper traceability (registered rule)

Registered by RUN-20260807-9, after the audit that found the program's
internal provenance break: no KL-000 specification of any version cited
`papers/minority-prophet-v1.0.3.md`, and two rules recorded as open owner
decisions (R1, R5.2) were derivable from the paper's §3 — the 22,440-world
divergence was one implementation contradicting a published definition that
the specification package had disconnected.

## The rule

**Every normative rule in a KL specification either:**

**(a) cites the paper section or theorem it implements** — with the claim
quoted, not merely referenced, so drift between paper and specification is
visible at the citation site; **or**

**(b) declares itself specification-local, with a reason** — making the
rule an acknowledged choice rather than an invention wearing a derivation's
confidence.

A rule with neither is a traceability defect and fails the suite
(`tests/test_traceability.py`).

## The map

Each kernel protocol carries (or references) a `TRACEABILITY-<version>.json`
with **both directions**:

- `rules`: every normative rule → paper citation (verbatim quote + location)
  or specification-local declaration (reason). Partial derivations state
  both halves.
- `paperClaims`: every paper claim in the kernel's scope → the invariant,
  fixture, baseline, or ablation that exercises it, or an explicit
  `not-tested-by-KL-...` with the reason. A paper claim with no test is an
  untested claim and the map says so; silence is not permitted in either
  direction.

KL-000's map: `experiments/KL-000/TRACEABILITY-v1.3.0.json` (the first
instance; its summary counts are machine-checked against its own entries).

## Why the quote requirement

The break survived eight runs because references would have been checked and
prose was not written at all. A verbatim quote at the citation site makes
the paper's text travel with the rule, so a future paper edit or a future
specification edit turns the mismatch into a reviewable diff instead of a
silent divergence — the same mechanism as the packet enumeration (BRF-101)
and the schema field list (SCH-001 repair), applied to the derivation layer.
