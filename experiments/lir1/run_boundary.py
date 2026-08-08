"""Run the LIR-1 software-mechanics fixture without making a research claim."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .infer import infer_parents, roots_from_parents
from .metrics import aggregation_accuracy, parent_metrics, root_count_metrics, root_pair_metrics
from .synthetic_fixture import build_fixture, hide_edges


FRACTIONS = (0.05, 0.15, 0.25, 0.40, 0.55, 0.70, 0.85, 0.95)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run() -> dict[str, object]:
    truth_claims = build_fixture()
    rows: list[dict[str, object]] = []
    for fraction in FRACTIONS:
        observed = hide_edges(truth_claims, fraction)
        predictions = infer_parents(claim.feature_view() for claim in observed)
        roots = roots_from_parents(predictions)
        rows.append({
            "hiddenFraction": fraction,
            "parent": parent_metrics(truth_claims, predictions),
            "rootPair": root_pair_metrics(truth_claims, roots),
            "rootCount": root_count_metrics(truth_claims, roots),
            "aggregation": aggregation_accuracy(truth_claims, roots),
        })
    prereg = Path(__file__).with_name("PREREGISTRATION.md")
    return {
        "schema": "minority-prophet.lir1-mechanics-result.v1",
        "status": "software-mechanics-only",
        "claimBoundary": "Deterministic text fixture; not the registered LLM corpus or a LIR-1 hypothesis result.",
        "configuration": {"cases": 40, "threshold": 0.58, "fractions": list(FRACTIONS)},
        "preregistrationSha256": sha256(prereg),
        "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run()
    rendered = json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
