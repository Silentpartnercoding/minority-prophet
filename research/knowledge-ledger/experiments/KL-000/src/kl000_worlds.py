"""KL-000 world generation.

A *world* is one knowledge-transaction payload: a claim type, a search ledger of
location statuses, and an evidence ledger of (rootId, side) records.

This module only builds worlds. It never evaluates them and never imports the
evaluator, so a bug here cannot quietly agree with a bug there.

Bounds are fixed by `preregistration.json` (protocol v1.0.0) and are duplicated
here as constants so that a drift between the two is detectable rather than
invisible; `verify_bounds_against_preregistration()` performs that check.
"""

from __future__ import annotations

import itertools
import json
import random
from pathlib import Path
from typing import Any, Iterator

# --- Declared exhaustive bounds (protocol v1.0.0) -------------------------

LOCATION_COUNTS = (1, 2, 3, 4)
LOCATION_STATUSES = ("searched", "unavailable", "failed", "not_searched")
RECORD_COUNTS = (0, 1, 2, 3)
ROOT_IDS = ("r1", "r2", "r3")
SIDES = ("support", "oppose")
CLAIM_TYPES = ("absence", "presence")

DECLARED_WORLD_COUNT = 176120

# --- Declared randomized bounds (protocol v1.0.0) -------------------------

RANDOM_SEED = 20260807
RANDOM_WORLD_COUNT = 1_000_000
RANDOM_LOCATION_RANGE = (1, 12)
RANDOM_RECORD_RANGE = (0, 24)
RANDOM_ROOT_POOL = ("r1", "r2", "r3", "r4", "r5", "r6", "r7", "r8")

PROPOSITIONS = {
    "absence": "No target-class defect exists in the declared components.",
    "presence": "A target-class defect exists in the declared components.",
}


def build_world(
    transaction_id: str,
    claim_type: str,
    statuses: tuple[str, ...],
    records: tuple[tuple[str, str], ...],
) -> dict[str, Any]:
    """Assemble one payload from a status tuple and a (rootId, side) tuple."""
    return {
        "transactionId": transaction_id,
        "claim": {"type": claim_type, "proposition": PROPOSITIONS[claim_type]},
        "searchLedger": {
            "locations": [
                {"id": f"loc-{i}", "status": status}
                for i, status in enumerate(statuses, start=1)
            ]
        },
        "evidenceLedger": {
            "records": [
                {"id": f"rec-{i}", "rootId": root, "side": side}
                for i, (root, side) in enumerate(records, start=1)
            ]
        },
    }


def enumerate_status_ledgers() -> Iterator[tuple[str, ...]]:
    for n in LOCATION_COUNTS:
        yield from itertools.product(LOCATION_STATUSES, repeat=n)


def enumerate_record_ledgers() -> Iterator[tuple[tuple[str, str], ...]]:
    pairs = tuple(itertools.product(ROOT_IDS, SIDES))
    for n in RECORD_COUNTS:
        yield from itertools.product(pairs, repeat=n)


def exhaustive_worlds() -> Iterator[dict[str, Any]]:
    """Every world inside the declared bounds, in a deterministic order."""
    index = 0
    status_ledgers = list(enumerate_status_ledgers())
    record_ledgers = list(enumerate_record_ledgers())
    for claim_type in CLAIM_TYPES:
        for statuses in status_ledgers:
            for records in record_ledgers:
                index += 1
                yield build_world(f"kl000-ex-{index}", claim_type, statuses, records)


def expected_exhaustive_count() -> int:
    """Recompute the declared count from the bounds themselves."""
    status_ledgers = sum(len(LOCATION_STATUSES) ** n for n in LOCATION_COUNTS)
    pair_count = len(ROOT_IDS) * len(SIDES)
    record_ledgers = sum(pair_count**n for n in RECORD_COUNTS)
    return status_ledgers * record_ledgers * len(CLAIM_TYPES)


