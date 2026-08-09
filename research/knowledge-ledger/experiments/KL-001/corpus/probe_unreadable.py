#!/usr/bin/env python3
"""Count repositories containing a source file the scanner cannot decode.

This is the population property KL-001's mechanism depends on. The dual ledger
returns `not_established` instead of a clean verdict when the scanner found
nothing AND its coverage was incomplete; incomplete coverage, in this pipeline,
means a `.py` file that could not be decoded. A corpus without one cannot move
the primary endpoint no matter how the aggregation is written.

Prints one integer to stdout. Nothing else -- the reachability check parses it.

    corpus/frozen-v1 -> 0     (v0.2 registered its endpoint against this)
    corpus/frozen-v2 -> 22
"""

from __future__ import annotations

import pathlib
import sys


def count(corpus: pathlib.Path) -> int:
    total = 0
    for repo in sorted(p for p in corpus.iterdir() if p.is_dir()):
        for source in repo.rglob("*.py"):
            try:
                source.read_text()
            except (UnicodeDecodeError, OSError):
                total += 1
                break                      # one unreadable file makes the repo count
    return total


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: probe_unreadable.py CORPUS_DIR", file=sys.stderr)
        raise SystemExit(2)
    directory = pathlib.Path(sys.argv[1])
    if not directory.is_dir():
        print(f"not a directory: {directory}", file=sys.stderr)
        raise SystemExit(2)
    print(count(directory))
