"""TRC-101 enforcement: every normative rule cites the paper or declares
itself specification-local with a reason (schemas/traceability-TRC-101.md).

Family of tests/test_closing_packets.py and tests/test_preregistrations.py:
a rule with neither a citation nor a declaration fails the suite, a paper
claim with neither a test nor an explicit not-tested reason fails the suite,
and the map's summary counts are recomputed rather than trusted (the DOC-102
lesson: counts in prose drift; counts in tests cannot).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
KL000 = REPO / "research" / "knowledge-ledger" / "experiments" / "KL-000"
MAP = json.loads((KL000 / "TRACEABILITY-v1.3.0.json").read_text())
PREREG = json.loads((KL000 / "preregistration-v1.3.0.json").read_text())
PAPER = (REPO / "papers" / "minority-prophet-v1.0.3.md").read_text()

RULE_BASES = {"paper", "partial", "specification-local"}
CLAIM_STATUSES = {"tested", "partially-tested", "not-tested-by-KL-000", "out-of-scope"}


@pytest.mark.parametrize("entry", MAP["rules"], ids=lambda e: e["id"])
def test_every_rule_is_cited_or_declared(entry):
    assert entry["basis"] in RULE_BASES, entry["id"]
    if entry["basis"] in ("paper", "partial"):
        citation = entry.get("citation", {})
        assert citation.get("location", "").strip(), f"{entry['id']}: citation without location"
        assert citation.get("quote", "").strip(), f"{entry['id']}: citation without verbatim quote"
    if entry["basis"] in ("specification-local", "partial"):
        assert entry.get("reason", "").strip(), f"{entry['id']}: specification-local without a reason"


@pytest.mark.parametrize("entry", MAP["rules"], ids=lambda e: e["id"])
def test_quotes_are_verbatim_from_the_paper(entry):
    """A citation whose quote is not in the paper is a fabricated derivation --
    worse than no citation. Normalised for the map's ASCII transcription of
    the paper's typography."""
    if entry["basis"] not in ("paper", "partial"):
        pytest.skip("no citation to check")
    quote = entry["citation"]["quote"]
    paper = PAPER.replace("**", "").replace("*", "").replace("—", "--")
    normalised = quote.replace("**", "").replace("*", "").replace("—", "--")
    for fragment in normalised.split("[...]"):
        fragment = fragment.strip()
        assert fragment and fragment in paper, (
            f"{entry['id']}: quoted fragment not found verbatim in the paper: {fragment[:80]!r}"
        )


def test_every_registered_invariant_appears_in_the_map():
    registered = {inv["id"] for inv in PREREG["invariants"]}
    mapped = {e["id"] for e in MAP["rules"]}
    missing = registered - mapped
    assert not missing, f"registered invariants with no traceability entry: {sorted(missing)}"


@pytest.mark.parametrize("entry", MAP["paperClaims"], ids=lambda e: e["claim"][:40])
def test_every_paper_claim_is_tested_or_says_why_not(entry):
    assert entry["status"] in CLAIM_STATUSES
    if entry["status"] in ("tested", "partially-tested"):
        assert entry.get("testedBy", "").strip(), f"claim marked tested with no tester: {entry['claim'][:60]}"
    if entry["status"] in ("partially-tested", "not-tested-by-KL-000", "out-of-scope"):
        assert entry.get("whyNot", "").strip(), f"untested claim with no reason: {entry['claim'][:60]}"


def test_summary_counts_are_recomputed_not_trusted():
    s = MAP["summary"]
    rules = MAP["rules"]
    claims = MAP["paperClaims"]
    assert s["rulesTotal"] == len(rules)
    assert s["rulesPaperDerived"] == sum(1 for e in rules if e["basis"] == "paper")
    assert s["rulesPartial"] == sum(1 for e in rules if e["basis"] == "partial")
    assert s["rulesSpecificationLocal"] == sum(1 for e in rules if e["basis"] == "specification-local")
    assert s["paperClaimsTotal"] == len(claims)
    assert s["paperClaimsTested"] == sum(1 for e in claims if e["status"] == "tested")
    assert s["paperClaimsPartiallyTested"] == sum(1 for e in claims if e["status"] == "partially-tested")
    assert s["paperClaimsNotTested"] == sum(1 for e in claims if e["status"] == "not-tested-by-KL-000")
    assert s["paperClaimsOutOfScope"] == sum(1 for e in claims if e["status"] == "out-of-scope")
