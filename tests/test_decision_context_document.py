"""Reading the decision-context document form, which nothing ever parsed.

`provenance/decision-context.schema.json` has existed since v0.1. Every decision
this corpus has scored was scored on a `DecisionContext` built in Python by an
experiment harness — `experiments/dri1`, `dri2`, `dri3`, `dri8`, `dri9`. The
declared document form, the one an outside caller would actually send, had no
reader at all.

The loader lives in its own module because `decision_relative` is a pinned
frozen input of nine preregistered experiments. See
`provenance/decision_context_document.py` for why re-deriving those pins would
have been worse than the failure that suggested it.
"""

from __future__ import annotations

import json
import pathlib

import pytest

from provenance.decision_context_document import (
    DECISION_CONTEXT_SCHEMA,
    decision_context_from_document,
)
from provenance.decision_relative import DecisionContextError

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "provenance" / "decision-context.schema.json"


def document(**overrides):
    base = {
        "schema": DECISION_CONTEXT_SCHEMA,
        "decision_id": "decision-1",
        "proposition_id": "prop-1",
        "failure_domain": "sensor-calibration",
        "independence_cut": "machine",
        "minimum_winning_roots": 2,
        "consequence": "reversible",
        "reversibility": "reversible",
        "cut_selection_basis": "preregistered",
    }
    base.update(overrides)
    return {k: v for k, v in base.items() if v is not _OMIT}


_OMIT = object()


def test_a_well_formed_document_loads():
    context = decision_context_from_document(document())
    assert context.decision_id == "decision-1"
    assert context.minimum_winning_roots == 2
    assert context.cut_selection_basis == "preregistered"


def test_the_selected_cut_is_always_a_candidate():
    """The dataclass folds the selected cut into the candidate list. A document
    that names alternatives must not lose the cut actually in force."""
    context = decision_context_from_document(
        document(candidate_cuts=["controller", "evidence_origin"])
    )
    assert context.candidate_cuts[0] == "machine"
    assert set(context.candidate_cuts) == {"machine", "controller", "evidence_origin"}


def test_required_document_fields_are_enforced():
    """`consequence` and `reversibility` carry Python defaults for in-process
    callers, but the document requires them. Defaulting them while reading a
    document would invent the declaration rather than read it."""
    for field in ("consequence", "reversibility", "failure_domain", "decision_id"):
        with pytest.raises(DecisionContextError, match="requires"):
            decision_context_from_document(document(**{field: _OMIT}))


def test_unknown_keys_are_refused():
    """`additionalProperties: false`. Silently ignoring a key would discard a
    policy fact the caller believed it had declared."""
    with pytest.raises(DecisionContextError, match="unpermitted"):
        decision_context_from_document(document(independence_cutt="machine"))


def test_wrong_schema_is_refused():
    with pytest.raises(DecisionContextError, match="unsupported"):
        decision_context_from_document(document(schema="something.else.v1"))


def test_a_boolean_is_not_a_threshold():
    """`isinstance(True, int)` is True in Python, so an unguarded read turns
    `true` into a minimum of one — a real threshold, silently."""
    with pytest.raises(DecisionContextError, match="must be an integer"):
        decision_context_from_document(document(minimum_winning_roots=True))


def test_threshold_below_one_is_refused():
    with pytest.raises(DecisionContextError, match="at least 1"):
        decision_context_from_document(document(minimum_winning_roots=0))


def test_unsupported_cut_selection_basis_is_refused():
    with pytest.raises(DecisionContextError, match="cut_selection_basis"):
        decision_context_from_document(document(cut_selection_basis="vibes"))


def test_candidate_cuts_must_be_a_list_not_a_string():
    """A bare string is iterable, and would silently become one cut per
    character."""
    with pytest.raises(DecisionContextError, match="array of strings"):
        decision_context_from_document(document(candidate_cuts="controller"))


def test_duplicate_candidate_cuts_are_refused():
    with pytest.raises(DecisionContextError, match="unique"):
        decision_context_from_document(
            document(candidate_cuts=["controller", "controller"])
        )


def test_non_object_is_refused():
    with pytest.raises(DecisionContextError, match="must be an object"):
        decision_context_from_document(["decision-1"])


# --- agreement with the published schema ---------------------------------


def test_loader_agrees_with_the_schema_document():
    """The loader's vocabulary is derived from a schema file that ships beside
    it. If the schema gains a field and the loader does not, a caller's declared
    policy fact would be refused as an unknown key."""
    from provenance.decision_context_document import CONTEXT_KEYS, CONTEXT_REQUIRED

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert set(schema["properties"]) == set(CONTEXT_KEYS)
    assert set(schema["required"]) == set(CONTEXT_REQUIRED)
    assert schema["properties"]["schema"]["const"] == DECISION_CONTEXT_SCHEMA


def test_every_schema_enum_value_is_accepted():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    for basis in schema["properties"]["cut_selection_basis"]["enum"]:
        context = decision_context_from_document(document(cut_selection_basis=basis))
        assert context.cut_selection_basis == basis
