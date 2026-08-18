#!/usr/bin/env python3
"""Fail closed on incomplete or internally inconsistent paper packaging."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER_VERSION = "1.2.0"
SOURCE = ROOT / f"papers/peer-review/minority-prophet-peer-review-v{PAPER_VERSION}.md"
AUDIT = ROOT / "papers/peer-review/LITERATURE-AUDIT.md"
CHECKLIST = ROOT / "papers/peer-review/SUBMISSION-CHECKLIST.md"
METADATA = ROOT / "papers/peer-review/metadata.json"
PDF = ROOT / f"output/pdf/minority-prophet-peer-review-v{PAPER_VERSION}.pdf"
ARXIV_METADATA = ROOT / "papers/peer-review/arxiv/metadata.json"
CITATION = ROOT / "CITATION.cff"
# The VERSION doi identifies one deposit; the CONCEPT doi identifies the family
# and resolves to the latest. Only the concept doi may be required inside the
# manuscript: a version doi is minted FROM the document, so demanding the
# document contain it forces either a false statement or an artifact that
# differs from the deposit. Both happened before this split existed --
# see papers/peer-review/ARCHIVAL-INTEGRITY.md.
CONCEPT_DOI = "10.5281/zenodo.21965712"
DOI = "10.5281/zenodo.21997434"

REQUIRED_SECTIONS = [
    "## Abstract", "## 1. Introduction", "## 2. Related work", "## 3. Model",
    "## 4. Formal results", "## 5. Validation evidence",
    "## 7. Threats to validity and limitations", "## 8. Conclusion",
    "## Data and code availability", "## Ethics statement", "## Funding",
    "## Competing interests", "## Author contributions", "## References",
]
FORBIDDEN = ["TODO", "TBD", "FIXME", "COMMIT_SHA", "DOI_PLACEHOLDER"]


def fail(message: str) -> None:
    print(f"paper-check: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    for path in (SOURCE, AUDIT, CHECKLIST, METADATA, ARXIV_METADATA, CITATION, PDF):
        if not path.is_file() or path.stat().st_size == 0:
            fail(f"missing or empty artifact: {path.relative_to(ROOT)}")
    text = SOURCE.read_text(encoding="utf-8")
    for section in REQUIRED_SECTIONS:
        if section not in text:
            fail(f"missing section: {section}")
    for token in FORBIDDEN:
        if token in text or token in AUDIT.read_text(encoding="utf-8"):
            fail(f"unresolved placeholder: {token}")
    cited = {int(n) for n in re.findall(r"\[(\d+)\]", text.split("## References", 1)[0])}
    listed = {int(n) for n in re.findall(r"^\[(\d+)\]", text.split("## References", 1)[1], re.MULTILINE)}
    if cited != listed:
        fail(f"citation mismatch: cited={sorted(cited)} listed={sorted(listed)}")
    meta = json.loads(METADATA.read_text(encoding="utf-8"))
    arxiv_meta = json.loads(ARXIV_METADATA.read_text(encoding="utf-8"))
    title = text.splitlines()[0].removeprefix("# ")
    if meta["title"] != title or meta["version"] != PAPER_VERSION:
        fail("metadata title or version disagrees with manuscript")
    if meta.get("doi") != DOI:
        fail("metadata does not record the assigned version DOI")
    if CONCEPT_DOI not in text:
        fail("manuscript does not cite the concept DOI")
    if DOI in text:
        fail("manuscript cites its own version DOI; use the concept DOI so the "
             "deposited artifact and the repository source cannot diverge")
    citation = CITATION.read_text(encoding="utf-8")
    if f'doi: "{DOI}"' not in citation or meta["title"] not in citation:
        fail("CITATION.cff is missing the preferred paper title or DOI")
    if arxiv_meta["title"] != title or arxiv_meta["abstract"] != meta["abstract"]:
        fail("arXiv title or abstract disagrees with canonical metadata")
    if "not yet assigned" in text.lower():
        fail("manuscript still represents the archival DOI as unassigned")
    if PDF.stat().st_size < 50_000:
        fail("PDF is unexpectedly small")
    print("paper-check: source, citations, metadata, and PDF package are consistent")


if __name__ == "__main__":
    main()
