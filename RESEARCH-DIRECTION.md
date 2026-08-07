# Research direction: evidence and search ledgers

Status: **research direction, not an established result or product claim.** The
formal results govern aggregation over declared evidence roots. They do not
prove that a collection process found every relevant observation.

## The boundary

> Minority Prophet reduces the lineage needed to evaluate evidence; it does not
> reduce the coverage needed to prove absence. Absence remains practical when
> the possible locations are finite, declared in advance, and exhaustively
> searchable.

This separates three operations that must not be collapsed:

1. **Discovery:** where the system looked and what portion of the declared
   search space it covered.
2. **Provenance:** which records represent genuinely distinct evidence roots,
   and which are copies or share dependencies.
3. **Decision:** what the resulting roots support, what could reverse the
   verdict, and when the system must abstain.

The current theorems reduce the provenance burden under R1–R3. They do not
reduce discovery coverage for a universal negative. One valid counterexample
can establish presence; absence requires complete coverage of the claim's
declared, finite scope. Otherwise the result is **not established**, not
**absent**.

## Dual-ledger model

The proposed extension keeps two linked, auditable records.

### Evidence ledger

Records the evidence used by a decision:

- evidence-root identifiers and authenticated issuers;
- repeated records collapsed into each root;
- declared shared dependencies and side-separation status;
- supporting and opposing root counts;
- `flip_budget` and `conversions_to_reverse` in their correct units;
- unattributed evidence, uncertainty, and the reason for abstention.

### Search ledger

Records how the evidence was sought:

- the exact proposition and whether it asserts presence or absence;
- the finite set of eligible locations, records, intervals, or sources;
- inclusion and exclusion rules fixed before evaluation;
- locations searched, failed, unavailable, or not searched;
- coverage numerator, denominator, retrieval time, and method;
- the stopping rule and the strongest conclusion coverage permits.

The ledgers answer different questions. Independent agreement cannot repair an
incomplete search, and exhaustive search cannot repair duplicated or forged
evidence.

## Candidate evidence label

An implementation should emit a compact, machine-readable label with every
material conclusion. For example:

```text
Conclusion: condition not found
Claim type: absence
Search space: 25 declared locations
Coverage: 20/25
Independent supporting roots: 3
Repeated records collapsed: 14
Opposing roots: 0
Result: not established — five locations were not searched
```

For a decisive presence claim, the same label should report the roots, margin,
reversal units, dependencies, and remaining uncertainty. The label is an audit
surface, not a certificate of truth.

## Research program

This direction becomes evidence only through preregistered tests. The next work
should:

1. define schemas for both ledgers and deterministic conclusion-strength rules;
2. construct positive, negative, incomplete-coverage, duplicated-source, and
   shared-dependency controls;
3. test whether the system ever promotes incomplete coverage to absence;
4. test whether duplicated records ever increase independent evidential mass;
5. test whether declared coverage and provenance are reproducible from the
   emitted records;
6. compare the dual-ledger output with released provenance and truth-discovery
   systems using matched inputs;
7. test at least one real provider without treating identity as independence.

Failure, null results, and cumbersome search spaces must remain visible. If a
space cannot be enumerated or searched exhaustively, the system must narrow the
claim or return **not established**.

## Intended value

This direction treats evidence as an auditable supply chain: discovery records
where the system looked, provenance prevents copies from becoming witnesses,
and decision rules expose the conclusion's safety margin. Its intended use is
to make the limits of machine knowledge measurable and visible—not to claim a
general truth machine.
