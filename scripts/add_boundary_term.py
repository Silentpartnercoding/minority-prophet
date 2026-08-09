#!/usr/bin/env python3
"""Turn a sensitive term into a boundary digest without the term touching anything.

THE PROBLEM THIS SOLVES. The public blocklist in check_public_boundary.py matches
by SHA-256 so that the file stops naming what it protects. That helps, but the
digests are themselves public, and a digest of a short guessable phrase falls to a
wordlist immediately. It is obscurity, not secrecy -- stated plainly in that file.

Storing the term in a CI secret looks like the fix and is not quite, because
putting it there means typing it: into a shell that keeps history, a command line
another process can read, or a transcript. The act of protecting the word states
the word.

So this tool never handles the term in a way that persists. It is read without
echo, hashed in memory, and only the 64 hex characters are printed. Put those in
the repository secret. The word then exists in no file, no git history, no CI
configuration, no shell history and no transcript -- and because the digest lives
in a secret rather than in the public checker, an attacker cannot run a wordlist
against it either. They cannot test guesses against a digest they cannot see.

Usage:
    python3 scripts/add_boundary_term.py

    (paste the digest into the MP_BOUNDARY_DIGESTS repository secret; multiple
     digests may be separated by whitespace or commas)

Deliberately absent: any --term flag. A term on the command line is in the shell
history and the process list before this program starts, which would defeat the
entire point.
"""

from __future__ import annotations

import getpass
import hashlib
import re
import sys

_MAX_TERM_WORDS = 3


def digest(term: str) -> str:
    return hashlib.sha256(term.strip().lower().encode()).hexdigest()


def main() -> int:
    if len(sys.argv) > 1:
        print("This tool takes no arguments. A term passed on the command line is "
              "already in your shell history and the process list.", file=sys.stderr)
        return 2

    try:
        term = getpass.getpass("term (not echoed): ")
    except (EOFError, KeyboardInterrupt):
        print(file=sys.stderr)
        return 1

    cleaned = term.strip().lower()
    if not cleaned:
        print("no term given", file=sys.stderr)
        return 1

    # The matcher tokenises on word characters and tests 1..3-word n-grams, so a
    # term outside that shape can never be matched however it is stored. Better to
    # refuse than to hand back a digest that silently blocks nothing.
    words = re.findall(r"[a-z0-9']+", cleaned)
    if not words:
        print("that term contains no matchable words", file=sys.stderr)
        return 1
    if len(words) > _MAX_TERM_WORDS:
        print(f"the matcher checks n-grams up to {_MAX_TERM_WORDS} words; this term "
              f"has {len(words)} and would never be matched", file=sys.stderr)
        return 1
    if " ".join(words) != cleaned:
        print(f"note: the term normalises to {len(words)} word(s) before hashing; "
              f"punctuation and spacing are not significant", file=sys.stderr)

    print(digest(" ".join(words)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
