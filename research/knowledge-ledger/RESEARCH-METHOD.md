# Research method

Every registered experiment is incomplete until all fields below are committed before its
confirmatory run.

## Required preregistration

1. Identifier and immutable protocol version.
2. Exact research question.
3. Null and target hypotheses.
4. Population or generated-world distribution.
5. Search-space definition and enumeration method.
6. Evidence-root and shared-dependency definition.
7. Baselines and ablations.
8. Primary and secondary endpoints.
9. Effect size, uncertainty interval, and multiple-testing correction.
10. Success, failure, invalidation, and stop conditions.
11. Frozen seeds, splits, code commit, environment, and artifact paths.
12. Safety boundary and required human authorization.

## Required execution phases

`specification -> fixture -> exhaustive-small -> randomized -> adversarial ->
retrospective-real -> prospective-shadow -> bounded-pilot`

Later phases are forbidden until earlier gates pass. Safety-critical experiments
stop at retrospective or simulation phases unless separately authorized after
external review.

## Controls required everywhere

- head or record counting;
- source counting;
- evidence ledger without search coverage;
- search ledger without root collapse;
- dual ledger;
- a genuinely independent-evidence condition;
- a copied or shared-dependency condition;
- an incomplete-coverage condition;
- a counterexample in a searched location;
- a counterexample in an unsearched location.

## Claim discipline

- A generated fixture is a fixture, not a finding.
- Replaying the same bytes establishes reproducibility, not truth.
- A canonical synthetic result establishes only behavior in its frozen model.
- A retrospective association establishes neither causality nor prospective
  utility.
- A shadow deployment establishes workflow behavior without decision authority.
- Null, failed, incomplete, and adverse results remain visible.
- Worldwide novelty is not claimed until primary-source literature review is
  completed and recorded.

## Evidence package

Each run must write a manifest containing prompt digest, model and tool versions,
repository commit, dirty-worktree state, environment lock, start/end timestamps,
inputs, outputs, stdout/stderr, tests, hashes, and every human intervention.
Secrets and private data are referenced by opaque identifiers and never committed.

## Reproduction and independent verification

The implementation author may not be the sole checker. At minimum, a clean
environment must reproduce the artifact from the public protocol. That
establishes reproducibility, not independent control or evidence-root
independence.

Different models, prompts, keys, processes, branches, services, machines, or
separately written implementations may test portability and interoperability.
When they share an operator, orchestrator, evidence producer, or controlling
party, they remain one control domain and their agreement is internal
replication. A claim of independent verification requires supported external
provenance showing that the verifier cannot manufacture or promote the evidence
it verifies. Hidden common control remains outside what the record can prove.
