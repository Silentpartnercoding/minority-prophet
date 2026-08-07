"""KL-000 invariant checking.

Checks the ten hard invariants of protocol v1.0.0 against *any* evaluator with
the signature `evaluate(payload) -> receipt`. It is written against that
interface rather than against `knowledge_ledger.evaluate_transaction`
specifically, so the same checker can be pointed at the ablated baselines. That
is what makes the power-of-the-test claim meaningful: the baselines are caught
by the identical code path that clears the real evaluator, not by a separate
one written to catch them.

A violation is a *finding*, never an exception. The checker returns them so the
runner can preserve the offending world verbatim.
"""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Callable, NamedTuple

Evaluator = Callable[[dict[str, Any]], dict[str, Any]]

EVIDENCE_INVARIANT_FIELDS = (
    "distinctRoots",
    "supportingRoots",
    "opposingRoots",
    "margin",
    "conversionsToReverse",
)


class Violation(NamedTuple):
    invariant: str
    detail: str
    world: dict[str, Any]


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()


def _digest_of(receipt: dict[str, Any]) -> str:
    unsigned = {k: v for k, v in receipt.items() if k != "contentDigest"}
    return "sha256:" + hashlib.sha256(canonical_bytes(unsigned)).hexdigest()


def _distinct_declared_roots(world: dict[str, Any]) -> set[str]:
    return {r["rootId"] for r in world["evidenceLedger"]["records"]}


def _inadmissibility(world: dict[str, Any]) -> str | None:
    """v1.1.0 admissibility: the correct outcome for these worlds is refusal.

    Returns the invariant a receipt would violate, or None for an admissible
    world. Neither generator emits an inadmissible world (the declared bounds
    require locationCount >= 1 and enumerate distinct location ids), so on the
    enumerated and randomized phases this is exercised zero times and changes
    no count; it is load-bearing only for adversarial input.
    """
    locations = world["searchLedger"]["locations"]
    if not locations:
        return "I8"  # R2: complete requires declared > 0; empty scope refuses
    ids = [location["id"] for location in locations]
    if len(ids) != len(set(ids)):
        return "I11"  # R3: duplicate location ids refuse
    return None


def _expected_conclusion_and_margin(world: dict[str, Any]) -> tuple[str, int]:
    """The registered conclusionFunction and R5.2 margin, computed from the
    WORLD's ledgers and never from receipt fields (v1.3.0 I12).

    Admissibility is not re-checked here: check_world only reaches I12 for
    worlds whose receipt exists, and inadmissible worlds return earlier.
    """
    sides: dict[str, str] = {}
    for record in world["evidenceLedger"]["records"]:
        sides.setdefault(record["rootId"], record["side"])
    supporting = sum(1 for side in sides.values() if side == "support")
    opposing = len(sides) - supporting
    margin = abs(supporting - opposing)
    locations = world["searchLedger"]["locations"]
    complete = bool(locations) and all(loc["status"] == "searched" for loc in locations)
    if world["claim"]["type"] == "absence":
        if opposing:
            conclusion = "present"
        elif complete:
            conclusion = "absent_within_declared_scope"
        else:
            conclusion = "not_established"
    else:
        conclusion = "supported" if supporting > opposing else "not_established"
    return conclusion, margin


def _has_root_on_both_sides(world: dict[str, Any]) -> bool:
    sides: dict[str, str] = {}
    for record in world["evidenceLedger"]["records"]:
        previous = sides.setdefault(record["rootId"], record["side"])
        if previous != record["side"]:
            return True
    return False


