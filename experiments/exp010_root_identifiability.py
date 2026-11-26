#!/usr/bin/env python3
"""EXP010: paired-world root-identifiability experiment."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import random
import statistics
import sys
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass, replace
from itertools import combinations


CASE_FAMILIES = (
    "independent_convergence",
    "direct_copy_honest_declaration",
    "direct_copy_omitted_declaration",
    "lossy_transformation",
    "hidden_shared_feed",
    "replay_fresh_identity",
    "sybil_control_boundary",
    "same_actor_distinct_acquisitions",
    "honest_receipt_copy",
    "compromised_provider_receipt",
)
METHODS = (
    "all_claims",
    "actor_key",
    "declared_lineage",
    "registry_policy",
    "source_receipt",
    "oracle",
)
CONFIRMATORY_SEEDS = tuple(range(401, 421))
PAIRS_PER_SEED = 200
BOOTSTRAP_SEED = 20261029
BOOTSTRAP_RESAMPLES = 10_000
METHOD_LEVELS = {
    "all_claims": 0,
    "actor_key": 1,
    "declared_lineage": 2,
    "registry_policy": 3,
    "source_receipt": 4,
    "oracle": 5,
}
HONEST_COPY_FAMILIES = frozenset(
    {
        "direct_copy_honest_declaration",
        "direct_copy_omitted_declaration",
        "lossy_transformation",
        "hidden_shared_feed",
        "replay_fresh_identity",
        "sybil_control_boundary",
        "honest_receipt_copy",
    }
)


@dataclass(frozen=True)
class Receipt:
    source_event_id: str
    challenge: str
    raw_digest: str
    provider_id: str
    capture_id: str
    time_window: int
    signature_valid: bool = True


@dataclass(frozen=True)
class Claim:
    claim_id: int
    assertion: tuple[int, ...]
    payload_digest: str
    actor_id: str
    actor_signature: str
    declared_parent: int | None
    citation: str | None
    registry_nonce: str
    issued_at: int
    tombstoned: bool
    receipt: Receipt


@dataclass(frozen=True)
class World:
    case_family: str
    claims: tuple[Claim, ...]
    true_root_by_claim: dict[int, int]
    provider_honest: bool


@dataclass(frozen=True)
class RootEstimate:
    root_by_claim: dict[int, int]
    abstained_claims: frozenset[int] = frozenset()


@dataclass(frozen=True)
class RootMetrics:
    root_precision: float
    root_recall: float
    root_f1: float
    pairwise_precision: float
    pairwise_recall: float
    pairwise_f1: float
    root_inflation: int
    root_deflation: int
    symmetric_difference: int
    abstention_rate: float


@dataclass(frozen=True)
class VerdictMetrics:
    applicable: int
    agree: int
    false_reversals: int
    root_error_k: int
    oracle_margins: tuple[int, ...]
    k_lt_m_agree: int
    k_lt_m_total: int


def _digest(label: str) -> str:
    return hashlib.sha256(label.encode()).hexdigest()


def _root_layout(copied_target: bool) -> dict[int, int]:
    roots = {0: 0, 1: 0 if copied_target else 1}
    for start, stop in ((2, 6), (6, 10), (10, 14), (14, 24)):
        for claim_id in range(start, stop):
            roots[claim_id] = start
    return roots


def _family_fields(family: str) -> tuple[str, str, int | None, str | None]:
    """Return target actors and public declaration fields for a family."""
    if family == "direct_copy_honest_declaration":
        return "actor-a", "actor-b", 0, "claim:0"
    if family == "direct_copy_omitted_declaration":
        return "actor-a", "actor-b", None, None
    if family == "replay_fresh_identity":
        return "actor-a", "actor-replay", None, "source:visible"
    if family == "sybil_control_boundary":
        return "sybil-key-a", "sybil-key-b", None, None
    if family == "same_actor_distinct_acquisitions":
        return "actor-shared", "actor-shared", None, None
    if family == "honest_receipt_copy":
        return "actor-a", "actor-b", 0, "claim:0"
    if family == "compromised_provider_receipt":
        return "actor-a", "actor-b", None, None
    return "actor-a", "actor-b", None, None


def _make_claims(
    rng: random.Random,
    family: str,
    roots: dict[int, int],
    copied_target: bool,
    compromised_provider: bool,
) -> tuple[Claim, ...]:
    salt = f"{rng.getrandbits(128):032x}"
    actor_zero, actor_one, parent_one, citation_one = _family_fields(family)
    root_assertions = {
        root: tuple(
            int(bit)
            for bit in bin(int(_digest(f"assertion:{salt}:{root}"), 16))[2:].zfill(256)[:8]
        )
        for root in (0, 1, 2, 6, 10, 14)
    }
    # Keep the target observations fixed across the pair even when their hidden
    # causal relation differs. A hidden copy therefore carries the visible
    # assertion selected for claim 1, just as an independent convergence does.
    root_assertions[1] = root_assertions[0]

    claims: list[Claim] = []
    for claim_id in range(24):
        root_id = roots[claim_id]
        if claim_id == 1:
            assertion = root_assertions[1]
        else:
            assertion = root_assertions[root_id]
        actor_id = (
            actor_zero
            if claim_id == 0
            else actor_one
            if claim_id == 1
            else f"actor-{root_id}"
        )
        declared_parent = parent_one if claim_id == 1 else None
        citation = citation_one if claim_id == 1 else None
        if claim_id > 1 and claim_id != root_id:
            declared_parent = root_id
            citation = f"claim:{root_id}"

        visible_event = (
            1
            if claim_id == 1 and compromised_provider
            else root_id
        )
        receipt = Receipt(
            source_event_id=f"event:{salt}:{visible_event}",
            challenge=f"challenge:{salt}:{claim_id}",
            raw_digest=_digest(f"raw:{salt}:{visible_event}"),
            provider_id="provider:source-bound",
            capture_id=f"capture:{salt}:{visible_event}",
            time_window=claim_id // 4,
        )
        claims.append(
            Claim(
                claim_id=claim_id,
                assertion=assertion,
                payload_digest=_digest(f"payload:{salt}:{claim_id}:{assertion}"),
                actor_id=actor_id,
                actor_signature=_digest(f"signature:{salt}:{actor_id}:{claim_id}"),
                declared_parent=declared_parent,
                citation=citation,
                registry_nonce=f"nonce:{salt}:{claim_id}",
                issued_at=1_800_000_000 + claim_id,
                tombstoned=False,
                receipt=receipt,
            )
        )
    return tuple(claims)


def generate_pair(rng: random.Random, case_family: str) -> tuple[World, World]:
    """Create observationally paired worlds using only the supplied PRNG."""
    if case_family not in CASE_FAMILIES:
        raise ValueError(f"unknown case family: {case_family}")

    independent_roots = _root_layout(copied_target=False)
    copied_roots = _root_layout(copied_target=True)
    compromised = case_family == "compromised_provider_receipt"

    # Generate one public record set, then alter only the receipt fields that
    # the honest provider would necessarily bind to the distinct hidden event.
    public_rng_state = rng.getstate()
    left_claims = _make_claims(
        rng,
        case_family,
        independent_roots,
        copied_target=False,
        compromised_provider=compromised,
    )
    rng.setstate(public_rng_state)
    right_claims = _make_claims(
        rng,
        case_family,
        copied_roots,
        copied_target=True,
        compromised_provider=compromised,
    )

    # Hidden causality must not leak into L0-L3. For honest providers, only the
    # source-event receipt changes: the copied world binds claim 1 to event 0.
    if not compromised:
        right = list(right_claims)
        right[1] = replace(
            right[1],
            receipt=replace(
                right[1].receipt,
                source_event_id=right[0].receipt.source_event_id,
                raw_digest=right[0].receipt.raw_digest,
                capture_id=right[0].receipt.capture_id,
            ),
        )
        right_claims = tuple(right)

    return (
        World(case_family, left_claims, independent_roots, not compromised),
        World(case_family, right_claims, copied_roots, not compromised),
    )


def _claim_projection(claim: Claim, level: int) -> dict[str, object]:
    output: dict[str, object] = {
        "assertion": list(claim.assertion),
        "claim_id": claim.claim_id,
        "payload_digest": claim.payload_digest,
    }
    if level >= 1:
        output.update(
            actor_id=claim.actor_id,
            actor_signature=claim.actor_signature,
        )
    if level >= 2:
        output.update(
            citation=claim.citation,
            declared_parent=claim.declared_parent,
        )
    if level >= 3:
        output.update(
            issued_at=claim.issued_at,
            registry_nonce=claim.registry_nonce,
            tombstoned=claim.tombstoned,
        )
    if level >= 4:
        output["receipt"] = asdict(claim.receipt)
    return output


def project(world: World, level: int) -> bytes:
    """Return canonical bytes visible at interface level L0 through L4."""
    if level not in range(5):
        raise ValueError("level must be an integer from 0 through 4")
    visible = {
        "case_family": world.case_family,
        "claims": [_claim_projection(claim, level) for claim in world.claims],
        "level": level,
    }
    return (json.dumps(visible, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _declared_roots(world: World) -> dict[int, int]:
    claims = {claim.claim_id: claim for claim in world.claims}
    roots: dict[int, int] = {}

    def root(claim_id: int, trail: frozenset[int] = frozenset()) -> int:
        if claim_id in roots:
            return roots[claim_id]
        if claim_id in trail:
            return claim_id
        parent = claims[claim_id].declared_parent
        if parent is None or parent not in claims:
            roots[claim_id] = claim_id
        else:
            roots[claim_id] = root(parent, trail | {claim_id})
        return roots[claim_id]

    for claim in world.claims:
        root(claim.claim_id)
    return roots


def _group_roots(
    world: World, key_function: Callable[[Claim], object]
) -> dict[int, int]:
    groups: dict[object, list[int]] = {}
    for claim in world.claims:
        key = key_function(claim)
        groups.setdefault(key, []).append(claim.claim_id)
    representatives = {
        key: min(claim_ids) for key, claim_ids in groups.items()
    }
    return {
        claim.claim_id: representatives[key_function(claim)]
        for claim in world.claims
    }


def estimate_roots(world: World, method: str, level: int) -> RootEstimate:
    """Estimate operational roots from a named interface policy."""
    if method not in METHODS:
        raise ValueError(f"unknown method: {method}")
    claim_ids = frozenset(claim.claim_id for claim in world.claims)
    if method == "oracle":
        return RootEstimate(dict(world.true_root_by_claim))
    if method == "all_claims":
        return RootEstimate({claim_id: claim_id for claim_id in claim_ids})
    if method == "actor_key":
        if level < 1:
            return RootEstimate({}, claim_ids)
        return RootEstimate(_group_roots(world, lambda claim: claim.actor_id))
    if method == "declared_lineage":
        if level < 2:
            return RootEstimate({}, claim_ids)
        return RootEstimate(_declared_roots(world))
    if method == "registry_policy":
        if level < 3:
            return RootEstimate({}, claim_ids)
        valid = tuple(claim for claim in world.claims if not claim.tombstoned)
        valid_world = replace(world, claims=valid)
        roots = _declared_roots(valid_world)
        abstained = claim_ids - frozenset(roots)
        return RootEstimate(roots, abstained)
    if level < 4:
        return RootEstimate({}, claim_ids)
    valid_receipts = tuple(
        claim for claim in world.claims if claim.receipt.signature_valid
    )
    roots = _group_roots(
        replace(world, claims=valid_receipts),
        lambda claim: claim.receipt.source_event_id,
    )
    return RootEstimate(roots, claim_ids - frozenset(roots))


def _f1(precision: float, recall: float) -> float:
    return 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)


def score_roots(world: World, estimate: RootEstimate) -> RootMetrics:
    true_roots = set(world.true_root_by_claim.values())
    estimated_roots = set(estimate.root_by_claim.values())
    overlap = len(true_roots & estimated_roots)
    root_precision = overlap / len(estimated_roots) if estimated_roots else 0.0
    root_recall = overlap / len(true_roots) if true_roots else 0.0

    pair_true_positive = 0
    pair_false_positive = 0
    pair_false_negative = 0
    decided = sorted(estimate.root_by_claim)
    for left, right in combinations(decided, 2):
        true_same = world.true_root_by_claim[left] == world.true_root_by_claim[right]
        estimated_same = estimate.root_by_claim[left] == estimate.root_by_claim[right]
        pair_true_positive += int(true_same and estimated_same)
        pair_false_positive += int(not true_same and estimated_same)
        pair_false_negative += int(true_same and not estimated_same)
    pair_precision_denominator = pair_true_positive + pair_false_positive
    pair_recall_denominator = pair_true_positive + pair_false_negative
    pair_precision = (
        pair_true_positive / pair_precision_denominator
        if pair_precision_denominator
        else 0.0
    )
    pair_recall = (
        pair_true_positive / pair_recall_denominator
        if pair_recall_denominator
        else 0.0
    )
    return RootMetrics(
        root_precision=root_precision,
        root_recall=root_recall,
        root_f1=_f1(root_precision, root_recall),
        pairwise_precision=pair_precision,
        pairwise_recall=pair_recall,
        pairwise_f1=_f1(pair_precision, pair_recall),
        root_inflation=max(0, len(estimated_roots) - len(true_roots)),
        root_deflation=max(0, len(true_roots) - len(estimated_roots)),
        symmetric_difference=len(true_roots ^ estimated_roots),
        abstention_rate=len(estimate.abstained_claims) / len(world.claims),
    )


def _root_votes(
    world: World, root_by_claim: dict[int, int], proposition: int
) -> tuple[int | None, int, bool]:
    claims = {claim.claim_id: claim for claim in world.claims}
    groups: dict[int, list[int]] = {}
    for claim_id, root_id in root_by_claim.items():
        groups.setdefault(root_id, []).append(claim_id)
    sides = {0: 0, 1: 0}
    side_consistent = True
    for claim_ids in groups.values():
        answers = {claims[claim_id].assertion[proposition] for claim_id in claim_ids}
        if len(answers) != 1:
            side_consistent = False
            continue
        sides[answers.pop()] += 1
    difference = sides[1] - sides[0]
    verdict = None if difference == 0 else int(difference > 0)
    return verdict, abs(difference), side_consistent


def score_verdicts(world: World, estimate: RootEstimate) -> VerdictMetrics:
    k = score_roots(world, estimate).symmetric_difference
    applicable = agree = false_reversals = 0
    margins: list[int] = []
    k_lt_m_agree = k_lt_m_total = 0
    if estimate.abstained_claims:
        return VerdictMetrics(0, 0, 0, k, (), 0, 0)
    for proposition in range(len(world.claims[0].assertion)):
        oracle, margin, oracle_consistent = _root_votes(
            world, world.true_root_by_claim, proposition
        )
        estimated, _, estimated_consistent = _root_votes(
            world, estimate.root_by_claim, proposition
        )
        margins.append(margin)
        if not oracle_consistent or not estimated_consistent:
            continue
        applicable += 1
        matches = estimated == oracle
        agree += int(matches)
        false_reversals += int(not matches)
        if k < margin:
            k_lt_m_total += 1
            k_lt_m_agree += int(matches)
    return VerdictMetrics(
        applicable,
        agree,
        false_reversals,
        k,
        tuple(margins),
        k_lt_m_agree,
        k_lt_m_total,
    )


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def exact_zero_error_upper(total: int, alpha: float = 0.05) -> float:
    if total < 1:
        raise ValueError("total must be positive")
    return 1.0 - alpha ** (1.0 / total)


def exact_all_success_lower(total: int, alpha: float = 0.05) -> float:
    if total < 1:
        raise ValueError("total must be positive")
    return alpha ** (1.0 / total)


def _percentile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return round(ordered[lower] * (1 - fraction) + ordered[upper] * fraction, 12)


def _pair_bootstrap(values: list[float], seed: int, resamples: int) -> dict[str, object]:
    if not values or resamples < 1:
        raise ValueError("bootstrap requires values and positive resamples")
    rng = random.Random(seed)
    count = len(values)
    samples: list[float] = []
    for _ in range(resamples):
        samples.append(sum(values[rng.randrange(count)] for _ in range(count)) / count)
    return {
        "lower": _percentile(samples, 0.025),
        "point": round(statistics.mean(values), 12),
        "samples": resamples,
        "upper": _percentile(samples, 0.975),
    }


def _mean_method_metrics(rows: list[RootMetrics]) -> dict[str, float]:
    names = tuple(asdict(rows[0]))
    return {
        name: round(statistics.mean(float(getattr(row, name)) for row in rows), 12)
        for name in names
    }


def run_experiment(
    seeds: tuple[int, ...] = CONFIRMATORY_SEEDS,
    pairs_per_seed: int = PAIRS_PER_SEED,
    bootstrap_seed: int = BOOTSTRAP_SEED,
    resamples: int = BOOTSTRAP_RESAMPLES,
) -> dict[str, object]:
    if pairs_per_seed < 1 or pairs_per_seed % len(CASE_FAMILIES):
        raise ValueError("pairs_per_seed must be a positive multiple of ten")

    method_rows: dict[str, list[RootMetrics]] = {method: [] for method in METHODS}
    source_pair_f1: list[float] = []
    family_counts = {family: 0 for family in CASE_FAMILIES}
    lower_projection_violations = 0
    hidden_relation_violations = 0
    compromised_l4_witnesses = 0
    compromised_l4_violations = 0
    copy_errors = copy_opportunities = 0
    independent_successes = independent_opportunities = 0
    margin_checks = {
        method: {"agree": 0, "total": 0, "violations": 0}
        for method in METHODS
    }

    for seed in seeds:
        rng = random.Random(seed)
        for pair_index in range(pairs_per_seed):
            family = CASE_FAMILIES[pair_index % len(CASE_FAMILIES)]
            independent, copied = generate_pair(rng, family)
            family_counts[family] += 1
            if independent.true_root_by_claim == copied.true_root_by_claim:
                hidden_relation_violations += 1
            if any(project(independent, level) != project(copied, level) for level in range(4)):
                lower_projection_violations += 1

            l4_equal = project(independent, 4) == project(copied, 4)
            if family == "compromised_provider_receipt":
                compromised_l4_witnesses += int(l4_equal)
                compromised_l4_violations += int(not l4_equal)

            pair_source_f1: list[float] = []
            for world in (independent, copied):
                for method in METHODS:
                    estimate = estimate_roots(world, method, METHOD_LEVELS[method])
                    root_metrics = score_roots(world, estimate)
                    method_rows[method].append(root_metrics)
                    verdict = score_verdicts(world, estimate)
                    margin_checks[method]["agree"] += verdict.k_lt_m_agree
                    margin_checks[method]["total"] += verdict.k_lt_m_total
                    margin_checks[method]["violations"] += (
                        verdict.k_lt_m_total - verdict.k_lt_m_agree
                    )
                    if method == "source_receipt":
                        pair_source_f1.append(root_metrics.pairwise_f1)
            source_pair_f1.append(statistics.mean(pair_source_f1))

            if family in HONEST_COPY_FAMILIES:
                copy_opportunities += 1
                copied_estimate = estimate_roots(copied, "source_receipt", 4)
                copy_errors += int(copied_estimate.root_by_claim[0] != copied_estimate.root_by_claim[1])
            if family != "compromised_provider_receipt":
                independent_opportunities += 1
                independent_estimate = estimate_roots(independent, "source_receipt", 4)
                independent_successes += int(
                    independent_estimate.root_by_claim[0]
                    != independent_estimate.root_by_claim[1]
                )

    copy_upper = (
        exact_zero_error_upper(copy_opportunities)
        if copy_errors == 0
        else 1.0
    )
    independent_rate = independent_successes / independent_opportunities
    independent_lower = (
        exact_all_success_lower(independent_opportunities)
        if independent_successes == independent_opportunities
        else 0.0
    )
    h1 = lower_projection_violations == 0 and hidden_relation_violations == 0
    h2 = copy_errors == 0 and copy_upper < 0.005
    h3 = independent_rate >= 0.99 and independent_lower >= 0.985
    h4 = compromised_l4_witnesses > 0 and compromised_l4_violations == 0
    informative_margin_checks = sum(
        values["total"] for values in margin_checks.values()
    )
    h5 = informative_margin_checks > 0 and all(
        values["violations"] == 0 for values in margin_checks.values()
    )
    hypotheses = {
        "H10-1": "supported" if h1 else "rejected",
        "H10-2": "supported" if h2 else "rejected",
        "H10-3": "supported" if h3 else "rejected",
        "H10-4": "supported" if h4 else "rejected",
        "H10-5": "supported" if h5 else "rejected",
    }
    return {
        "bootstrap": {
            "resampling_unit": "world_pair",
            "seed": bootstrap_seed,
            "source_receipt_pairwise_f1": _pair_bootstrap(
                source_pair_f1, bootstrap_seed, resamples
            ),
        },
        "configuration": {
            "bootstrap_resamples": resamples,
            "bootstrap_seed": bootstrap_seed,
            "case_families": list(CASE_FAMILIES),
            "pairs_per_seed": pairs_per_seed,
            "seeds": list(seeds),
        },
        "construction": {
            "compromised_l4_violations": compromised_l4_violations,
            "compromised_l4_witnesses": compromised_l4_witnesses,
            "family_counts": family_counts,
            "hidden_relation_violations": hidden_relation_violations,
            "l0_l3_projection_violations": lower_projection_violations,
        },
        "honest_receipt": {
            "copy_errors": copy_errors,
            "copy_opportunities": copy_opportunities,
            "copy_zero_error_upper_95": round(copy_upper, 12),
            "independent_lower_95": round(independent_lower, 12),
            "independent_opportunities": independent_opportunities,
            "independent_preservation": round(independent_rate, 12),
            "independent_successes": independent_successes,
        },
        "hypotheses": hypotheses,
        "margin_checks": margin_checks,
        "method_metrics": {
            method: _mean_method_metrics(rows) for method, rows in method_rows.items()
        },
        "overall_verdict": (
            "supported" if set(hypotheses.values()) == {"supported"} else "rejected"
        ),
    }


def attach_provenance(
    result: dict[str, object],
    protocol_commit: str,
    implementation_commit: str,
    runner_source: bytes,
) -> dict[str, object]:
    output = dict(result)
    output["provenance"] = {
        "implementation_commit": implementation_commit,
        "protocol_commit": protocol_commit,
        "runner_source_sha256": hashlib.sha256(runner_source).hexdigest(),
    }
    output["schema"] = "minority-prophet.exp010-result.v1"
    return output


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=str)
    parser.add_argument("--timing-output", required=True, type=str)
    parser.add_argument("--protocol-commit", required=True)
    parser.add_argument("--implementation-commit", required=True)
    return parser


def _validate_commit(value: str, label: str) -> None:
    if len(value) != 40 or any(character not in "0123456789abcdef" for character in value):
        raise ValueError(f"{label} must be a lowercase 40-character Git SHA")


def main() -> int:
    from pathlib import Path

    args = build_parser().parse_args()
    _validate_commit(args.protocol_commit, "protocol commit")
    _validate_commit(args.implementation_commit, "implementation commit")
    output_path = Path(args.output)
    timing_path = Path(args.timing_output)
    if output_path == timing_path:
        raise ValueError("scientific and timing outputs must differ")
    if output_path.exists() or timing_path.exists():
        raise FileExistsError("EXP010 outputs are append-only")
    started = time.perf_counter()
    result = run_experiment()
    scientific = attach_provenance(
        result,
        args.protocol_commit,
        args.implementation_commit,
        Path(__file__).read_bytes(),
    )
    scientific_bytes = canonical_json(scientific)
    diagnostics = {
        "environment": {
            "implementation": platform.python_implementation(),
            "platform": platform.platform(),
            "python": sys.version,
        },
        "schema": "minority-prophet.exp010-diagnostics.v1",
        "scientific_output_sha256": hashlib.sha256(scientific_bytes).hexdigest(),
        "total_duration_seconds": round(time.perf_counter() - started, 12),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    timing_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("xb") as destination:
        destination.write(scientific_bytes)
    with timing_path.open("xb") as destination:
        destination.write(canonical_json(diagnostics))
    print(json.dumps({
        "overall_verdict": scientific["overall_verdict"],
        "scientific_output_sha256": hashlib.sha256(scientific_bytes).hexdigest(),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
