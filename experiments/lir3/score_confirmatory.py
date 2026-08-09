"""One-shot confirmatory scorer for the sealed LIR-3 holdout."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path
from typing import Any

from experiments.lir1.llm_echo.score_confirmatory import root_pair_counts_by_case
from experiments.lir1.metrics import root_count_metrics, root_pair_metrics
from experiments.lir1.model import ClaimInstance, read_jsonl
from experiments.lir1.run_pheme_confirmatory import f1_from_counts, percentile
from experiments.lir1.synthetic_fixture import hide_edges
from experiments.lir2.root_grouping import infer_roots as infer_lir2_roots
from experiments.lir2.score_pheme_transfer import root_errors_by_case
from experiments.lir3.provenance_parent import Configuration, infer_roots


INPUT_SHA256 = "4a66b3bd48865c8a05d6167417d283ef3ad6ea46aef44aa18436a9ea2db5e1c0"
DEVELOPMENT_RESULT_SHA256 = "dec0f4d5c64ff0966920ec14a7d16f649d3e6778cf57dc7be29a6d7bf17322ba"
CONFIGURATION = Configuration(0.00, 0.00, "none")
HIDDEN_FRACTION = 0.40
BOOTSTRAP_SEED = 20260809
BOOTSTRAP_SAMPLES = 10_000


def _pair_values(counts: list[tuple[int, int, int]]) -> tuple[float, float, float]:
    tp = sum(row[0] for row in counts)
    fp = sum(row[1] for row in counts)
    fn = sum(row[2] for row in counts)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return precision, recall, f1_from_counts(tp, fp, fn)


def bootstrap_comparison(
    claims: list[ClaimInstance],
    provenance_roots: dict[str, str],
    baseline_roots: dict[str, str],
) -> dict[str, Any]:
    provenance_counts = root_pair_counts_by_case(claims, provenance_roots)
    baseline_counts = root_pair_counts_by_case(claims, baseline_roots)
    provenance_errors = root_errors_by_case(claims, provenance_roots)
    case_ids = sorted(provenance_counts)
    rng = random.Random(BOOTSTRAP_SEED)
    values: dict[str, list[float]] = {
        "rootPrecision": [],
        "rootRecall": [],
        "rootF1": [],
        "rootCountMae": [],
        "recallGainOverLir2": [],
        "f1GainOverLir2": [],
    }
    for _ in range(BOOTSTRAP_SAMPLES):
        sample = [case_ids[rng.randrange(len(case_ids))] for _ in case_ids]
        provenance = _pair_values([provenance_counts[case_id] for case_id in sample])
        baseline = _pair_values([baseline_counts[case_id] for case_id in sample])
        values["rootPrecision"].append(provenance[0])
        values["rootRecall"].append(provenance[1])
        values["rootF1"].append(provenance[2])
        values["rootCountMae"].append(
            sum(provenance_errors[case_id] for case_id in sample) / len(sample)
        )
        values["recallGainOverLir2"].append(provenance[1] - baseline[1])
        values["f1GainOverLir2"].append(provenance[2] - baseline[2])
    return {
        "samples": BOOTSTRAP_SAMPLES,
        "seed": BOOTSTRAP_SEED,
        "intervals95": {
            key: {
                "lower": percentile(series, 0.025),
                "upper": percentile(series, 0.975),
            }
            for key, series in values.items()
        },
    }


def score(source: Path, development_result: Path) -> dict[str, Any]:
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    development_hash = hashlib.sha256(development_result.read_bytes()).hexdigest()
    if source_hash != INPUT_SHA256:
        raise ValueError("source does not match the sealed LIR-3 holdout")
    if development_hash != DEVELOPMENT_RESULT_SHA256:
        raise ValueError("development result does not match the frozen selection")
    development = json.loads(development_result.read_text())
    if development["selected"]["configuration"]["id"] != CONFIGURATION.identifier:
        raise ValueError("selected configuration does not match the frozen scorer")
    claims = read_jsonl(source)
    if len(claims) != 5000 or len({claim.case_id for claim in claims}) != 425:
        raise ValueError("LIR-3 holdout requires exactly 425 cases and 5,000 claims")
    if any(claim.split != "confirmatory" for claim in claims):
        raise ValueError("LIR-3 scorer accepts only confirmatory rows")
    visible = hide_edges(claims, HIDDEN_FRACTION)
    provenance_roots = infer_roots(
        (claim.feature_view() for claim in visible), configuration=CONFIGURATION
    )
    baseline_roots = infer_lir2_roots(
        (claim.feature_view() for claim in visible), threshold=0.75
    )
    pair = root_pair_metrics(claims, provenance_roots)
    count = root_count_metrics(claims, provenance_roots)
    baseline_pair = root_pair_metrics(claims, baseline_roots)
    baseline_count = root_count_metrics(claims, baseline_roots)
    recall_gain = pair["recall"] - baseline_pair["recall"]
    f1_gain = pair["f1"] - baseline_pair["f1"]
    tests = {
        "minimumRootPrecision": pair["precision"] >= 0.99,
        "minimumRootRecall": pair["recall"] >= 0.45,
        "minimumRootF1": pair["f1"] >= 0.60,
        "strictMaximumRootCountMae": count["meanAbsoluteError"] < 4.0,
        "minimumRecallGainOverLir2": recall_gain >= 0.15,
        "minimumF1GainOverLir2": f1_gain >= 0.15,
    }
    return {
        "schema": "minority-prophet.lir3-confirmatory-result.v1",
        "status": "confirmatory-complete",
        "configuration": {
            "id": CONFIGURATION.identifier,
            "authorMinScore": CONFIGURATION.author_min_score,
            "authorMargin": CONFIGURATION.author_margin,
            "fallback": CONFIGURATION.fallback,
        },
        "caseCount": 425,
        "claimCount": 5000,
        "hiddenFraction": HIDDEN_FRACTION,
        "criterion": {
            "thresholds": {
                "minimumRootPrecision": 0.99,
                "minimumRootRecall": 0.45,
                "minimumRootF1": 0.60,
                "strictMaximumRootCountMae": 4.0,
                "minimumRecallGainOverLir2": 0.15,
                "minimumF1GainOverLir2": 0.15,
            },
            "tests": tests,
            "supported": all(tests.values()),
        },
        "rootPair": pair,
        "rootCount": count,
        "lir2SameCaseComparator": {
            "rootPair": baseline_pair,
            "rootCount": baseline_count,
        },
        "gainsOverLir2": {"rootRecall": recall_gain, "rootF1": f1_gain},
        "bootstrap": bootstrap_comparison(claims, provenance_roots, baseline_roots),
        "inputs": {
            "normalizedConfirmatorySha256": source_hash,
            "developmentResultSha256": development_hash,
        },
        "labelBoundary": "Recorded PHEME reply-tree roots; not causal evidence independence.",
        "interpretationBoundary": (
            "Previously unused cases from a previously studied corpus; not independent-dataset "
            "generalization, causal ancestry, evidence independence, or truth recovery."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--development-result", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = score(args.source, args.development_result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps({
        "criterionSupported": result["criterion"]["supported"],
        "outputSha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
