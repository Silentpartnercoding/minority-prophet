#!/usr/bin/env python3
"""Fail closed on incomplete or internally inconsistent paper packaging."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "papers/peer-review/minority-prophet-peer-review-v1.1.0.md"
AUDIT = ROOT / "papers/peer-review/LITERATURE-AUDIT.md"
CHECKLIST = ROOT / "papers/peer-review/SUBMISSION-CHECKLIST.md"
METADATA = ROOT / "papers/peer-review/metadata.json"
PDF = ROOT / "output/pdf/minority-prophet-peer-review-v1.1.0.pdf"

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
    for path in (SOURCE, AUDIT, CHECKLIST, METADATA, PDF):
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
    title = text.splitlines()[0].removeprefix("# ")
    if meta["title"] != title or meta["version"] != "1.1.0-review":
        fail("metadata title or version disagrees with manuscript")
    if PDF.stat().st_size < 50_000:
        fail("PDF is unexpectedly small")
    print("paper-check: source, citations, metadata, and PDF package are consistent")


if __name__ == "__main__":
    main()

