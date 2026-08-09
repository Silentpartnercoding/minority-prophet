#!/usr/bin/env python3
"""Reject newly added public-boundary leaks without rewriting historical records."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import subprocess
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class Rule:
    name: str
    pattern: re.Pattern[str]
    guidance: str


RULES = (
    Rule("private key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"), "remove the private key and rotate it"),
    Rule("GitHub token", re.compile(r"\b(?:gh[opusr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"), "remove and revoke the token"),
    Rule("AWS access key", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"), "remove and rotate the key"),
    Rule("Slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"), "remove and revoke the token"),
    Rule("Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b"), "remove and rotate the key"),
    Rule("credential-bearing URL", re.compile(r"https?://[^\s/:]+:[^\s/@]+@[^\s]+|https?://[^\s]+[?&](?:access_token|api_key|token|secret)=[A-Za-z0-9._~-]{16,}", re.IGNORECASE), "remove the credential and rotate it"),
    Rule("Bearer credential", re.compile(r"\bBearer\s+[A-Za-z0-9._~-]{24,}\b", re.IGNORECASE), "remove and rotate the credential"),
    Rule("assigned secret", re.compile(r"\b(?:api[_-]?key|client[_-]?secret|access[_-]?token|auth[_-]?token|password)\s*[:=]\s*['\"]?[A-Za-z0-9._~+/=-]{24,}['\"]?", re.IGNORECASE), "replace the value with an obvious placeholder and rotate any real credential"),
    Rule("local user path", re.compile(r"(?<![A-Za-z0-9._~-])/(?:Users|home)/[^/\s'\"`]+/"), "replace it with a repository-relative or generic path"),
)

# --- Sensitive vocabulary, matched by digest -------------------------------
#
# A public blocklist that spells out what it blocks is a directory of what is
# worth hiding: the file meant to protect internal vocabulary publishes it. Two
# rules here previously named an internal control-plane component and six
# internal-strategy phrases in the clear (BLK-101). They are matched by SHA-256
# of the lowercased term instead, so the list no longer names its own contents.
#
# HONEST LIMIT: a digest of a short, guessable phrase is recoverable by anyone
# willing to hash a wordlist. This raises the cost from "read the file" to "run
# a dictionary" -- a real improvement for multi-word phrases, a weak one for
# single common words. It is obscurity, not secrecy. For vocabulary that must
# genuinely not be recoverable, set MP_BOUNDARY_TERMS in CI (newline-separated)
# from a repository secret; those terms never enter the tree in any form.
#
# SCOPE (BL-052, owner decision 2026-08-08): coined and internal names only.
# Five inherited entries were ordinary business English. They failed twice over:
# they blocked any document discussing governance in the abstract -- the audit
# that found this defect tripped on one, used descriptively -- and hashing
# protected them from nobody, since a two-word English phrase falls to a wordlist
# immediately. Two further entries were hyphenated variants that this matcher can
# never reach: it tokenises on word characters, so the one-word digest already
# covers them. Generic vocabulary is a review question, not a boundary rule.
_TERM_DIGESTS = frozenset({
    "f1a26a13024dcb651eb674d989704a1e07185a601424008649ac476ba8527012",
    "96a4bc2602655473120fcc571ee3d8cfe5f8801f8038ccc06323d305e323331c",
    "2e0f266b14026f17bd89bb2dcb1fb5187f6d7b1917ab91fc2d583904f2d8cefb",
})
_MAX_TERM_WORDS = 3
_VOCAB_GUIDANCE = ("internal vocabulary: describe the interface or rationale in "
                   "public terms instead of naming the internal component")


def _extra_digests() -> frozenset:
    raw = os.environ.get("MP_BOUNDARY_TERMS", "")
    return frozenset(hashlib.sha256(term.strip().lower().encode()).hexdigest()
                     for term in raw.splitlines() if term.strip())


def sensitive_vocabulary_hit(line: str) -> bool:
    """True if any 1..3-word n-gram of `line` digests to a blocked term."""
    digests = _TERM_DIGESTS | _extra_digests()
    words = re.findall(r"[a-z0-9']+", line.lower())
    for size in range(1, _MAX_TERM_WORDS + 1):
        for i in range(len(words) - size + 1):
            phrase = " ".join(words[i:i + size])
            if hashlib.sha256(phrase.encode()).hexdigest() in digests:
                return True
    return False


# The checker and its regression tests necessarily contain the signatures above.
SELF_EXEMPT = {"scripts/check_public_boundary.py", "tests/test_public_boundary.py"}


def added_lines(base: str, head: str) -> list[tuple[str, int, str]]:
    command = ["git", "diff", "--unified=0", "--no-color", f"{base}...{head}", "--"]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    findings: list[tuple[str, int, str]] = []
    path = ""
    new_line = 0
    for line in result.stdout.splitlines():
        if line.startswith("+++ b/"):
            path = line[6:]
        elif line.startswith("@@"):
            match = re.search(r"\+(\d+)(?:,(\d+))?", line)
            if match:
                new_line = int(match.group(1))
        elif line.startswith("+") and not line.startswith("+++"):
            findings.append((path, new_line, line[1:]))
            new_line += 1
        elif line.startswith(" "):
            new_line += 1
    return findings


def violations(lines: list[tuple[str, int, str]]) -> list[str]:
    output: list[str] = []
    for path, line_number, text in lines:
        if path in SELF_EXEMPT:
            continue
        for rule in RULES:
            if rule.pattern.search(text):
                output.append(f"{path}:{line_number}: {rule.name}: {rule.guidance}")
        if sensitive_vocabulary_hit(text):
            output.append(f"{path}:{line_number}: {_VOCAB_GUIDANCE}")
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True, help="trusted base commit")
    parser.add_argument("--head", default="HEAD", help="commit to inspect")
    args = parser.parse_args()

    added = added_lines(args.base, args.head)

    # A diff-based check that inspects nothing still prints "passed". Running it
    # with --head HEAD *before* committing makes base and head the same commit, so
    # the diff is empty and the run is vacuous while looking green. That mistake
    # has been made three times in this programme and published a leak each time,
    # most recently the one this very file records. The check now refuses the
    # situation rather than reporting a success it did not earn.
    if not added and subprocess.run(("git", "status", "--porcelain"),
                                    capture_output=True, text=True).stdout.strip():
        print("Public-boundary check REFUSED: the diff is empty but the working "
              "tree has uncommitted changes.\n  Nothing would be inspected, so a "
              "pass here would mean nothing. Commit first, then re-run.",
              file=sys.stderr)
        return 1

    problems = violations(added)
    if problems:
        print("Public-boundary check failed. Only newly added lines were inspected:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1
    print("Public-boundary check passed: no prohibited additions detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
