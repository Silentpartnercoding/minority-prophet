from pathlib import Path
import hashlib
import json
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
DRAFT_DIR = ROOT / "papers" / "ietf"
DRAFT_NAME = "draft-he-agentproto-verifier-evidence-01"
SOURCE = DRAFT_DIR / f"{DRAFT_NAME}.xml"
TEXT = DRAFT_DIR / f"{DRAFT_NAME}.txt"
HTML = DRAFT_DIR / f"{DRAFT_NAME}.html"
LEDGER = DRAFT_DIR / "VERIFIER-EVIDENCE-REVIEW-LEDGER.md"
CHECKLIST = DRAFT_DIR / "VERIFIER-EVIDENCE-SUBMISSION-CHECKLIST.md"
PACKAGE_README = DRAFT_DIR / "VERIFIER-EVIDENCE-README.md"
MANIFEST = DRAFT_DIR / "verifier-evidence-submission-manifest.json"


def test_agentproto_package_contains_source_and_generated_formats():
    assert SOURCE.is_file()
    assert TEXT.is_file()
    assert HTML.is_file()


def test_agentproto_source_has_explicit_revision_date_and_current_references():
    root = ET.parse(SOURCE).getroot()
    assert root.attrib["docName"] == DRAFT_NAME
    assert root.attrib["submissionType"] == "IETF"
    assert root.attrib["consensus"] == "false"

    front = root.find("front")
    assert front is not None
    date = front.find("date")
    assert date is not None
    assert date.attrib == {"year": "2026", "month": "October", "day": "18"}

    source = SOURCE.read_text(encoding="utf-8")
    assert "draft-bu-agentproto-security-principal-binding-08" in source
    assert "draft-bu-agentproto-security-principal-binding-07" not in source
    assert "draft-oga-musubi-settlement-01" in source
    assert "635f3d57eb6f90fdf4c6945778020c34521be0a1" in source
    assert "dd64d0e2" in source
    for forbidden in ("TBD", "TODO", "Wesleyan", "Zinglez"):
        assert forbidden not in source


def test_agentproto_source_has_confirmed_author_identity():
    root = ET.parse(SOURCE).getroot()
    author = root.find("./front/author")
    assert author is not None
    assert author.attrib == {
        "fullname": "James Siyuan He",
        "initials": "J. S.",
        "surname": "He",
    }
    assert author.findtext("organization") == "Independent"
    assert author.findtext("./address/email") == "jsiyuanhe@gmail.com"


def test_agentproto_source_preserves_reviewed_scope_boundaries():
    source = " ".join(SOURCE.read_text(encoding="utf-8").split())
    for required in (
        "This is a bounded source replay, not a second implementation or a conformance result.",
        "CMP-1 and CMP-2 address the completeness and omission subcase of the third open issue.",
        "A record containing only the former does not satisfy this exercise condition; it does not by itself establish that the latter outcome is unreachable.",
        "Acknowledgment does not imply endorsement of this document.",
    ):
        assert required in source


def test_agentproto_source_answers_public_review_without_overclaiming():
    source = " ".join(SOURCE.read_text(encoding="utf-8").split())
    for required in (
        "paths to outcomes classified as neither",
        "one expected to accept and one expected to produce the declared non-accepting outcome",
        "outcome token alone does not identify the rule or condition that fired",
        "reachable-unexercised",
        "shadowed-unreachable",
        "This document does not assign either obligation to a working group",
        "not a second external evidence root",
        "not independent verification of MUSUBI",
    ):
        assert required in source


def test_agentproto_source_records_external_results_and_their_limits():
    source = " ".join(SOURCE.read_text(encoding="utf-8").split())
    for required in (
        "165 report objects",
        "82 accept, 28 reject, and 55 cannot-tell",
        "35 mutation scenarios, including the baseline",
        "128 vectors",
        "more than 200000 verified headers",
        "nobody outside the MUSUBI project has rerun the exercise script",
        "The original four vectors",
        "The two additional vectors in this revision are prose vectors",
    ):
        assert required in source
    assert "The vectors in <xref target=\"vectors\"/> are published in executable form" not in source


def test_agentproto_rendered_text_preserves_title_and_nonclaim():
    rendered = " ".join(TEXT.read_text(encoding="utf-8").split())
    assert "Exercise and Completeness Evidence for Agent Protocol Verifier Results" in rendered
    assert "bounded source replay, not a second implementation or a conformance result" in rendered
    assert "shadowed-unreachable" in rendered
    assert "not independent verification of MUSUBI" in rendered
    assert "This document has no IANA actions." in rendered


def test_makefile_exposes_separate_agentproto_build_and_check_targets():
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "agentproto-draft:" in makefile
    assert "agentproto-check:" in makefile


def test_agentproto_package_records_review_scope_and_human_submission_boundary():
    for path in (LEDGER, CHECKLIST, PACKAGE_README, MANIFEST):
        assert path.is_file(), path

    ledger = " ".join(LEDGER.read_text(encoding="utf-8").replace("**", "").split())
    for required in (
        "bounded source replay",
        "not a second implementation or conformance result",
        "The wording and parity review concluded at that point.",
        "draft-bu-agentproto-security-principal-binding-07",
        "draft-bu-agentproto-security-principal-binding-08",
        "Public review after -00",
        "Lars Kersten Kroehl",
        "Toshikatsu Oga",
        "Orie Steele",
    ):
        assert required in ledger
    assert "This completes the requested wording/parity review." not in ledger

    checklist = CHECKLIST.read_text(encoding="utf-8")
    assert "submitted and confirmed" in checklist.lower()
    assert "https://datatracker.ietf.org/doc/draft-he-agentproto-verifier-evidence/" in checklist
    assert "Datatracker" in checklist
    assert "IPR" in checklist
    assert "working-group adoption" in checklist

    internal_plan = (
        ROOT
        / "docs"
        / "superpowers"
        / "plans"
        / "2026-10-17-agentproto-datatracker-submission.md"
    )
    assert not internal_plan.exists()


def test_agentproto_manifest_binds_current_rendered_package():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["document"] == DRAFT_NAME
    assert manifest["submission_state"] == "submitted-confirmed"
    assert manifest["submission_id"] == "170563"
    assert manifest["revision_url"].endswith(
        "/draft-he-agentproto-verifier-evidence/01/"
    )
    assert manifest["renderer"] == {
        "name": "xml2rfc",
        "version": "3.34.1",
        "requirements_file": "requirements-agentproto.txt",
    }

    expected_paths = {
        f"papers/ietf/{DRAFT_NAME}.xml": SOURCE,
        f"papers/ietf/{DRAFT_NAME}.txt": TEXT,
        f"papers/ietf/{DRAFT_NAME}.html": HTML,
    }
    assert set(manifest["files"]) == set(expected_paths)
    for relative_path, path in expected_paths.items():
        expected = hashlib.sha256(path.read_bytes()).hexdigest()
        assert manifest["files"][relative_path]["sha256"] == expected
        assert manifest["files"][relative_path]["bytes"] == path.stat().st_size
