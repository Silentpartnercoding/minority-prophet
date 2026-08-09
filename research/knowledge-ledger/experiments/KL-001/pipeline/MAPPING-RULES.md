# KL-001 mapping rules — repository to ledgers

Gate item (1). **Preparatory: KL-001 remains `seeded`.** These rules are
registered here so they are frozen before any evaluation uses them, per the
gate's requirement that the mapping layer's rules be registered as carefully as
the evaluator's. Committing KL-001 is the owner's act and nothing here does it.

The mapping layer is where the two known exposures live. Both are designed
against below rather than discovered again.

## M1 — the declared scope is DERIVED, never supplied

**The exposure (ADV-001, demonstrated as FC1's W3).** The evaluator honours the
declared search scope and cannot see what a declaration left out. Omit the two
uncovered files from the declaration — declared 2, searched 2 — and
`absent_within_declared_scope` falls out cleanly. The verdict is honest about the
scope it was given and the scope was a lie.

**The rule.** `map_repository()` takes no scope argument. The scope is computed
from the repository by a registered pattern set, and supplying one is a
`TypeError` rather than an option. To shrink the scope an adversary must delete
files from the repository, which changes its content digest, which is recorded
beside the ledgers.

    scopePatterns  = ["**/*.py"]            # registered; changing this is a
                                            # registration change, not a call argument
    scope          = sorted(repo.glob(p) for p in scopePatterns)
    scopeDigest    = SHA-256 over the sorted relative paths

**What this does not fix.** A file that never existed cannot be enumerated. The
rule converts "silently under-declare" into "delete, and leave a digest that does
not match the corpus manifest". It narrows the attack to one that leaves
evidence; it does not eliminate it. Stated because the previous version of this
programme's claims were too strong twice.

## M2 — one scanner family, one root

**The exposure (ADV-004 class).** The aggregator counts independent evidence
roots. If each of a scanner's findings becomes its own root, running one scanner
that reports five times manufactures five "independent" witnesses, and the margin
is inflated by repetition — the precise failure the whole programme exists to
refuse.

**The rule.** A root is a **scanner family**, identified by a registered
`familyId`. Every finding that scanner produces collapses to that one root,
regardless of count, file, or defect class. Two findings from two families are
two roots; two hundred findings from one family are one.

    rootId = familyId                      # never familyId + file, never per-finding

## M3 — searched means read, and is recorded per location

A location is `searched` only if the scanner opened it. A location in scope that
no scanner read is `not_searched`, and one that errored is `unavailable`. These
are the evaluator's three terminal states and the mapping layer must not collapse
them: `not_searched` and `unavailable` both block a clean absence verdict, and
conflating either with `searched` reintroduces W3 one layer down.

## M4 — the mapping is recorded, not just its output

Every run emits, beside the ledgers: the scope patterns used, the scope digest,
the family identifiers, and the count of findings collapsed into each root. A
reader can then check that M1 and M2 were obeyed rather than trusting that they
were.

## What is deliberately not decided here

The **defect-class taxonomy** — which scanner outputs count as the same finding —
is not registered, because KL-001's endpoints are not registered. Fixing it now
would decide part of the experiment before the owner commits it.
