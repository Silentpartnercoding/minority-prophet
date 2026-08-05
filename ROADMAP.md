# Roadmap

## v0.1 — foundational slice

- [x] Formal problem statement and explicit assumptions
- [x] Deterministic synthetic binary worlds with hidden ground truth
- [x] Majority and competence-weighted baselines
- [x] Evidence-lineage data model and JSON Schema
- [x] Truth accuracy, minority recovery, Brier score, abstention, and timing metrics
- [x] Landing page and synthetic-world observatory
- [x] Automated unit and server-render tests
- [x] Freeze the first exploratory semantic-aggregation report

Acceptance: a clean checkout runs all tests and reproduces a seeded report without network access.

## Immediate next experiment

Preregister a v0.2 ancestry-aware experiment before execution, adding hidden seeds, noisy observations, imperfect competence estimates, and external data. Retain these controls:

1. an independently grounded majority;
2. an ungrounded minority;
3. corrupted lineage metadata.

The method succeeds only if it improves copied-majority recovery without systematically favoring minorities or failing the controls.

## Out of scope for this release

Persistent identity, shared memory, belief propagation, global world models, multi-civilization simulation, production inference, and claims about higher-order cognition are not part of v0.1.
