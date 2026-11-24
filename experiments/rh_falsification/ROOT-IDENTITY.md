# Root identity

A root is a finished calculation. Agent ids, votes and declared
`independent_of` lists are never roots.

## Fingerprint

A root is identified by the computation that produced it: search region,
method, software and version, seed, and result hash. In this pack the
fingerprint is the `result_hash`, or `method` plus `candidate_key` when no
hash exists yet.

`src/ledger_adapter.py` records a fingerprinted report as reading
`urn:rh-calc:<fingerprint>`. The canonical graph (`provenance/graph.py`)
materialises one parentless `source:` node per distinct reference, so every
report of the same calculation is a child of the same root. Forgetting to
cite a source therefore does not mint a new root.

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

One computational identity (same software, same method family, same
operator) must not be able to mint an unbounded number of roots by varying
only a seed or a window label.

The repository's mechanism for this is `provenance/root_registry.py`:
roots are bounded per authenticated issuer per fixed time window, and
`EvidenceGraph(root_authority=registry)` refuses any parentless node the
registry did not issue. `KnowledgeLedger` accepts a `root_authority` and
passes it to the graph. No authority is configured in this pack, so no cap is
enforced yet. Fingerprinted calculations enter the graph as cited `source:`
nodes, which the graph does not check against the authority, so enforcing a
cap on them needs one more step: issue each calculation as a registry root.

## Gate

Not wired: Gate `decide()` with `TrustAllVerifier`. If Gate is used later,
use `selective_decide` with a subject bound to the candidate and a real
verifier.
