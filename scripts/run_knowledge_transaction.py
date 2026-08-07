#!/usr/bin/env python3
"""Evaluate one knowledge transaction and write canonical pretty JSON."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from knowledge_ledger import evaluate_transaction  # noqa: E402


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: run_knowledge_transaction.py INPUT OUTPUT")
    source, destination = map(Path, sys.argv[1:])
    result = evaluate_transaction(json.loads(source.read_text()))
    destination.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"transactionId": result["transactionId"], "conclusion": result["conclusion"], "contentDigest": result["contentDigest"]}))


if __name__ == "__main__":
    main()
