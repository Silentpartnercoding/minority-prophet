"""The warrant field that was never written to, finally written to.

`verify_outcome` has been in claim-warrant.schema.json since before the
dereference gate existed, and nothing had ever set it. These tests hold the
translation to the schema's own stated rules, especially the one it is most
emphatic about: `unverifiable` must never become `rejected`.
"""

import json
import pathlib
import sys
from datetime import datetime, timezone

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from provenance.graph import WARRANT_KEY, EvidenceGraph, EvidenceNode  # noqa: E402
from provenance.warrant_recheck import attach_recheck, recheck_outcome, recheck_report  # noqa: E402

SCHEMA = json.loads((ROOT / "provenance/claim-warrant.schema.json").read_text())
ALLOWED = set(SCHEMA["properties"]["verify_outcome"]["properties"]["result"]["enum"])
FIELDS = set(SCHEMA["properties"]["verify_outcome"]["properties"])

WARRANT = {"warrant_version": "1", "claim_type": "cited", "verify_determinism": "deterministic"}
REAL = {WARRANT_KEY: dict(WARRANT), "doi": "10.1000/paper"}
FAKE = {WARRANT_KEY: dict(WARRANT), "doi": "10.1000/never-happened"}
NOW = datetime(2026, 9, 16, tzinfo=timezone.utc)


def resolver(form, reference):
    return reference in {"10.1000/paper"}


def test_a_resolving_reference_is_verified():
    assert recheck_outcome(REAL, resolver, now=NOW)["result"] == "verified"


def test_a_fabricated_reference_is_rejected():
    """The only edge that condemns, and it fires only when a resolver said False."""
    assert recheck_outcome(FAKE, resolver, now=NOW)["result"] == "rejected"


def test_no_resolver_is_unverifiable_never_rejected():
    """The schema's most emphatic rule: 'a prophet can make claims unverifiable
    at no cost', so unreachable must not read as failed."""
    outcome = recheck_outcome(REAL, None, now=NOW)
    assert outcome["result"] == "unverifiable"
    assert outcome["reason"] == "oracle_absent"


def test_a_resolver_that_cannot_answer_is_unverifiable():
    outcome = recheck_outcome(REAL, lambda f, r: None, now=NOW)
    assert outcome["result"] == "unverifiable"
    assert outcome["reason"] == "fetch_failed"


def test_the_outcome_conforms_to_the_schema():
    """Flips if a result value or field name drifts out of the schema."""
    for evidence, res in ((REAL, resolver), (FAKE, resolver), (REAL, None)):
        outcome = recheck_outcome(evidence, res, now=NOW)
        assert outcome["result"] in ALLOWED
        assert set(outcome) <= FIELDS


def test_evidence_naming_no_reference_is_not_rechecked_at_all():
    """UnattributedRootError already governs this. Recording it here would make
    verify_outcome look exercised when nothing was checked."""
    assert recheck_outcome({WARRANT_KEY: dict(WARRANT), "source": "trust me"}, resolver) is None


def test_attach_never_mutates_and_never_invents_a_warrant():
    before = json.dumps(FAKE, sort_keys=True)
    attached = attach_recheck(FAKE, resolver, now=NOW)
    assert json.dumps(FAKE, sort_keys=True) == before
    assert attached[WARRANT_KEY]["verify_outcome"]["result"] == "rejected"
    # evidence with no warrant is returned unchanged: claim_type is the
    # producer's to declare, and determinism is DERIVED from it.
    bare = {"doi": "10.1000/never-happened"}
    assert attach_recheck(bare, resolver, now=NOW) == bare
    assert WARRANT_KEY not in attach_recheck(bare, resolver, now=NOW)


def test_report_separates_unverifiable_from_rejected_in_the_rate():
    """The rate is over what a resolver actually answered."""
    def node(nid, evidence):
        return EvidenceNode(node_id=nid, proposition_id="p", value=True, observer_id=nid,
                            source_id=nid, confidence=0.9, evidence=evidence, copied_from=())
    g = EvidenceGraph(strict=True)
    g.add(node("a", REAL))
    g.add(node("f", FAKE))
    report = recheck_report(g._nodes.values(), resolver)
    assert report["outcomes"]["verified"] == 1 and report["outcomes"]["rejected"] == 1
    assert report["rejectedRate"] == 0.5
    assert report["distinctOutcomes"] >= 2

    offline = recheck_report(g._nodes.values(), None)
    assert offline["outcomes"]["unverifiable"] == 2
    assert offline["rejectedRate"] is None, "nothing was answered, so there is no rate"
