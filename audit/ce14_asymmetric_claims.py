#!/usr/bin/env python3
"""CE-14 — the two shipped verdict paths disagree on a universal claim.

Run:  PYTHONPATH=. python3 audit/ce14_asymmetric_claims.py

A universal claim ("every X has property P") is falsified by ONE counterexample,
whatever the confirming count. The repository has two verdict paths and only one
of them knows that:

  aggregation/root_vote.verdict          counts roots per side, compares
  knowledge_ledger.evaluate_transaction  branches on (opposing?, coverage?)

`root_vote` is the aggregator the Lean theorems are about (formal/CLAIM-SCOPE.md).
On a universal claim it is not merely imprecise -- it returns the wrong side, with
an immunity guarantee attached, while holding an ATTESTED counterexample.

This file demonstrates the divergence and exits non-zero if it has been repaired
without the ledger entry being updated. It is an audit reproducer, not a fix.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass

from aggregation.root_vote import verdict
from knowledge_ledger.presentation import reversal_metrics
from knowledge_ledger.transaction_v2 import evaluate_transaction_v2

CONFIRMATIONS = 999


@dataclass
class Claim:
    """Minimal RootedClaim structural conformer."""

    value: bool
    root_id: str | None
    independence_basis: str | None = None


def counting_path(confirmations: int = CONFIRMATIONS):
    """The theorem-backed aggregator, handed one attested counterexample."""
    claims = [Claim(True, f"conf-{i}", "attested") for i in range(confirmations)]
    claims.append(Claim(False, "counterexample", "attested"))
    return verdict(claims)


def ledger_path(confirmations: int = CONFIRMATIONS, *, copies: int = 1):
    """The dual-ledger evaluator on the same evidence, as an absence claim.

    `copies` repeats the SAME opposing root, to show that copy collapse is
    recorded in the receipt and cannot reach the conclusion.
    """
    records = [{"rootId": f"conf-{i}", "side": "support"} for i in range(confirmations)]
    records += [{"rootId": "counterexample", "side": "oppose"}] * copies
    return evaluate_transaction_v2({
        "transactionId": "ce-14",
        "claim": {"id": "universal", "type": "absence",
                  "statement": "no member of the declared scope violates P"},
        "searchLedger": {"locations": [{"id": "scope-0", "status": "searched"}]},
        "evidenceLedger": {"records": records},
    })


def main() -> int:
    counted = counting_path()
    ledger = ledger_path()

    print("One ATTESTED counterexample against "
          f"{CONFIRMATIONS} confirmations of a universal claim:\n")
    print(f"  aggregation/root_vote      -> verdict={counted.verdict.value!r} "
          f"margin={counted.margin} flip_budget={counted.flip_budget} "
          f"attested_margin={counted.attested_margin} "
          f"immunity_applicable={counted.immunity_applicable}")
    print(f"  knowledge_ledger v0.2      -> conclusion={ledger['conclusion']!r} "
          f"margin={ledger['evidence']['margin']} "
          f"opposing_roots={len(ledger['evidence']['opposingRoots'])}")

    print("\nCopy collapse is recorded and cannot reach the conclusion:")
    for copies in (1, 20):
        r = ledger_path(copies=copies)
        print(f"  {copies:>2} record(s) of the SAME opposing root -> "
              f"conclusion={r['conclusion']!r} "
              f"collapsed={r['evidence']['repeatedRecordsCollapsed']}")

    metrics = reversal_metrics(ledger)
    print(f"\nflip_budget presented for that verdict: {metrics['flipBudget']} "
          f"({metrics['flipBudgetUnits']})")
    print(f"  budgetApplies={metrics.get('budgetApplies')!r}  "
          f"decidedByRootCount={metrics.get('decidedByRootCount')!r}")

    divergent = (counted.verdict.value == "true") and (ledger["conclusion"] == "present")
    if not divergent:
        print("\nCE-14 NOT REPRODUCED: the two paths now agree. "
              "Update formal/COUNTEREXAMPLES.md before removing this file.")
        return 1
    print("\nCE-14 reproduced: two shipped paths, one input, opposite sides.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
