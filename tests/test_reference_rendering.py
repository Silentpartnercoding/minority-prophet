"""The human-readable rendering must never contradict its own receipt.

The first version of `render_transmission` wrote its numbers into the prose as
literal text — "Five rooms were named. Four opened their doors" — while
interpolating the receipt block underneath. The two agreed only for the one
fixture it was written against. It was also titled "First Transmission" and
said "This is the first transmission", for a receipt whose own README states
that `reference-conformance-001` "is not a cross-system result".

Prose is the part a reader trusts. These tests hold it to the receipt.
"""

import importlib.util
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "run_knowledge_transaction",
    Path(__file__).resolve().parents[1] / "scripts" / "run_knowledge_transaction.py",
)
RKT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RKT)


def flat(text: str) -> str:
    """Collapse wrapping before asserting on wording.

    The renderer wraps prose to 78 columns, so a phrase under test can arrive
    split across a newline ("A\ncounterexample was found"). Asserting on raw
    substrings makes the test sensitive to line breaks rather than to meaning,
    which is the opposite of what it is for.
    """
    return " ".join(text.split())


def receipt(**overrides):
    base = {
        "transactionId": "t-test",
        "conclusion": "not_established",
        "contentDigest": "sha256:test",
        "search": {"declared": 5, "searched": 4, "unavailable": 1},
        "evidence": {"records": 4, "distinctRoots": 2},
    }
    base.update(overrides)
    return base


def test_prose_counts_follow_the_receipt():
    text = RKT.render_transmission(
        receipt(search={"declared": 3, "searched": 3, "unavailable": 0},
                evidence={"records": 6, "distinctRoots": 2})
    )
    assert "Three rooms were named." in text
    assert "Three opened their doors." in text
    assert "None remained beyond our reach." in text
    # The literal fixture numbers must not survive into a different world.
    assert "Five rooms" not in text
    assert "Four opened" not in text


def test_a_counterexample_is_never_described_as_no_contradiction():
    # Keyed on coverage alone, the caveat wrote "No contradiction was found"
    # onto a `present` receipt — denying the counterexample recorded two lines
    # below it in the same document.
    text = RKT.render_transmission(receipt(conclusion="present"))
    assert "No contradiction was found" not in flat(text)
    assert "A counterexample was found" in flat(text)
    assert "**Present.**" in text
    assert "does not declare victory" not in flat(text)


def test_absence_within_scope_states_its_boundary():
    text = RKT.render_transmission(
        receipt(conclusion="absent_within_declared_scope",
                search={"declared": 4, "searched": 4, "unavailable": 0})
    )
    assert "**Absent within the declared scope.**" in text
    assert "bounded by that declaration" in flat(text)


def test_singular_and_plural_track_the_values():
    text = RKT.render_transmission(
        receipt(search={"declared": 2, "searched": 1, "unavailable": 1},
                evidence={"records": 1, "distinctRoots": 1})
    )
    assert "One opened its door." in text
    assert "One voice answered" in flat(text)
    assert "held it apart as one independent root" in flat(text)
    assert "the unopened door still matters" in flat(text)


def test_collapsed_records_are_distinguished_from_independent_ones():
    collapsed = RKT.render_transmission(receipt(evidence={"records": 4, "distinctRoots": 2}))
    assert "lineage drew them back to two independent roots" in flat(collapsed)

    independent = RKT.render_transmission(receipt(evidence={"records": 4, "distinctRoots": 4}))
    assert "held them apart as four independent roots" in flat(independent)
    # Agreement that survives lineage is not the same finding as agreement that
    # collapses, and the sentence must not read identically for both.
    assert "drew them back" not in flat(independent)


def test_the_rendering_does_not_claim_the_milestone():
    text = RKT.render_transmission(receipt())
    assert text.startswith("# Reference Conformance Rendering")
    assert "First Transmission" not in text
    assert "this is the first transmission" not in text.lower()
    assert "rendering, not a milestone" in flat(text)
    assert "does not promote" in flat(text)


def test_numerals_stay_lowercase_mid_sentence():
    text = RKT.render_transmission(receipt())
    # "back to Two independent roots" reads as a typo and undercuts the care
    # the rest of the document is claiming.
    assert "to Two independent" not in flat(text)
    assert "as Four independent" not in flat(text)


@pytest.mark.parametrize("count", [13, 40, 250])
def test_large_counts_stay_exact_rather_than_spelled(count):
    text = RKT.render_transmission(
        receipt(search={"declared": count, "searched": count, "unavailable": 0},
                evidence={"records": count, "distinctRoots": count})
    )
    assert f"{count} rooms were named." in text
