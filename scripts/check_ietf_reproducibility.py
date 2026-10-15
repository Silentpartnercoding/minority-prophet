#!/usr/bin/env python3
"""Compare xml2rfc HTML while excluding its machine-specific version banner."""

from __future__ import annotations

import pathlib
import re
import sys

GENERATOR_BANNER = re.compile(
    r"<!-- Generator version information:\n.*?\n-->\n?", re.DOTALL
)


def normalized_html(value: str) -> str:
    return GENERATOR_BANNER.sub("", value)


def main() -> int:
    generated, committed = (pathlib.Path(value) for value in sys.argv[1:3])
    if normalized_html(generated.read_text()) != normalized_html(committed.read_text()):
        print(f"Substantive generated HTML differs from {committed}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
