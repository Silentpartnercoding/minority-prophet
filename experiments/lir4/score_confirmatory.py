"""Frozen scorer for the LIR-4 provenance degradation envelope."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Any

from experiments.lir1.llm_echo.score_confirmatory import root_pair_counts_by_case
from experiments.lir1.metrics import root_count_metrics, root_pair_metrics
from experiments.lir1.model import ClaimInstance, read_jsonl
from experiments.lir1.run_pheme_confirmatory import f1_from_counts, percentile
from experiments.lir2.score_pheme_transfer import root_errors_by_case
from experiments.lir3.provenance_parent import Configuration, infer_roots
from experiments.lir4.attacks import (
    adversarially_misbind,
    collide_identities,
    count_hidden_edges,
    remove_reply_identity,
    visible_edges,
)


INPUT_SHA256 = "974df303ea8c489060b281260abde10e7b59f6525fcd2943e8c7138c99ddfe15"
CONFIGURATION = Configuration(0.00, 0.00, "none")
MISSING_FRACTIONS = (0.00, 0.25, 0.50, 0.75, 1.00)
COLLISION_BUCKETS = (32, 16, 8, 4, 2, 1)
BOOTSTRAP_SEED = 20260809
BOOTSTRAP_SAMPLES = 10_000


def _metrics(claims: list[ClaimInstance], features: list[ClaimInstance]) -> tuple[dict[str, Any], dict[str, str]]:
    roots = infer_roots(
        (claim.feature_view() for claim in features), configuration=CONFIGURATION
    )
    return ({
        "rootPair": root_pair_metrics(claims, roots),
        "rootCount": root_count_metrics(claims, roots),
    }, roots)


def _multi_root_claims(claims: list[ClaimInstance]) -> list[ClaimInstance]:
    roots: dict[str, set[str | None]] = defaultdict(set)
    for claim in claims:
        roots[claim.case_id].add(claim.true_root_id)
    cases = {case_id for case_id, values in roots.items() if len(values) > 1}
    return [claim for claim in claims if claim.case_id in cases]


def _restricted_roots(claims: list[ClaimInstance], roots: dict[str, str]) -> dict[str, str]:
    return {claim.claim_id: roots[claim.claim_id] for claim in claims}


def _pair_values(counts: list[tuple[int, int, int]]) -> tuple[float, float, float]:
    tp = sum(row[0] for row in counts)
    fp = sum(row[1] for row in counts)
    fn = sum(row[2] for row in counts)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return precision, recall, f1_from_counts(tp, fp, fn)


def _bootstrap(
    claims: list[ClaimInstance],
    intact_roots: dict[str, str],
    primary_roots: dict[str, str],
) -> dict[str, Any]:
    intact_counts = root_pair_counts_by_case(claims, intact_roots)
    primary_counts = root_pair_counts_by_case(claims, primary_roots)
    primary_errors = root_errors_by_case(claims, primary_roots)
    case_ids = sorted(primary_counts)
    rng = random.Random(BOOTSTRAP_SEED)
    values: dict[str, list[float]] = {
        "rootPrecision": [],
        "rootRecall": [],
        "rootF1": [],
        "rootCountMae": [],
        "recallChangeFromIntact": [],
        "f1ChangeFromIntact": [],
    }
    for _ in range(BOOTSTRAP_SAMPLES):
        sample = [case_ids[rng.randrange(len(case_ids))] for _ in case_ids]
        intact = _pair_values([intact_counts[case_id] for case_id in sample])
        primary = _pair_values([primary_counts[case_id] for case_id in sample])
        values["rootPrecision"].append(primary[0])
        values["rootRecall"].append(primary[1])
        values["rootF1"].append(primary[2])
        values["rootCountMae"].append(
            sum(primary_errors[case_id] for case_id in sample) / len(sample)
        )
        values["recallChangeFromIntact"].append(primary[1] - intact[1])
        values["f1ChangeFromIntact"].append(primary[2] - intact[2])
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


def score(source: Path) -> dict[str, Any]:
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    if source_hash != INPUT_SHA256:
        raise ValueError("source does not match the sealed LIR-4 holdout")
    claims = read_jsonl(source)
    if len(claims) != 5000 or len({claim.case_id for claim in claims}) != 400:
        raise ValueError("LIR-4 requires exactly 400 cases and 5,000 claims")
    visible = visible_edges(claims)
    hidden_edges = count_hidden_edges(claims, visible)

    missing_rows: list[dict[str, Any]] = []
    missing_roots: dict[float, dict[str, str]] = {}
    for fraction in MISSING_FRACTIONS:
        features = remove_reply_identity(claims, visible, fraction=fraction)
        metrics, roots = _metrics(claims, features)
        attacked = sum(
            original.channel_metadata.get("reply_target_author_id")
            != feature.channel_metadata.get("reply_target_author_id")
            for original, feature in zip(visible, features, strict=True)
        )
        missing_rows.append({"missingFraction": fraction, "attackedRecords": attacked, **metrics})
        missing_roots[fraction] = roots

    collision_rows: list[dict[str, Any]] = []
    collision_roots: dict[int, dict[str, str]] = {}
    for buckets in COLLISION_BUCKETS:
        metrics, roots = _metrics(
            claims, collide_identities(claims, visible, buckets=buckets)
        )
        collision_rows.append({"identityBuckets": buckets, **metrics})
        collision_roots[buckets] = roots

    misbound_features, eligible_misbindings = adversarially_misbind(claims, visible)
    misbound_metrics, misbound_roots = _metrics(claims, misbound_features)
    multi_claims = _multi_root_claims(claims)
    intact = missing_rows[0]
    primary = next(row for row in missing_rows if row["missingFraction"] == 0.50)
    complete = next(row for row in missing_rows if row["missingFraction"] == 1.00)
    tests = {
        "intactMinimumPrecision": intact["rootPair"]["precision"] >= 0.99,
        "intactMinimumRecall": intact["rootPair"]["recall"] >= 0.99,
        "primaryMinimumPrecision": primary["rootPair"]["precision"] >= 0.99,
        "primaryMinimumRecall": primary["rootPair"]["recall"] >= 0.65,
        "primaryMinimumF1": primary["rootPair"]["f1"] >= 0.78,
        "primaryMaximumRootCountMae": primary["rootCount"]["meanAbsoluteError"] < 2.5,
        "completeRemovalMinimumRecallLoss": (
            intact["rootPair"]["recall"] - complete["rootPair"]["recall"] >= 0.30
        ),
    }
    multi_case_count = len({claim.case_id for claim in multi_claims})
    multi_intact = {
        "rootPair": root_pair_metrics(
            multi_claims, _restricted_roots(multi_claims, missing_roots[0.00])
        ),
        "rootCount": root_count_metrics(
            multi_claims, _restricted_roots(multi_claims, missing_roots[0.00])
        ),
    }
    multi_collision = {
        "rootPair": root_pair_metrics(
            multi_claims, _restricted_roots(multi_claims, collision_roots[1])
        ),
        "rootCount": root_count_metrics(
            multi_claims, _restricted_roots(multi_claims, collision_roots[1])
        ),
    }
    multi_misbound = {
        "rootPair": root_pair_metrics(
            multi_claims, _restricted_roots(multi_claims, misbound_roots)
        ),
        "rootCount": root_count_metrics(
            multi_claims, _restricted_roots(multi_claims, misbound_roots)
        ),
    }
    safety_powered = multi_case_count >= 20 and eligible_misbindings >= 20
    safety_pass = safety_powered and multi_misbound["rootPair"]["precision"] >= 0.99
    return {
        "schema": "minority-prophet.lir4-confirmatory-result.v1",
        "status": "confirmatory-complete",
        "caseCount": 400,
        "claimCount": 5000,
        "hiddenExactEdges": hidden_edges,
        "configuration": CONFIGURATION.identifier,
        "criterion": {
            "tests": tests,
            "supported": all(tests.values()),
        },
        "primary": primary,
        "missingnessCurve": missing_rows,
        "collisionCurve": collision_rows,
        "primaryBootstrap": _bootstrap(
            claims, missing_roots[0.00], missing_roots[0.50]
        ),
        "safetyDiagnostic": {
            "minimumCasesForClaim": 20,
            "minimumEligibleMisbindingsForClaim": 20,
            "multiRootCases": multi_case_count,
            "eligibleMisbindings": eligible_misbindings,
            "powered": safety_powered,
            "safeResistanceSupported": safety_pass,
            "intact": multi_intact,
            "oneBucketCollision": multi_collision,
            "whiteBoxMisbindingAllCases": misbound_metrics,
            "whiteBoxMisbindingMultiRootCases": multi_misbound,
        },
        "normalizedInputSha256": source_hash,
        "labelBoundary": "Recorded PHEME reply-tree roots; not causal evidence independence.",
        "interpretationBoundary": (
            "Identity degradation within PHEME only; the cross-root safety diagnostic is "
            "underpowered unless its preregistered sample floors are met."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = score(args.source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps({
        "criterionSupported": result["criterion"]["supported"],
        "safetyPowered": result["safetyDiagnostic"]["powered"],
        "outputSha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
