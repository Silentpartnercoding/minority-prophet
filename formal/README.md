# Formal model

Start with these files:

1. [`CLAIM-SCOPE.md`](CLAIM-SCOPE.md) — what the proofs establish and do not
   establish.
2. [`PROOFS.md`](PROOFS.md) — readable statements, assumptions, corrections,
   and reproduction guidance.
3. [`THEOREM-LEDGER.json`](THEOREM-LEDGER.json) — machine-readable theorem
   status.
4. [`lean/`](lean/) — pinned Lean 4 source and Mathlib dependency.

[`COUNTEREXAMPLES.md`](COUNTEREXAMPLES.md) preserves failed formulations and
boundary cases. [`DEFINITION-AUDIT.md`](DEFINITION-AUDIT.md) and
[`EXTENSION-SOCKETS.md`](EXTENSION-SOCKETS.md) cover definition and extension
work. `MinorityProphetV2.lean` is preserved historical source; the current
compiled package is under `lean/`.

Formal compilation proves narrow statements under explicit assumptions. It
does not certify real root identity, causal independence, or deployment safety.
