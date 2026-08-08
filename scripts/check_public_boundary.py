#!/usr/bin/env python3
"""Reject newly added public-boundary leaks without rewriting historical records."""

from __future__ import annotations

import argparse
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
    Rule("local user path", re.compile(r"(?:^|[\s'\"`(])/(?:Users|home)/[^/\s]+/"), "replace it with a repository-relative or generic path"),
    Rule("internal OpenClaw path", re.compile(r"(?:^|[\s'\"`(])(?:~|/[^\s'\"`]*)?/\.?(?:openclaw)(?:/|\b)", re.IGNORECASE), "describe the interface generically; do not expose internal runtime paths"),
    Rule("internal strategy wording", re.compile(r"\b(?:shadow lane|master plan|internal strategy|our moat|strategic leverage|position ourselves)\b", re.IGNORECASE), "rewrite as factual public project rationale"),
)

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
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True, help="trusted base commit")
    parser.add_argument("--head", default="HEAD", help="commit to inspect")
    args = parser.parse_args()

    problems = violations(added_lines(args.base, args.head))
    if problems:
        print("Public-boundary check failed. Only newly added lines were inspected:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1
    print("Public-boundary check passed: no prohibited additions detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
