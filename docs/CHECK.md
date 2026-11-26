# The public check

Theorem 1: if two finite acyclic claim graphs are side-consistent, have equal
assertion functions, and have equal root sets, their root-counting verdicts
are equal. Among non-roots, lineage accuracy is not load-bearing; root integrity
and side separation are, with assertions fixed.

## One command

Run `make demo` from a Git clone with Make and Python 3.11+ available. This uses
only the standard library and checked-in files; it does not install dependencies,
fetch sources, call an endpoint, or execute a new confirmatory experiment.

The runner prints the full commit, whether the working tree is modified, a UTC
timestamp, and PASS/FAIL lines. Exit zero means all checks below passed.
A failed check prints `FAIL: <check>: <reason>` and exits nonzero. A missing
interpreter, file, or dependency import is also a nonzero execution failure;
it is not a mathematical counterexample. Optimized Python (`-O` or
`PYTHONOPTIMIZE`) is rejected because it disables the reused assertions.

| Check | What executes | Failure condition |
|---|---|---|
| Citation illustration | Existing constructed fixture, with three explicitly supplied root IDs | Citation count differs from 3 or supporting root set differs from `{MIL-2291}` |
| Bounded immunity | Existing LIN-000 live test enumerates side-consistent forests through four claims and valid single reparentings | A checked rewiring changes either side-root set or verdict, or no rewiring is checked |
| Assumption boundaries | Existing root-set and side-separation breaking controls | Expected counterexamples disappear |
| Side locality | Existing live forests through three claims, plus the recorded non-side-consistent witness | Equality fails under the assumptions, or the negative witness no longer has overlapping side roots |
| Incorrect implementations | Existing shallow-root and claim-count ablations through four claims | A registered incorrect variant is no longer detected |
| Archived-result consistency | Registered population derivation and committed LIN-000 result fields | Counts or recorded expectations disagree |

The six existing regression functions are named in the output and in
[`scripts/demo.py`](../scripts/demo.py); their implementation remains in
[`tests/test_lineage_t1_l1.py`](../tests/test_lineage_t1_l1.py).
Archived-result consistency does **not** regenerate the historical 100,000-world
randomized run. The citation illustration is not automatic provenance recovery,
and the constructed corpus is not a NIST validation or endorsement of MP.

## What would refute the theorem?

Two valid graphs satisfying **all** the stated preconditions but yielding
different verdicts would be a counterexample. A failing implementation check
requires diagnosis: an implementation or environment fault need not refute the
mathematical statement. A graph violating a precondition is an assumption-boundary
example, not a refutation. Finite forest checks are not a proof over all DAGs.

The proof uses the pinned Lean/Mathlib environment under `formal/lean/`:

```bash
cd formal/lean
lake exe cache get
lake build
```

This separate route needs the Lean toolchain and can download dependencies.
See [formal scope](../formal/PROOFS.md) and
[toolchain and axiom audit](../audit/REPRODUCE.md) before citing proof verification.

## Report exactly what ran

Use [Reproductions](../REPRODUCTIONS.md). A demo PASS supports this bounded
execution only. A Lean build, an external rerun, a separately written
implementation, and real-world validation are different evidence classes.
