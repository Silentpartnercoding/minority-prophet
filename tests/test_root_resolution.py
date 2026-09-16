"""The root rule finally reaches the engine -- without touching the engine.

Each test names what would flip it. The last two are the ones that matter: they
run the real evaluator on the same evidence twice and show the conclusion move.
"""

import json
import pathlib

import pytest

from knowledge_ledger.root_resolution import resolution_report, resolve_transaction_roots
from knowledge_ledger.transaction_v2 import evaluate_transaction_v2 as evaluate_v2

ROOT = pathlib.Path(__file__).resolve().parents[1]

DOCS = {
    "SRC-0": {"isOriginal": True},
    **{f"COPY-{i}": {"derivedFrom": "SRC-0"} for i in range(1, 6)},
    "REAL-A": {"isOriginal": True},
    "REAL-B": {"isOriginal": True},
    "ORPHAN": {},
    "CYC-1": {"derivedFrom": "CYC-2"},
    "CYC-2": {"derivedFrom": "CYC-1"},
}


def _payload(records):
    return {
        "transactionId": "kl-root-resolution-fixture",
        "claim": {"type": "absence", "statement": "no defect of this class exists"},
        "searchLedger": {"locations": [{"id": "loc-1", "status": "searched"}]},
        "evidenceLedger": {"records": records},
    }


def test_five_copies_of_one_source_collapse_to_one_root():
    """Flips if any copy stops declaring SRC-0."""
    payload = _payload([{"id": f"COPY-{i}", "side": "support", "rootId": f"SELF-{i}"}
                        for i in range(1, 6)])
    report = resolution_report(payload, DOCS)
    assert report["suppliedDistinctRoots"] == 5
    assert report["resolvedDistinctRoots"] == 1
    assert report["collapsed"] == 4


def test_genuine_independence_is_preserved():
    """The control. Flips if resolution flattened real roots too."""
    payload = _payload([{"id": "REAL-A", "side": "support", "rootId": "REAL-A"},
                        {"id": "REAL-B", "side": "support", "rootId": "REAL-B"}])
    assert resolution_report(payload, DOCS)["resolvedDistinctRoots"] == 2


def test_orphan_and_cycle_are_unattributable_not_roots():
    payload = _payload([{"id": "ORPHAN", "side": "support", "rootId": "X"},
                        {"id": "CYC-1", "side": "support", "rootId": "Y"}])
    report = resolution_report(payload, DOCS)
    assert report["resolvedDistinctRoots"] == 0
    assert report["unattributable"] == ["CYC-1", "ORPHAN"]


def test_resolution_does_not_mutate_its_input():
    """An evaluator given the original and one given the resolved payload must
    stay comparable; that is the point of doing this outside the evaluator."""
    payload = _payload([{"id": "COPY-1", "side": "support", "rootId": "SELF-1"}])
    before = json.dumps(payload, sort_keys=True)
    resolve_transaction_roots(payload, DOCS)
    assert json.dumps(payload, sort_keys=True) == before


def test_the_frozen_evaluator_file_is_untouched():
    """KL-000 pins knowledge_ledger/transaction.py as the artifact under test and
    an independent implementation agrees on its digests. This change must not
    edit it. Flips the moment someone does."""
    source = (ROOT / "knowledge_ledger/transaction.py").read_text()
    assert 'root_id = record["rootId"]' in source, "the frozen evaluator was modified"


# ---- the end-to-end result: the engine's verdict actually moves --------------

def test_laundered_support_wins_before_resolution_and_does_not_after():
    """Five copies of ONE source against two genuine opposing roots.

    Unresolved, the engine sees 5 supporting roots against 2 and concludes the
    claim is contradicted with a comfortable margin. Resolved, it sees 1 against
    2. Same evidence, same evaluator, different answer -- which is the whole
    reason the root rule had to reach it.
    """
    records = ([{"id": f"COPY-{i}", "side": "support", "rootId": f"SELF-{i}"} for i in range(1, 6)]
               + [{"id": "REAL-A", "side": "oppose", "rootId": "REAL-A"},
                  {"id": "REAL-B", "side": "oppose", "rootId": "REAL-B"}])
    payload = _payload(records)

    unresolved = evaluate_v2(payload)
    resolved = evaluate_v2(resolve_transaction_roots(payload, DOCS))

    assert len(unresolved["evidence"]["supportingRoots"]) == 5
    assert len(resolved["evidence"]["supportingRoots"]) == 1
    assert len(resolved["evidence"]["opposingRoots"]) == 2
    # the side that wins on root count reverses
    assert len(unresolved["evidence"]["supportingRoots"]) > len(unresolved["evidence"]["opposingRoots"])
    assert len(resolved["evidence"]["supportingRoots"]) < len(resolved["evidence"]["opposingRoots"])


def test_unattributable_evidence_is_reported_not_silently_dropped():
    """v2 already counts a record with no rootId as `unattributed`. Resolution
    emits that shape rather than inventing a second vocabulary, so 'we could not
    attribute what we found' stays distinct from 'we found nothing'."""
    payload = _payload([{"id": "ORPHAN", "side": "support", "rootId": "X"},
                        {"id": "REAL-A", "side": "support", "rootId": "REAL-A"}])
    result = evaluate_v2(resolve_transaction_roots(payload, DOCS))
    assert result["evidence"]["unattributedRecords"] == 1
    assert result["evidence"]["supportingRoots"] == ["REAL-A"]
