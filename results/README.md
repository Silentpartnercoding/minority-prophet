# Preserved results

This directory contains result packages, manifests, replications, incomplete
runs, and adverse outcomes. It is an evidence store, not a “successful results”
gallery.

## Find a result

- `exp*`, `heo*`, `hes*`, `hgd*`, and `hvi*` directories correspond to named
  experiment tracks.
- `lir*` directories preserve development, transfer, confirmatory, and
  replication packages from the lineage-inference series.
- [`canonical-replications-v1/`](canonical-replications-v1/) contains the
  canonical replication bundle.
- [`eaa-p5-out-of-tree-v1/`](eaa-p5-out-of-tree-v1/) is an imported out-of-tree
  test whose frozen gate rejected the candidate.

## Read safely

A directory name does not determine authority. Check:

1. [`research/records/`](../research/records/) for the machine-readable lifecycle
   record;
2. [`CANONICAL-RECORDS.md`](../CANONICAL-RECORDS.md) for canonical/imported
   status; and
3. [`EVIDENCE-ALIGNMENT.md`](../EVIDENCE-ALIGNMENT.md) for the claims the result
   does and does not support.

Canonical and imported packages are not rewritten in place. Null, rejected,
incomplete, and superseded outcomes remain visible so later readers can audit
the complete research history.
