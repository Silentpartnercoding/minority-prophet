"""KL-000 red-team suite: the ten attacks required before confirmation.

Two kinds of test live here and they are labelled, never blended:

`test_defends_*`   the evaluator resists the attack. A failure is a violation.
`test_limit_*`     the evaluator CANNOT resist, and the test pins the exposed
                   limit in place. These assert the weakness so that silently
                   losing it is a test failure, and so that fixing it forces a
                   deliberate protocol change rather than a quiet edit.

A `test_limit_*` passing is not reassurance. Each one names a real capability the
v0.1 schema does not have, and the most serious of them (A05) is an attack an
adversary controls entirely.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

EXPERIMENT = Path(__file__).resolve().parents[1]
REPO = EXPERIMENT.parents[3]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(EXPERIMENT / "src"))

from knowledge_ledger import evaluate_transaction  # noqa: E402
import kl000_worlds as worlds  # noqa: E402


def world(claim_type, statuses, records, tid="adv"):
    return worlds.build_world(tid, claim_type, tuple(statuses), tuple(records))


# === A01 unlimited paraphrased copies ====================================

def test_defends_a01_unlimited_paraphrased_copies():
    """1000 paraphrases of one source must remain one root with margin 1."""
    receipt = evaluate_transaction(
        world("absence", ["searched"] * 3, [("r1", "support")] * 1000))
    assert receipt["evidence"]["distinctRoots"] == 1
    assert receipt["evidence"]["margin"] == 1
    assert receipt["evidence"]["repeatedRecordsCollapsed"] == 999
    assert receipt["evidence"]["conversionsToReverse"] == 1


# === A02 circular citation / shared upstream source ======================

def test_limit_a02_shared_upstream_source_is_not_representable():
    """Two roots secretly derived from one upstream source count as two.

    Schema v0.1 has no dependency edge between roots. An evaluator cannot
    distinguish two genuinely independent roots from two that share an
    undeclared upstream ancestor. Collapsing them is the transaction author's
    responsibility, and nothing checks that they did it.
    """
    receipt = evaluate_transaction(
        world("absence", ["searched"] * 2,
              [("derived-a", "support"), ("derived-b", "support")]))
    assert receipt["evidence"]["distinctRoots"] == 2
    assert receipt["evidence"]["repeatedRecordsCollapsed"] == 0


# === A03 forged or replayed root receipts ================================

def test_limit_a03_no_issuer_authentication_exists():
    """rootId is an unauthenticated string. Forgery is free.

    There is no signature, issuer, or attestation field in v0.1, so a replayed
    or invented root receipt is indistinguishable from a genuine one. Identity
    would authenticate an issuer; it would still not prove causal independence.
    """
    honest = evaluate_transaction(
        world("absence", ["searched"], [("scanner-1", "support")]))
    forged = evaluate_transaction(
        world("absence", ["searched"], [("scanner-1-forged", "support")]))
    assert honest["evidence"]["distinctRoots"] == forged["evidence"]["distinctRoots"] == 1
    assert honest["conclusion"] == forged["conclusion"]


# === A04 one root on opposing sides ======================================

def test_defends_a04_one_root_on_opposing_sides_fails_closed():
    with pytest.raises(ValueError):
        evaluate_transaction(
            world("absence", ["searched"], [("r1", "support"), ("r1", "oppose")]))


def test_limit_a04b_side_conflict_is_a_denial_of_service_surface():
    """Fail-closed rejection is safe for truth and costly for availability.

    One injected record carrying an existing rootId with the opposite side makes
    the ENTIRE transaction unevaluable, rather than isolating the contradiction.
    An adversary who can append a single record can therefore suppress an
    otherwise valid conclusion. Safe, because no wrong answer is produced; not
    free, because silence can be the adversary's goal.
    """
    valid = [("r1", "support"), ("r2", "support"), ("r3", "oppose")]
    assert evaluate_transaction(world("absence", ["searched"] * 3, valid))
    with pytest.raises(ValueError):
        evaluate_transaction(
            world("absence", ["searched"] * 3, valid + [("r1", "oppose")]))


# === A05 unavailable and silently omitted search locations ===============

def test_defends_a05_declared_but_unavailable_location_blocks_absence():
    receipt = evaluate_transaction(
        world("absence", ["searched"] * 4 + ["unavailable"], [("r1", "support")]))
    assert receipt["conclusion"] == "not_established"


def test_limit_a05b_an_under_declared_search_space_is_undetectable():
    """THE MOST SERIOUS LIMIT IN THIS SUITE.

    Absence is admissible only inside a declared finite scope -- and the scope
    is declared by the same party that reports the evidence. An adversary who
    simply OMITS the location containing the counterexample gets a clean
    `absent_within_declared_scope`, and the receipt shows no trace of the
    omission: coverage reads 3/3 complete.

    Compare the honest ledger, which declares five locations and cannot reach
    absence, with the truncated one, which declares three and can. Both receipts
    are internally consistent, both verify their digests, and nothing in either
    reveals which is which.

    The bounded-absence invariant I2 is NOT violated: the conclusion really is
    bounded by the declared scope. The attack is on the declaration, which sits
    upstream of everything this evaluator can see.
    """
    honest = evaluate_transaction(
        world("absence", ["searched"] * 3 + ["unavailable"] * 2, [("r1", "support")]))
    truncated = evaluate_transaction(
        world("absence", ["searched"] * 3, [("r1", "support")]))

    assert honest["conclusion"] == "not_established"
    assert truncated["conclusion"] == "absent_within_declared_scope"
    assert truncated["search"] == {"declared": 3, "searched": 3,
                                    "unavailable": 0, "complete": True}
    # Nothing in the truncated receipt records that two locations ever existed.
    assert "omitted" not in str(truncated)


# === A06 counterexample hidden in an unsearched location =================

def test_limit_a06_records_carry_no_location_so_c09_and_c10_agree():
    """Preregistered as expected and permitted; see PROTOCOL.md.

    Safe direction: a counterexample refutes absence wherever it was found.
    Unsafe direction, and the real blind spot: a receipt may assert a location
    was `unavailable` while carrying evidence sourced from it, and this
    evaluator cannot detect the contradiction.
    """
    searched = evaluate_transaction(
        world("absence", ["searched"] * 3,
              [("r1", "support"), ("r2", "support"), ("r3", "oppose")]))
    unsearched = evaluate_transaction(
        world("absence", ["searched", "searched", "unavailable"],
              [("r1", "support"), ("r2", "support"), ("r3", "oppose")]))
    assert searched["conclusion"] == unsearched["conclusion"] == "present"
    assert searched["evidence"]["opposingRoots"] == unsearched["evidence"]["opposingRoots"]


# === A07 reordered, duplicated, delayed, partially failed messages =======

def test_defends_a07_reorder_and_duplication_change_nothing():
    records = [("r1", "support"), ("r2", "oppose"), ("r3", "support")]
    a = evaluate_transaction(world("absence", ["searched", "unavailable"], records))
    b = evaluate_transaction(
        world("absence", ["unavailable", "searched"], list(reversed(records))))
    assert a["contentDigest"] == b["contentDigest"]


def test_limit_a07b_delay_and_partial_failure_are_not_modelled():
    """v0.1 evaluates one complete payload. There is no transport layer, so
    delayed, dropped, or partially delivered messages have no representation.
    A partially delivered ledger is simply a smaller ledger -- which is exactly
    the A05b attack arriving by accident rather than by malice."""
    partial = evaluate_transaction(world("absence", ["searched"], [("r1", "support")]))
    assert partial["conclusion"] == "absent_within_declared_scope"


# === A08 one compromised issuer minting many roots =======================

def test_limit_a08_one_issuer_can_mint_unlimited_roots():
    """Root identity is operationally declared, so a single compromised issuer
    minting eight distinct rootIds produces eight independent roots and a margin
    of 8. Copy invariance does not help: these are not copies, they are
    fabrications, and the evaluator has no issuer field to attribute them to.

    This is the quantified cost of PUBLIC-CLAIMS.md's stated boundary that
    'root identity is operationally assigned, not semantically proved'.
    """
    minted = [(f"sybil-{i}", "support") for i in range(8)]
    receipt = evaluate_transaction(world("absence", ["searched"] * 2, minted))
    assert receipt["evidence"]["distinctRoots"] == 8
    assert receipt["evidence"]["margin"] == 8
    assert receipt["evidence"]["conversionsToReverse"] == 5


# === A09 ambiguous root identity and partial dependence ==================

@pytest.mark.parametrize("a,b", [
    ("r1", "r1 "), ("r1", "R1"), ("r1", "r１"), ("scanner", "scanner​"),
])
def test_limit_a09_near_identical_root_ids_are_distinct_roots(a, b):
    """Trailing space, case, a fullwidth digit, a zero-width space: each yields
    two roots from what a human reader would call one source. No normalisation
    is specified, so root identity is byte identity."""
    receipt = evaluate_transaction(
        world("absence", ["searched"], [(a, "support"), (b, "support")]))
    assert receipt["evidence"]["distinctRoots"] == 2


# === A10 malformed, oversized, schema-valid-but-misleading ===============

@pytest.mark.parametrize("payload", [
    {"transactionId": "t", "claim": {"type": "absence"},
     "searchLedger": {"locations": [{"id": "a", "status": "searched"}]},
     "evidenceLedger": {"records": [{"id": "r", "rootId": ["unhashable"], "side": "support"}]}},
    {"transactionId": "t", "claim": {},
     "searchLedger": {"locations": [{"id": "a", "status": "searched"}]},
     "evidenceLedger": {"records": []}},
    {"transactionId": "t", "claim": {"type": "absence"},
     "searchLedger": {"locations": "not-a-list"},
     "evidenceLedger": {"records": []}},
])
def test_defends_a10_malformed_input_fails_closed(payload):
    with pytest.raises(Exception):
        evaluate_transaction(payload)


def test_defends_a10b_oversized_input_stays_correct():
    """5,000 records over 3 roots: counts stay exact, no overflow, no timeout."""
    records = [(f"r{i % 3}", "support") for i in range(5000)]
    receipt = evaluate_transaction(world("absence", ["searched"] * 2, records))
    assert receipt["evidence"]["records"] == 5000
    assert receipt["evidence"]["distinctRoots"] == 3
    assert receipt["evidence"]["repeatedRecordsCollapsed"] == 4997


def test_limit_a10c_schema_valid_but_misleading_proposition():
    """The proposition is free text and is never checked against the ledgers.

    A receipt may claim to have searched for one thing while its search ledger
    describes another. The evaluator binds the conclusion to the ledgers, not to
    the sentence a human will actually read.
    """
    receipt = evaluate_transaction({
        "transactionId": "misleading",
        "claim": {"type": "absence",
                  "proposition": "No defect exists anywhere in the world."},
        "searchLedger": {"locations": [{"id": "one-file", "status": "searched"}]},
        "evidenceLedger": {"records": []},
    })
    assert receipt["conclusion"] == "absent_within_declared_scope"
    assert receipt["search"]["declared"] == 1