def randomized_worlds(
    count: int = RANDOM_WORLD_COUNT, seed: int = RANDOM_SEED
) -> Iterator[dict[str, Any]]:
    """Frozen-seed worlds over the wider randomized bounds.

    Uses an explicit Random instance rather than the module-level generator so
    that unrelated code drawing from `random` cannot perturb the stream.
    """
    rng = random.Random(seed)
    lo_loc, hi_loc = RANDOM_LOCATION_RANGE
    lo_rec, hi_rec = RANDOM_RECORD_RANGE
    for index in range(1, count + 1):
        n_loc = rng.randint(lo_loc, hi_loc)
        statuses = tuple(rng.choice(LOCATION_STATUSES) for _ in range(n_loc))
        n_rec = rng.randint(lo_rec, hi_rec)
        records = tuple(
            (rng.choice(RANDOM_ROOT_POOL), rng.choice(SIDES)) for _ in range(n_rec)
        )
        claim_type = rng.choice(CLAIM_TYPES)
        yield build_world(f"kl000-rnd-{index}", claim_type, statuses, records)


def world_within_declared_bounds(world: dict[str, Any], phase: str) -> bool:
    """Guard against the generator silently leaving its own declared bounds."""
    locations = world["searchLedger"]["locations"]
    records = world["evidenceLedger"]["records"]
    if world["claim"]["type"] not in CLAIM_TYPES:
        return False
    if any(loc["status"] not in LOCATION_STATUSES for loc in locations):
        return False
    if any(rec["side"] not in SIDES for rec in records):
        return False
    if phase == "exhaustive":
        return (
            len(locations) in LOCATION_COUNTS
            and len(records) in RECORD_COUNTS
            and all(rec["rootId"] in ROOT_IDS for rec in records)
        )
    if phase == "randomized":
        return (
            RANDOM_LOCATION_RANGE[0] <= len(locations) <= RANDOM_LOCATION_RANGE[1]
            and RANDOM_RECORD_RANGE[0] <= len(records) <= RANDOM_RECORD_RANGE[1]
            and all(rec["rootId"] in RANDOM_ROOT_POOL for rec in records)
        )
    raise ValueError(f"unknown phase: {phase}")


def verify_bounds_against_preregistration(path: Path | None = None) -> list[str]:
    """Return a list of drifts between this module and the frozen protocol.

    An empty list means the code and the preregistration agree. This is checked
    at run start because a generator that has drifted from its own protocol
    produces results for an experiment nobody preregistered.
    """
    path = path or Path(__file__).resolve().parents[1] / "preregistration.json"
    prereg = json.loads(path.read_text())
    ex = prereg["population"]["exhaustive"]
    rnd = prereg["population"]["randomized"]
    frozen = prereg["frozenSeedsOrSplits"]

    checks = [
        ("locationCount", list(LOCATION_COUNTS), ex["locationCount"]),
        ("locationStatuses", list(LOCATION_STATUSES), ex["locationStatuses"]),
        ("recordCount", list(RECORD_COUNTS), ex["recordCount"]),
        ("rootIds", list(ROOT_IDS), ex["rootIds"]),
        ("sides", list(SIDES), ex["sides"]),
        ("claimTypes", list(CLAIM_TYPES), ex["claimTypes"]),
        ("declaredWorldCount", DECLARED_WORLD_COUNT, ex["declaredWorldCount"]),
        ("randomWorldCount", RANDOM_WORLD_COUNT, rnd["worldCount"]),
        ("randomLocationRange", list(RANDOM_LOCATION_RANGE), rnd["locationCountRange"]),
        ("randomRecordRange", list(RANDOM_RECORD_RANGE), rnd["recordCountRange"]),
        ("randomRootPool", list(RANDOM_ROOT_POOL), rnd["rootIdPool"]),
        ("randomSeed", RANDOM_SEED, frozen["randomizedSeed"]),
    ]
    drifts = [
        f"{name}: code={code!r} preregistration={preregistered!r}"
        for name, code, preregistered in checks
        if code != preregistered
    ]
    if expected_exhaustive_count() != DECLARED_WORLD_COUNT:
        drifts.append(
            f"derived exhaustive count {expected_exhaustive_count()} "
            f"!= declared {DECLARED_WORLD_COUNT}"
        )
    return drifts
