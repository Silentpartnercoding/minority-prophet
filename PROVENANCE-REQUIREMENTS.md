# PROVENANCE-REQUIREMENTS.md — what provenance must (and need not) guarantee

Status: v2 consolidation. Supersedes the implicit "full lineage" assumption in
FOUNDATIONS.md v1. Derived from Theorems 1–4 (formal/PROOFS.md, exhaustively
machine-verified) and Experiments 001–006 (001–002 canonical; 003–006 replica,
pending canonical re-run). This file is the single source of truth for what
any provider-neutral attestation layer must provide to the aggregation layer.

## The requirement stack

R1. ROOT INTEGRITY (hard requirement — attestation's job)
  Guarantee: evidence roots cannot be manufactured or destroyed. No forged
  "original observations"; no laundering a copy into an apparent root.
  Threat excluded: sybil root-manufacturing (Douceur 2002 is the impossibility
  this layer escapes by making identity/origin costly or cryptographic).
  Measurement: root-set accuracy.
  Theorem dependency: T1 and T4 both assume the root set is preserved.

R2. SIDE-SEPARATION (hard requirement — the surprising minimum)
  Guarantee: a claim can never be attributed to a root of the opposing
  assertion. Camps must not blend.
  Everything else about lineage may be arbitrarily wrong (T1 Immunity:
  side-preserving, root-preserving rewiring cannot change any verdict —
  verified over 5,912 worlds / 121,944 rewirings / 100k randomized, 0
  violations).
  Measurement: side-confusion (must be 0 for the immunity guarantee);
  library diagnostic `immunity_applicable`.

R3. MARGIN SUFFICIENCY (system-level requirement — the defender's lever)
  Guarantee: maintain enough attested independent roots that the honest
  margin exceeds the adversary's forgery capacity. T4 (margin flip
  condition): a verdict flips only if net cross-side phantom root flow ≥ the
  true side-count margin. The attack budget IS the margin.
  Measurement: `flip_budget` (per-verdict margin, first-class output).
  Consequence (H5 REJECTED, preregistered): no margin-independent scalar
  corruption statistic predicts failure; defense planning must be
  margin-relative.

## Explicitly NOT required (demotions — the week's main economic result)

- Accurate who-copied-whom edges. (T1)
- Full lineage trees / high attribution accuracy. (Mode C: attribution
  1.0 → 0.59 with accuracy ≥ 0.98 throughout.)
- Copy-count knowledge. (T2: duplicates net to zero.)
- Root-set OVERLAP as a quality metric — demoted after EXP004 showed it blind
  to attribution damage; superseded by side-confusion and margin metrics.

## Field/metric registry added this cycle

  attribution accuracy      (per-claim true-root match; diagnostic only)
  side_confusion            (R2 gate)
  signed side_confusion     (directional diagnostic; not sufficient — H5)
  flip_budget / margin      (R3 gate; verdict output)
  immunity_applicable       (R2 precondition check; verdict output)
  edge_confidence, inferred (lineage schema extensions, backward compatible)

## Known limits of the current definition

- Binary assertions only; multi-proposition and continuous claims unformalized.
- "Independence" is modeled as distinct roots; graded independence (partially
  correlated observers) is future work.
- R1's cost mechanism (what makes roots expensive to forge) is imported from
  the attestation layer and is outside these theorems' scope — the theorems
  quietly become vacuous if R1 fails. State this in every application.
- Canonical replication of EXP003–006 findings is pending (see HANDOFF.md).

One-line summary: provenance does not need to reconstruct the family tree;
it needs unforgeable origins (R1), unblended camps (R2), and a protected
lead (R3) — in that order, and nothing more.
