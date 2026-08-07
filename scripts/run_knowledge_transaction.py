#!/usr/bin/env python3
"""Evaluate one knowledge transaction and write its machine and human receipts."""

from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from knowledge_ledger import evaluate_transaction  # noqa: E402


WORDS = {
    0: "No", 1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six",
    7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten", 11: "Eleven", 12: "Twelve",
}


def _word(count: int, lower: bool = False) -> str:
    """Small counts read better as words; large ones must stay exact.

    `lower` matters: a capitalised numeral mid-sentence ("back to Two
    independent roots") reads as a typo and undermines the care the rest of the
    document is claiming.
    """
    word = WORDS.get(count, str(count))
    return word.lower() if lower else word


def _plural(count: int, singular: str, plural: str) -> str:
    return singular if count == 1 else plural


def render_transmission(result: dict) -> str:
    """Render a receipt as restrained prose derived from its own values.

    Every sentence below is computed from the receipt. An earlier version wrote
    the numbers into the prose as literal text — "Five rooms were named. Four
    opened their doors" — while interpolating the receipt block underneath it.
    A different input would have produced a rendering whose story and whose
    receipt disagreed, with the prose being the part a reader trusts. Prewritten
    prose is not a rendering of evidence; it is a claim that happens to sit next
    to some.

    The title is deliberately modest. `reference-conformance-001` is a local
    conformance artifact, and rendering it in human language does not promote
    it. "First Transmission" is reserved for a passed cross-system transaction
    carrying a durable-history receipt, and "Candidate First Transmission" for
    one that passed the scientific gates without that receipt.
    """
    search = result["search"]
    evidence = result["evidence"]
    declared = int(search["declared"])
    searched = int(search["searched"])
    unavailable = int(search["unavailable"])
    records = int(evidence["records"])
    roots = int(evidence["distinctRoots"])
    conclusion = result["conclusion"]

    opening = [
        f"{_word(declared)} {_plural(declared, 'room was', 'rooms were')} named.",
        f"{_word(searched)} opened {_plural(searched, 'its door', 'their doors')}.",
    ]
    if unavailable:
        opening.append(
            f"{_word(unavailable)} remained beyond our reach."
        )
    else:
        opening.append("None remained beyond our reach.")

    if records == roots:
        lineage = (
            f"{_word(records)} {_plural(records, 'voice', 'voices')} answered, and lineage "
            f"held {_plural(records, 'it', 'them')} apart as {_word(roots, lower=True)} "
            f"independent {_plural(roots, 'root', 'roots')}."
        )
    else:
        lineage = (
            f"{_word(records)} {_plural(records, 'voice', 'voices')} answered, but lineage drew "
            f"them back to {_word(roots, lower=True)} independent {_plural(roots, 'root', 'roots')}."
        )

    # The caveat must follow the CONCLUSION, not just the coverage. Keyed on
    # `unavailable` alone it wrote "No contradiction was found in the rooms we
    # entered" onto a `present` receipt — a rendering that denied the very
    # counterexample its own receipt recorded two lines below.
    found_counterexample = conclusion == "present"
    if found_counterexample:
        caveat = (
            "A counterexample was found, and one is enough. The unsearched "
            f"{_plural(unavailable, 'room', 'rooms')} {_plural(unavailable, 'does', 'do')} not soften it, "
            "because presence needs one witness where absence needs every room."
            if unavailable else
            "A counterexample was found, and one is enough. No further coverage "
            "was required, because presence needs one witness where absence "
            "needs every room."
        )
    elif unavailable:
        caveat = (
            "No contradiction was found in the rooms we entered. Yet the unopened "
            f"{_plural(unavailable, 'door', 'doors')} still {_plural(unavailable, 'matters', 'matter')}. "
            "Agreement is not completion, and silence is not proof."
        )
    else:
        caveat = (
            "No contradiction was found, and every declared room was entered. The "
            "conclusion is bounded by that declaration and reaches no further. "
            "Agreement is not completion, and silence is not proof."
        )

    verdict = {
        "not_established": "Not established.",
        "absent_within_declared_scope": "Absent within the declared scope.",
        "present": "Present.",
    }.get(conclusion, conclusion)

    closing = (
        "This is a rendering, not a milestone: not a claim that the world has "
        "yielded its truth, but a promise that the boundary of what was searched "
        "will travel with the evidence. What we found is preserved. What we did "
        "not examine remains visible. What we cannot yet know is not quietly "
        "turned into certainty."
    )

    stance = (
        "So the ledger records what the evidence forces:"
        if found_counterexample else
        "So the ledger does not declare victory. It records the more honest sentence:"
    )
    body = textwrap.fill(f"{lineage} {caveat}", width=78)
    tail = textwrap.fill(closing, width=78)

    return f"""# Reference Conformance Rendering

{chr(10).join(opening)}

{body}

{stance}

> **{verdict}**

{tail}

---

## Verifiable receipt

- Transaction: `{result['transactionId']}`
- Declared locations: {declared}
- Searched locations: {searched}
- Unavailable locations: {unavailable}
- Evidence records: {records}
- Independent roots: {roots}
- Conclusion: `{conclusion}`
- Content digest: `{result['contentDigest']}`

This rendering is a human-readable companion to the receipt.
The JSON receipt is authoritative; this text makes no broader truth or absence
claim, and it does not promote the conformance fixture it describes into a
cross-system result.
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
