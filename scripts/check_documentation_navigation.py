#!/usr/bin/env python3
"""Check the public documentation map without rewriting historical artifacts."""

from __future__ import annotations

import argparse
import pathlib
import re
import sys
from urllib.parse import unquote


NAVIGATION_DOCUMENTS = (
    "README.md",
    "aggregation/README.md",
    "benchmark/README.md",
    "docs/README.md",
    "docs/repository-map.md",
    "docs/architecture/README.md",
    "docs/contributing/README.md",
    "docs/evidence/README.md",
    "docs/evidence/STATUS.md",
    "docs/research/README.md",
    "docs/use/README.md",
    "experiments/README.md",
    "formal/README.md",
    "knowledge_ledger/README.md",
    "provenance/README.md",
    "research/README.md",
    "results/README.md",
)

STABLE_ENTRY_POINTS = (
    "PUBLIC-CLAIMS.md",
    "CANONICAL-RECORDS.md",
    "EVIDENCE-ALIGNMENT.md",
    "SYSTEM-ARCHITECTURE.md",
    "ROADMAP.md",
    "CONTRIBUTING.md",
    "papers/00-CURRENT-PAPER.md",
    "research/records/README.md",
)

README_DESTINATIONS = (
    "docs/README.md",
    "PUBLIC-CLAIMS.md",
    "CANONICAL-RECORDS.md",
    "EVIDENCE-ALIGNMENT.md",
    "papers/00-CURRENT-PAPER.md",
    "docs/contributing/README.md",
)

MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


def _local_destination(raw: str) -> str | None:
    destination = raw.strip()
    if destination.startswith("<") and ">" in destination:
        destination = destination[1 : destination.index(">")]
    else:
        destination = destination.split(maxsplit=1)[0]
    destination = unquote(destination).split("#", 1)[0]
    if not destination or destination.startswith(("http://", "https://", "mailto:")):
        return None
    return destination


def linked_destinations(document: pathlib.Path) -> list[str]:
    return [
        destination
        for match in MARKDOWN_LINK.finditer(document.read_text(encoding="utf-8"))
        if (destination := _local_destination(match.group(1))) is not None
    ]


def check(root: pathlib.Path) -> list[str]:
    problems: list[str] = []

    for relative in (*NAVIGATION_DOCUMENTS, *STABLE_ENTRY_POINTS):
        if not (root / relative).exists():
            problems.append(f"required public entry point is missing: {relative}")

    for relative in NAVIGATION_DOCUMENTS:
        document = root / relative
        if not document.is_file():
            continue
        for destination in linked_destinations(document):
            target = (document.parent / destination).resolve()
            try:
                target.relative_to(root.resolve())
            except ValueError:
                problems.append(f"{relative}: local link escapes the repository: {destination}")
                continue
            if not target.exists():
                problems.append(f"{relative}: broken local link: {destination}")

    readme = root / "README.md"
    if readme.is_file():
        destinations = set(linked_destinations(readme))
        for destination in README_DESTINATIONS:
            if destination not in destinations:
                problems.append(f"README.md: missing front-door link: {destination}")

    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="repository root")
    args = parser.parse_args()

    problems = check(pathlib.Path(args.root).resolve())
    if problems:
        print("Documentation navigation check FAILED:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1

    print(
        "Documentation navigation verified: "
        f"{len(NAVIGATION_DOCUMENTS)} maps and "
        f"{len(STABLE_ENTRY_POINTS)} stable entry points."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
