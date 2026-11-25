# Root identity

A root is a finished calculation. Agent ids, votes and declared
`independent_of` lists are never roots.

## Fingerprint

A root is identified by the computation that produced it: search region,
method, software and version, seed, and result hash. In this pack the
fingerprint is the `result_hash`, or `method` plus `candidate_key` when no
hash exists yet.

`src/ledger_adapter.py` issues each distinct fingerprint once as a registry
root (`provenance/root_registry.py`), signed by the identity that first
posted it. Every later report of the same calculation becomes a child of
that root and issues nothing. Forgetting to cite a source therefore does not
mint a new root.

## Worked cases

- Two reports of one table lookup with the same hash are one root.
- Two different algorithms, each producing an interval proof of a candidate,
  are two roots: two finished calculations, even for the same candidate.
- Twenty reports with the same `result_hash` and empty
  `parent_evidence_ids` are one root. Empty parents do not mean "original
  observation".
- A report that declares a parent is a recorded copy. It adds no root, even
  if it carries a new hash of its own.
- A parentless report with no fingerprint is unattributed, not a root. The
  default policy is quarantine (zero roots). See `unattributed_policy`.

## What this pack does not claim

Only recorded or fingerprinted copies are collapsed. This pack does not say
that duplicating a claim can never change a verdict. An unrecorded duplicate
that carries a fresh fingerprint is counted as a new root, because nothing in
the record shows the link.

## Cap

One computational identity must not be able to mint an unbounded number of
roots by varying only a seed or a window label.

The cap is 2 roots per hour per signed identity, enforced by
`provenance/root_registry.py`. Every calculation is issued as a registry
root, and the graph is built with that registry as its `root_authority`, so
a parentless node the registry did not issue is refused. No calculation
enters as a cited `source:` node, which is the path the authority does not
check. A calculation refused for being over the cap adds zero roots.

Worked cases:

- One operator posting 20 distinct hashes within one hour counts 2 roots.
  The other 18 are refused.
- The same operator posting again in the next hour gets a fresh budget.
- Control E (three separate finders, one calculation each) still counts 3.
- Twenty identities repeating one hash (FP5) is one issuance and one root.
- The tower's own rechecks are under the same cap: at most 2
  counterexample roots per hour.

Signing here uses synthetic keys and a clock that follows each report. A
deployment injects a real identity verifier and clock.

## Gate

Not wired: Gate `decide()` with `TrustAllVerifier`. If Gate is used later,
use `selective_decide` with a subject bound to the candidate and a real
verifier.
