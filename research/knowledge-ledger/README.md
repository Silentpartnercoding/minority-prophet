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

## What the reference receipt preserves

The v0.2 reference evaluator exists because a knowledge record must be able to
carry doubt, not merely a confident conclusion. Its receipt keeps these fields
together:

- declared search coverage and unsearched locations;
- supporting and opposing evidence roots, with repeated records collapsed;
- the root margin;
- `flipBudget`, measured in units of net per-side root gain (`p0 - p1`);
- `conversionsToReverse`, measured in modeled side-conversion actions;
- unattributed records and declared shared dependencies;
- side-separation status and the reason for abstention.

`flipBudget` and `conversionsToReverse` are deliberately reported together.
They price different modeled changes: one side conversion moves a root off one
side and onto the other, changing the margin by two units. Neither number is a
count of real-world incidents, compromised keys, or attackers.

The receipt therefore preserves not only what the evaluator concluded, but how
close the declared evidence state is to losing that conclusion and which
unknowns remain. It does not prove that a root is true or independent, establish
that discovery was complete beyond the declared search space, or authorize an
action.

## Current milestone

`reference-conformance-001` is a local conformance artifact. It demonstrates that four
searched locations out of five produce `not_established`, even when several
reports agree. It is not a cross-system result and is not evidence
that the method improves real-world truth recovery.
