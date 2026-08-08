"""KL-000 property tests: copy invariance, side separation, bounded absence,
deterministic replay, fail-closed parsing.

These are the permanent suite. They run in CI-time (seconds), unlike the
confirmatory enumeration, and they must never be narrowed to hide a
counterexample.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

EXPERIMENT = Path(__file__).resolve().parents[1]
REPO = EXPERIMENT.parents[3]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(EXPERIMENT / "src"))

from knowledge_ledger import evaluate_transaction  # noqa: E402
from knowledge_ledger.transaction import verify_content_digest  # noqa: E402

import kl000_worlds as worlds  # noqa: E402
from kl000_baselines import BASELINES  # noqa: E402
from kl000_invariants import check_world  # noqa: E402


def world(claim_type, statuses, records, tid="t"):
    return worlds.build_world(tid, claim_type, tuple(statuses), tuple(records))


# --- copy invariance (I1, I10) -------------------------------------------

def test_twenty_copies_of_one_source_remain_one_root():
    """KL-002's first gate, expressed at conformance level."""
    one = world("absence", ["searched"], [("r1", "support")])
    twenty = world("absence", ["searched"], [("r1", "support")] * 20)
    a, b = evaluate_transaction(one), evaluate_transaction(twenty)
    assert b["evidence"]["distinctRoots"] == 1
    assert b["evidence"]["records"] == 20
    assert b["evidence"]["repeatedRecordsCollapsed"] == 19
    assert b["evidence"]["margin"] == a["evidence"]["margin"] == 1
    assert b["conclusion"] == a["conclusion"]


@pytest.mark.parametrize("copies", [1, 2, 5, 50, 500])
def test_copy_count_never_changes_evidential_mass(copies):
    base = world("absence", ["searched", "unavailable"],
                 [("r1", "support"), ("r2", "support")])
    more = world("absence", ["searched", "unavailable"],
                 [("r1", "support")] * copies + [("r2", "support")])
    a, b = evaluate_transaction(base), evaluate_transaction(more)
    for field in ("distinctRoots", "supportingRoots", "opposingRoots",
                  "margin", "conversionsToReverse"):
        assert a["evidence"][field] == b["evidence"][field], field
    assert a["conclusion"] == b["conclusion"]


# --- bounded absence (I2, I5) --------------------------------------------

@pytest.mark.parametrize("status", ["unavailable", "failed", "not_searched", "pending", ""])
def test_absence_unreachable_while_any_location_is_not_searched(status):
    receipt = evaluate_transaction(
        world("absence", ["searched", status], [("r1", "support")]))
    assert receipt["conclusion"] == "not_established"
    assert receipt["search"]["complete"] is False


def test_absence_permitted_only_under_complete_coverage():
    receipt = evaluate_transaction(
        world("absence", ["searched"] * 4, [("r1", "support")]))
    assert receipt["conclusion"] == "absent_within_declared_scope"
    assert receipt["search"]["complete"] is True


def test_one_counterexample_outranks_any_amount_of_support():
    receipt = evaluate_transaction(
        world("absence", ["searched"] * 3,
              [("r1", "support")] * 100 + [("r9", "oppose")]))
    assert receipt["conclusion"] == "present"


def test_counterexample_dominates_even_at_incomplete_coverage():
    receipt = evaluate_transaction(
        world("absence", ["unavailable"] * 5, [("r9", "oppose")]))
    assert receipt["conclusion"] == "present"


# --- side separation (I3) -------------------------------------------------

def test_one_root_on_both_sides_fails_closed():
    with pytest.raises(ValueError, match="opposing sides"):
        evaluate_transaction(
            world("absence", ["searched"], [("r1", "support"), ("r1", "oppose")]))


# --- deterministic replay (I4) and digest integrity (I6) ------------------

def test_replay_is_byte_identical():
    w = world("absence", ["searched", "unavailable"],
              [("r1", "support"), ("r2", "oppose")])
    a = json.dumps(evaluate_transaction(w), sort_keys=True)
    b = json.dumps(evaluate_transaction(w), sort_keys=True)
    assert a == b


def test_every_receipt_self_verifies():
    w = world("absence", ["searched"] * 2, [("r1", "support")])
    assert verify_content_digest(evaluate_transaction(w))


@pytest.mark.parametrize("field,value", [
    ("conclusion", "absent_within_declared_scope"),
    ("reason", "tampered"),
    ("transactionId", "other"),
])
def test_single_field_mutation_breaks_the_digest(field, value):
    receipt = evaluate_transaction(world("absence", ["unavailable"], [("r1", "support")]))
    receipt[field] = value
    assert not verify_content_digest(receipt)


# --- order invariance (I7) -----------------------------------------------

def test_permutation_changes_nothing_including_the_digest():
    records = [("r1", "support"), ("r2", "support"), ("r3", "oppose")]
    a = evaluate_transaction(world("absence", ["searched", "unavailable"], records))
    b = evaluate_transaction(world("absence", ["unavailable", "searched"],
                                   list(reversed(records))))
    assert a["contentDigest"] == b["contentDigest"]


# --- fail-closed parsing (I9) --------------------------------------------

@pytest.mark.parametrize("payload", [
    {},
    {"transactionId": "t"},
    {"transactionId": "t", "claim": {"type": "absence"},
     "searchLedger": {"locations": []}, "evidenceLedger": {"records": []}},
    {"transactionId": "t", "claim": {"type": "absence"},
     "searchLedger": {"locations": [{"id": "a", "status": "searched"},
                                     {"id": "a", "status": "searched"}]},
     "evidenceLedger": {"records": []}},
    {"transactionId": "t", "claim": {"type": "absence"},
     "searchLedger": {"locations": [{"id": "a", "status": "searched"}]},
     "evidenceLedger": {"records": [{"id": "r", "rootId": "r1", "side": "maybe"}]}},
    {"transactionId": "t", "claim": {"type": "absence"},
     "searchLedger": {"locations": [{"id": "a"}]},
     "evidenceLedger": {"records": []}},
])
def test_malformed_input_raises_and_never_concludes(payload):
    with pytest.raises(Exception):
        evaluate_transaction(payload)


# --- power of the test: the ablated baselines must be caught --------------

@pytest.mark.parametrize("name", sorted(BASELINES))
def test_every_ablated_baseline_is_caught(name):
    """If this fails, the invariant suite is vacuous and KL-000 is invalid."""
    evaluate = BASELINES[name]
    violations = []
    for i, w in enumerate(worlds.exhaustive_worlds()):
        if i >= 3000:
            break
        violations.extend(check_world(evaluate, w))
    assert violations, f"{name} passed the invariant suite; the suite proves nothing"


def test_real_evaluator_clears_the_same_sample_the_baselines_fail():
    violations = []
    for i, w in enumerate(worlds.exhaustive_worlds()):
        if i >= 3000:
            break
        violations.extend(check_world(evaluate_transaction, w))
    assert violations == []


# --- generator integrity --------------------------------------------------

def test_generator_matches_its_own_preregistration():
    assert worlds.verify_bounds_against_preregistration() == []


def test_declared_world_count_is_derivable_not_asserted():
    assert worlds.expected_exhaustive_count() == worlds.DECLARED_WORLD_COUNT == 176120
