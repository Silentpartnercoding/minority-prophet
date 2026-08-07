#!/usr/bin/env python3
"""Evaluate one knowledge transaction and write its machine and human receipts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from knowledge_ledger import evaluate_transaction  # noqa: E402


def render_transmission(result: dict) -> str:
    """Render the reference receipt as restrained, evidence-faithful prose."""
    search = result["search"]
    evidence = result["evidence"]
    return f"""# First Transmission

Five rooms were named.
Four opened their doors.
One remained beyond our reach.

Four voices answered, but lineage drew them back to two independent roots.
No contradiction was found in the rooms we entered. Yet the unopened door
still matters. Agreement is not completion, and silence is not proof.

So the ledger does not declare victory. It records the more honest sentence:

> **Not established.**

This is the first transmission: not a claim that the world has yielded its
truth, but a promise that the boundary of what was searched will travel with
the evidence. What we found is preserved. What we did not examine remains
visible. What we cannot yet know is not quietly turned into certainty.

---

## Verifiable receipt

- Transaction: `{result['transactionId']}`
- Declared locations: {search['declared']}
- Searched locations: {search['searched']}
- Unavailable locations: {search['unavailable']}
- Evidence records: {evidence['records']}
- Independent roots: {evidence['distinctRoots']}
- Conclusion: `{result['conclusion']}`
- Content digest: `{result['contentDigest']}`

This rendering is a human-readable companion to `reference-receipt.json`. The
JSON receipt is authoritative; this text makes no broader truth or absence claim.
"""


def main() -> None:
    if len(sys.argv) not in (3, 4):
        raise SystemExit("usage: run_knowledge_transaction.py INPUT JSON_OUTPUT [MARKDOWN_OUTPUT]")
    source, destination = map(Path, sys.argv[1:3])
    result = evaluate_transaction(json.loads(source.read_text()))
    destination.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if len(sys.argv) == 4:
        Path(sys.argv[3]).write_text(render_transmission(result))
    print(json.dumps({"transactionId": result["transactionId"], "conclusion": result["conclusion"], "contentDigest": result["contentDigest"]}))


if __name__ == "__main__":
    main()
