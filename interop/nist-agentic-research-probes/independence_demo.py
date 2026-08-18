#!/usr/bin/env python3
"""Three citations, one evidentiary root -- the half that needs no LM judge.

The corpus in `corpus/` holds one measurement and two documents that report it.
A grounded report citing all three has three citations and one observation.

This script runs the provenance-aware aggregator over those three citations and
prints what a citation count says next to what a root count says. It is
deterministic, uses no model, and makes no network call: the independence side
of the proposed fourth probe does not require a judge.

The other side -- what NIST's faithfulness, completeness and sufficiency probes
score on the same report -- does require one, and has not been run. See README.

Run from the repository root:

    python3 interop/nist-agentic-research-probes/independence_demo.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from dataclasses import dataclass

from aggregation.root_vote import IndependenceBasis, verdict


@dataclass(frozen=True)
class Citation:
    """Conforms to the `RootedClaim` protocol in aggregation.root_vote."""

    value: bool
    root_id: str | None
    independence_basis: str | None

# One citation per corpus document. All three support the same proposition.
# Documents 02 and 03 state in their own text that they derive from MIL-2291,
# so the root is declared by the sources rather than inferred by us.
#
# `.value` is deliberate. `_basis_of` resolves the basis with
# `IndependenceBasis(str(raw))`, and `str()` on a `(str, Enum)` member yields
# "IndependenceBasis.DECLARED" rather than "declared", so passing the enum
# member itself resolves to UNKNOWN. Reported separately; this file passes the
# string so the printed basis is the one actually recorded.
CITATIONS = [
    ("[^1] corpus/01-root-observation.md", "MIL-2291", IndependenceBasis.DECLARED.value),
    ("[^2] corpus/02-derivative-trade-press.md", "MIL-2291", IndependenceBasis.DECLARED.value),
    ("[^3] corpus/03-derivative-review.md", "MIL-2291", IndependenceBasis.DECLARED.value),
]

PROPOSITION = "Kestrel-7 arrays drift 0.42% of full scale over a 300-hour hold at 41 C"


def main() -> int:
    claims = [
        Citation(value=True, root_id=root, independence_basis=basis)
        for _label, root, basis in CITATIONS
    ]
    result = verdict(claims)

    print(f"proposition: {PROPOSITION}\n")
    print("citations in the report:")
    for label, root, basis in CITATIONS:
        print(f"  {label:45s} root={root} basis={basis}")

    print(f"\n  counting citations : {len(CITATIONS)} supporting sources")
    print(f"  counting roots     : {len(result.support_true)} supporting root"
          f" ({', '.join(sorted(result.support_true))})")
    print(f"\n  verdict            : {result.verdict}")
    print(f"  margin             : {result.margin}")
    print(f"  weakest basis      : {result.weakest_basis}")
    print(f"  unattributed       : {result.unattributed}")

    # The demonstration, stated as an assertion so this file fails loudly if the
    # aggregator ever stops distinguishing these two counts.
    assert len(result.support_true) == 1, result.support_true
    assert len(CITATIONS) == 3

    print("\nthree citations, one root. No citation is unfaithful, incomplete or")
    print("overreaching; the count is simply not three.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
