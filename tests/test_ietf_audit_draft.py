from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
DRAFT_DIR = ROOT / "papers" / "ietf"
DRAFT_NAME = "draft-he-audit-evidence-root-counting-00"
SOURCE = DRAFT_DIR / f"{DRAFT_NAME}.xml"
TEXT = DRAFT_DIR / f"{DRAFT_NAME}.txt"
HTML = DRAFT_DIR / f"{DRAFT_NAME}.html"


def test_ietf_package_contains_source_and_generated_formats():
    assert SOURCE.is_file()
    assert TEXT.is_file()
    assert HTML.is_file()


def test_source_declares_the_individual_draft_and_required_boundaries():
    root = ET.parse(SOURCE).getroot()
    assert root.attrib["docName"] == DRAFT_NAME
    assert root.attrib["submissionType"] == "IETF"
    assert root.attrib["consensus"] == "false"

    source_text = SOURCE.read_text(encoding="utf-8")
    for required in (
        "Evidence Multiplicity Is a Separate Verification Dimension",
        "Completeness Requires an External Scope Commitment",
        "Security Considerations",
        "Privacy Considerations",
        "IANA Considerations",
        "7114ae58bdc2efb13417e4624762f8f9b1ff6ba4",
        "draft-kuehlewind-audit-architecture-01",
        "draft-bradleyb-audit-decision-records-00",
    ):
        assert required in source_text

    for forbidden in ("TBD", "TODO", "Wesleyan", "Zinglez"):
        assert forbidden not in source_text


def test_generated_text_preserves_the_non_claims_and_counting_rule():
    rendered = TEXT.read_text(encoding="utf-8")
    normalized = " ".join(rendered.split())
    assert "An Echo Is Not a Witness" in normalized
    assert "one evidence-provenance root" in normalized
    assert "does not establish that those roots are independent" in normalized
    assert "This document has no IANA actions." in normalized


def test_readme_names_a_reproducible_build_and_pre_submission_checks():
    readme = (DRAFT_DIR / "README.md").read_text(encoding="utf-8")
    assert "make ietf-draft" in readme
    assert "make ietf-check" in readme
    assert "not submitted" in readme.lower()
    assert "November 2, 2026 at 23:59 UTC" in readme


def test_ci_rebuilds_and_checks_the_internet_draft_package():
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(
        encoding="utf-8"
    )
    assert "make ietf-check" in workflow


def test_pre_submission_packet_separates_preparation_from_human_actions():
    checklist = (DRAFT_DIR / "PRE-SUBMISSION.md").read_text(encoding="utf-8")
    review_packet = (DRAFT_DIR / "REVIEW-REQUESTS.md").read_text(
        encoding="utf-8"
    )

    assert "Human-only submission steps" in checklist
    assert "Confirm the IPR disclosure answer" in checklist
    assert "Do not send from this file" in review_packet
    for reviewer in ("Bradley", "Songbo", "Iman", "AUDIT architecture authors"):
        assert reviewer in review_packet
