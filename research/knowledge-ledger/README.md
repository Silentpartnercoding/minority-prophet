# Knowledge-ledger research program

Status: **seeded research program.** Only artifacts listed as completed in the
canonical registry may be described as results. Plans, fixtures, expected
outputs, simulations, and failed runs are not results.

## Start here

1. [`RESEARCH-METHOD.md`](RESEARCH-METHOD.md) defines the public method and claim rules.
2. [`EXPERIMENT-REGISTRY.json`](EXPERIMENT-REGISTRY.json) is the machine-readable experiment registry.
3. [`experiments/`](experiments/) contains versioned protocols, statuses, and results.
4. [`interoperability/`](interoperability/) contains reference conformance fixtures and cross-system acceptance criteria.
5. `knowledge_ledger.transaction` is a deliberately small reference evaluator.

## Program invariants

- Copies never create independent evidence.
- Search coverage and evidential independence are separate quantities.
- Incomplete coverage never becomes proof of absence.
- One root cannot count on opposing sides.
- Root-flow units and adversary actions are reported separately.
- Uncertainty widens or produces abstention; it never creates permission.
- No safety-critical experiment controls a live medical, legal, governmental,
  financial, or autonomous decision.
- Every claimed result is reproducible from immutable inputs, code, environment,
  and a recorded commit.

## Current milestone

`reference-conformance-001` is a local conformance artifact. It demonstrates that four
searched locations out of five produce `not_established`, even when several
reports agree. It is not a cross-system result and is not evidence
that the method improves real-world truth recovery.
