#!/usr/bin/env python3
"""Reproduce the 2026-08-06 sanitized field-evidence report."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Assertion:
    value: bool
    root_id: str | None


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))

from aggregation.root_vote import verdict  # noqa: E402


def evaluate_claim(claim: dict, *, root_strategy: str = "observer") -> dict:
    assertions = []
    for index, support in enumerate(claim["supports"], start=1):
        observer = support["observer"]
        root_id = observer if root_strategy == "observer" else f'{claim["id"]}:event-{index:03d}'
        if observer == claim["subject"]:
            root_id = None
        assertions.append(Assertion(value=bool(support["value"]), root_id=root_id))

    result = verdict(assertions)
    return {
        "id": claim["id"],
        "verdict": result.verdict.value,
        "margin": result.margin,
        "flip_budget": result.flip_budget,
        "conversions_to_reverse": result.conversions_to_reverse,
        "unattributed": result.unattributed,
        "distinct_roots": len(result.support_true | result.support_false),
    }


def main() -> None:
    payload = json.loads((HERE / "claims.generic.json").read_text())
    observer_results = [evaluate_claim(claim) for claim in payload["claims"]]
    repeated = next(claim for claim in payload["claims"] if claim["id"] == "claim-009")
    event_result = evaluate_claim(repeated, root_strategy="event")

    counts = {"true": 0, "false": 0, "abstain": 0}
    for result in observer_results:
        counts[result["verdict"]] += 1

    report = {
        "schema": "minority-prophet.field-report.v1",
        "claims": observer_results,
        "summary": {
            "claims_total": len(observer_results),
            "verdicts": counts,
            "one_root_decisions": sum(
                result["distinct_roots"] == 1 and result["verdict"] != "abstain"
                for result in observer_results
            ),
            "self_attestation_abstentions": sum(
                result["unattributed"] > 0 and result["verdict"] == "abstain"
                for result in observer_results
            ),
            "primary_observer_claim_share": "8/17",
        },
        "root_identity_probe": {
            "claim_id": "claim-009",
            "records": len(repeated["supports"]),
            "observer_keyed": next(r for r in observer_results if r["id"] == "claim-009"),
            "event_keyed": event_result,
            "interpretation": "The same records produce different margins solely from the root-identity rule.",
        },
        "partial_correlation_probe": {
            "shared_dependencies": payload["correlation_probe"]["shared_dependencies"],
            "representable_root_counts": [1, 2],
            "graded_value_representable": False,
        },
        "metric_unit_probe": {
            "margin": event_result["margin"],
            "flip_budget": event_result["flip_budget"],
            "conversions_to_reverse": event_result["conversions_to_reverse"],
            "interpretation": "Net per-side root change and side conversions are different units; both must be reported.",
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