def check_world(evaluate: Evaluator, world: dict[str, Any]) -> list[Violation]:
    """Check every applicable invariant against one world.

    Worlds that must fail closed (a root on opposing sides) are checked for I3
    and then skipped: an evaluator that correctly refuses to produce a receipt
    has no receipt for the remaining invariants to inspect.
    """
    violations: list[Violation] = []
    expect_closed = _has_root_on_both_sides(world)
    inadmissible_as = _inadmissibility(world)

    # --- I3 side separation, admissibility, and the fail-closed path ------
    try:
        receipt = evaluate(copy.deepcopy(world))
    except Exception as exc:  # noqa: BLE001 - any refusal is fail-closed
        if not expect_closed and inadmissible_as is None:
            violations.append(
                Violation("I9", f"unexpected refusal: {type(exc).__name__}: {exc}", world)
            )
        return violations

    if inadmissible_as is not None:
        violations.append(
            Violation(
                inadmissible_as,
                "inadmissible world (v1.1.0 "
                + ("R2: empty declared scope" if inadmissible_as == "I8"
                   else "R3/I11: duplicate location id")
                + ") yet a receipt was produced: "
                f"conclusion={receipt.get('conclusion')!r}",
                world,
            )
        )
        return violations

    if expect_closed:
        violations.append(
            Violation(
                "I3",
                "a root appears on both sides yet a receipt was produced: "
                f"conclusion={receipt.get('conclusion')!r}",
                world,
            )
        )
        return violations

    search = receipt["search"]
    evidence = receipt["evidence"]
    locations = world["searchLedger"]["locations"]
    records = world["evidenceLedger"]["records"]
    claim_type = world["claim"]["type"]

    # --- I8 search arithmetic --------------------------------------------
    declared = len(locations)
    searched = sum(loc["status"] == "searched" for loc in locations)
    unavailable = sum(loc["status"] == "unavailable" for loc in locations)
    if search["declared"] != declared:
        violations.append(Violation("I8", f"declared {search['declared']} != {declared}", world))
    if search["searched"] != searched:
        violations.append(Violation("I8", f"searched {search['searched']} != {searched}", world))
    if search["unavailable"] != unavailable:
        violations.append(
            Violation("I8", f"unavailable {search['unavailable']} != {unavailable}", world)
        )
    if search["searched"] + search["unavailable"] > search["declared"]:
        violations.append(Violation("I8", "searched + unavailable exceeds declared", world))
    if search["complete"] != (searched == declared):
        violations.append(
            Violation("I8", f"complete={search['complete']} but searched={searched}/{declared}", world)
        )

    # --- I2 bounded absence ----------------------------------------------
    if receipt["conclusion"] == "absent_within_declared_scope":
        if not search["complete"]:
            violations.append(
                Violation("I2", "absence concluded while search incomplete", world)
            )
        if evidence["opposingRoots"]:
            violations.append(
                Violation("I2", "absence concluded despite an opposing root", world)
            )
        if searched != declared:
            violations.append(
                Violation("I2", f"absence concluded at coverage {searched}/{declared}", world)
            )

    # --- I12 decision enforcement (v1.3.0) ---------------------------------
    # World-referential: both quantities derive from the world, never the
    # receipt. At most one violation per world, so caught-counts equal world
    # counts and the registered ablation surfaces (22,440 / 38,760) are
    # exact-match targets.
    expected_conclusion, expected_margin = _expected_conclusion_and_margin(world)
    i12_details = []
    if receipt["conclusion"] != expected_conclusion:
        i12_details.append(
            f"conclusion {receipt['conclusion']!r} != {expected_conclusion!r}"
        )
    if evidence["margin"] != expected_margin:
        i12_details.append(f"margin {evidence['margin']!r} != {expected_margin}")
    if i12_details:
        violations.append(Violation("I12", "; ".join(i12_details), world))

    # --- I5 counterexample dominance --------------------------------------
    if claim_type == "absence" and evidence["opposingRoots"]:
        if receipt["conclusion"] != "present":
            violations.append(
                Violation(
                    "I5",
                    f"opposing root present but conclusion={receipt['conclusion']!r}",
                    world,
                )
            )

    # --- I10 copies never mint roots --------------------------------------
    declared_roots = _distinct_declared_roots(world)
    if evidence["distinctRoots"] != len(declared_roots):
        violations.append(
            Violation(
                "I10",
                f"distinctRoots {evidence['distinctRoots']} != {len(declared_roots)} declared",
                world,
            )
        )
    if evidence["records"] != len(records):
        violations.append(
            Violation("I10", f"records {evidence['records']} != {len(records)}", world)
        )
    if evidence["repeatedRecordsCollapsed"] != len(records) - len(declared_roots):
        violations.append(
            Violation("I10", "repeatedRecordsCollapsed inconsistent with roots", world)
        )

    # --- I6 digest integrity ----------------------------------------------
    if receipt.get("contentDigest") != _digest_of(receipt):
        violations.append(Violation("I6", "contentDigest does not verify", world))
    else:
        mutated = copy.deepcopy(receipt)
        mutated["conclusion"] = mutated["conclusion"] + "-tampered"
        if mutated.get("contentDigest") == _digest_of(mutated):
            violations.append(Violation("I6", "mutation not detected by digest", world))

    # --- I4 deterministic replay ------------------------------------------
    replay = evaluate(copy.deepcopy(world))
    if canonical_bytes(replay) != canonical_bytes(receipt):
        violations.append(Violation("I4", "replay differed from first evaluation", world))

    # --- I7 order invariance ----------------------------------------------
    # Checked for every world, including record-free ones: reversing the search
    # ledger is meaningful even when there is no evidence to reverse.
    permuted = copy.deepcopy(world)
    permuted["evidenceLedger"]["records"] = list(reversed(permuted["evidenceLedger"]["records"]))
    permuted["searchLedger"]["locations"] = list(reversed(permuted["searchLedger"]["locations"]))
    permuted_receipt = evaluate(permuted)
    if permuted_receipt["conclusion"] != receipt["conclusion"]:
        violations.append(Violation("I7", "conclusion changed under permutation", world))
    for field in EVIDENCE_INVARIANT_FIELDS:
        if permuted_receipt["evidence"][field] != evidence[field]:
            violations.append(Violation("I7", f"{field} changed under permutation", world))
    if permuted_receipt.get("contentDigest") != receipt.get("contentDigest"):
        violations.append(Violation("I7", "contentDigest changed under permutation", world))

    # --- I1 copy invariance ------------------------------------------------
    if records:
        copied = copy.deepcopy(world)
        duplicate = copy.deepcopy(records[0])
        duplicate["id"] = duplicate["id"] + "-copy"
        copied["evidenceLedger"]["records"].append(duplicate)
        copied_receipt = evaluate(copied)
        copied_evidence = copied_receipt["evidence"]

        if copied_receipt["conclusion"] != receipt["conclusion"]:
            violations.append(
                Violation(
                    "I1",
                    f"conclusion changed {receipt['conclusion']!r} -> "
                    f"{copied_receipt['conclusion']!r} on adding one copy",
                    world,
                )
            )
        for field in EVIDENCE_INVARIANT_FIELDS:
            if copied_evidence[field] != evidence[field]:
                violations.append(
                    Violation(
                        "I1",
                        f"{field} changed {evidence[field]!r} -> "
                        f"{copied_evidence[field]!r} on adding one copy",
                        world,
                    )
                )
        if copied_evidence["records"] != evidence["records"] + 1:
            violations.append(Violation("I1", "records did not increase by exactly 1", world))
        if copied_evidence["repeatedRecordsCollapsed"] != evidence["repeatedRecordsCollapsed"] + 1:
            violations.append(
                Violation("I1", "repeatedRecordsCollapsed did not increase by exactly 1", world)
            )

    return violations
