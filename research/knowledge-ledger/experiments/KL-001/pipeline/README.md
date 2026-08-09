# KL-001 mapping pipeline — preparatory

**KL-001 remains `seeded`.** Nothing here advances it, and nothing is filed under
`results/`. Registering the endpoints and committing the gate is the owner's act.

Gate item (1): the layer that turns a repository into the two ledgers the KL-000
evaluator consumes. `MAPPING-RULES.md` registers the rules; `map_repository.py`
implements them.

## The two exposures this layer owns, designed against rather than rediscovered

**M1 — the scope is derived, never supplied.** FC1's W3 showed that a declaration
which simply omits the uncovered files earns a clean `absent_within_declared_scope`:
the evaluator is honest about the scope it is given, and the scope was a lie.
`map_repository()` takes no scope argument and refuses one loudly:

    map_repository(repo, scanners, scope=[...])
    -> ScopeSuppliedError: 'scope' may not be supplied ... this is ADV-001
       through the interface -- see FC1's W3

Narrowed, not eliminated: to shrink the scope an adversary must now delete files,
which changes the repository digest recorded beside the ledgers. Stated because
this programme has overclaimed twice.

**M2 — one scanner family, one root.** Per-finding roots would let a single
scanner reporting five times manufacture five "independent" witnesses. Measured
on the corpus: 2 findings from one family produce **1 distinct root, margin 1** —
not margin 2.

## Behaviour on the frozen corpus

    scanner reads everything   searched 5, not_searched 0  -> absent_within_declared_scope
    scanner skips one file     searched 4, not_searched 1  -> not_established
    scanner errors on one      searched 4, unavailable 1   -> not_established

`not_searched` and `unavailable` stay distinct and both block a clean absence.
Collapsing either into `searched` would reintroduce W3 one layer down.

## Not decided here

The defect-class taxonomy — which scanner outputs count as the same finding —
is left open, because KL-001's endpoints are unregistered and fixing it now would
decide part of the experiment before the owner commits it.
