#!/usr/bin/env python3
"""Count transactions whose direct receipt carries a non-null abstentionReason.

BL-060. Endpoint E3 measures whether uncertainty survives a crossing. A population
in which nothing is uncertain cannot move it and would pass by construction, so
the registration declares this probe with a negative control and the check refuses
the run if the population contains none.

Prints one integer. Nothing else.
"""
from __future__ import annotations

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[4]))

from knowledge_ledger.transaction_v2 import evaluate_transaction_v2  # noqa: E402


def count(population: pathlib.Path) -> int:
    total = 0
    for path in sorted(population.glob("*.json")):
        receipt = evaluate_transaction_v2(json.loads(path.read_text()))
        if receipt["uncertainty"]["abstentionReason"] is not None:
            total += 1
    return total


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: probe_uncertainty.py POPULATION_DIR", file=sys.stderr)
        raise SystemExit(2)
    directory = pathlib.Path(sys.argv[1])
    if not directory.is_dir():
        print(f"not a directory: {directory}", file=sys.stderr)
        raise SystemExit(2)
    print(count(directory))
