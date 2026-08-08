"""flip_budget presentation (RUN-20260807-10): the R3 metric surfaced with
every verdict, derived, with the receipt untouched -- and proven untouched.

Pass condition from the registration (KL-000/FLIP-BUDGET-PRESENTATION.md):
C11 and C12 reproduce byte-for-byte with the presentation module in use.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
KL000 = REPO / "research" / "knowledge-ledger" / "experiments" / "KL-000"
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(KL000 / "src"))

from knowledge_ledger.presentation import derive_flip_budget, reversal_metrics  # noqa: E402
from knowledge_ledger.transaction import evaluate_transaction  # noqa: E402

PREREG = json.loads((KL000 / "preregistration-v1.3.0.json").read_text())


def _fixture(rel):
    return json.loads((KL000 / rel).read_text())


def test_c11_and_c12_still_reproduce_byte_for_byte_with_presentation_loaded():
    """The registered pass condition: the pins hold with this module in use."""
    for rel in ("fixtures/v1.2.0/c11-canonical-digest.json",
                "fixtures/v1.2.0/c12-margin-sign.json"):
        doc = _fixture(rel)
        receipt = evaluate_transaction(doc["input"])
        reversal_metrics(receipt)  # exercised BEFORE comparison, deliberately
        assert receipt["contentDigest"] == doc["expected"]["contentDigest"], rel
        assert sorted(receipt.keys()) == sorted(
            ["schema", "transactionId", "claim", "search", "evidence",
             "conclusion", "reason", "limits", "contentDigest"]
        ), f"{rel}: receipt member set changed"


def test_frozen_hashes_unchanged():
    expected = PREREG["evaluatorUnderTest"]
    assert hashlib.sha256((REPO / "knowledge_ledger" / "transaction.py").read_bytes()).hexdigest() == expected["sha256"]
    assert hashlib.sha256((REPO / "knowledge_ledger" / "__init__.py").read_bytes()).hexdigest() == expected["packageInitSha256"]


def test_derivation_equals_margin_on_every_registered_fixture():
    for control in PREREG["controls"]:
        doc = _fixture(control["fixture"])
        receipt = evaluate_transaction(doc["input"])
        assert derive_flip_budget(receipt) == receipt["evidence"]["margin"], control["id"]


def test_derivation_equals_margin_across_an_exhaustive_sample():
    import kl000_worlds as worlds
    checked = 0
    for world in worlds.exhaustive_worlds():
        if checked >= 2000:
            break
        try:
            receipt = evaluate_transaction(world)
        except Exception:
            continue
        checked += 1
        assert derive_flip_budget(receipt) == receipt["evidence"]["margin"]
    assert checked == 2000


def test_ce03_both_metrics_always_paired_with_units():
    doc = _fixture("fixtures/v1.2.0/c12-margin-sign.json")
    metrics = reversal_metrics(evaluate_transaction(doc["input"]))
    assert metrics["flipBudget"] == 1
    assert metrics["conversionsToReverse"] == 1
    assert "net per-side root gain" in metrics["flipBudgetUnits"]
    assert "side-conversion actions" in metrics["conversionsToReverseUnits"]
    assert "CE-03" in metrics["note"]


def test_ce03_no_lone_flip_budget_presentation_exists():
    """The module's public surface pairs the metrics; derive_flip_budget is
    the arithmetic, reversal_metrics the only presentation."""
    import inspect

    import knowledge_ledger.presentation as presentation
    public = [n for n, obj in vars(presentation).items()
              if not n.startswith("_") and inspect.isfunction(obj)
              and obj.__module__ == presentation.__name__]
    assert sorted(public) == ["derive_flip_budget", "reversal_metrics"]
