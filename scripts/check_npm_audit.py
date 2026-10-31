#!/usr/bin/env python3
"""Fail on npm advisories except narrowly documented, unpatched exceptions."""

from __future__ import annotations

import json
import re
import subprocess
import sys

# GHSA-vfj7-8cjw-p6xm: braces, no patched npm release; dev-only glob consumers.
# GHSA-g3hv-75wg-m249: minimatch below 11.0.1, reached only through dev lint
# tooling (eslint, eslint-config-next and plugins), not used at runtime, no
# compatible patched 3.x release. Revisit when eslint ships a fix.
ALLOWED_ADVISORIES = {"GHSA-vfj7-8cjw-p6xm", "GHSA-g3hv-75wg-m249"}


def unexpected_advisories(report: dict, allowed: set[str]) -> set[str]:
    vulnerabilities = report.get("vulnerabilities", {})
    memo: dict[str, set[str]] = {}

    def advisories_for(name: str, visiting: set[str]) -> set[str]:
        if name in memo:
            return memo[name]
        if name in visiting:
            return set()
        found: set[str] = set()
        for source in vulnerabilities.get(name, {}).get("via", []):
            if isinstance(source, str):
                found |= advisories_for(source, visiting | {name})
            else:
                match = re.search(r"GHSA-[\w-]+", source.get("url", ""))
                if match:
                    found.add(match.group(0))
                else:
                    found.add(f"advisory-source:{source.get('source', 'unknown')}")
        memo[name] = found
        return found

    observed = set().union(*(advisories_for(name, set()) for name in vulnerabilities))
    return observed - allowed


def main() -> int:
    result = subprocess.run(["npm", "audit", "--json"], capture_output=True, text=True)
    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError:
        print(result.stderr or result.stdout, file=sys.stderr)
        return 2
    unexpected = unexpected_advisories(report, ALLOWED_ADVISORIES)
    if unexpected:
        print("Unexpected npm security advisories: " + ", ".join(sorted(unexpected)), file=sys.stderr)
        return 1
    total = report.get("metadata", {}).get("vulnerabilities", {}).get("total", 0)
    print(f"npm audit policy passed: {total} finding(s), all trace only to documented {sorted(ALLOWED_ADVISORIES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
