#!/usr/bin/env python3
"""Turn a repository into the two ledgers the KL-000 evaluator consumes.

Gate item (1), implementing MAPPING-RULES.md. Preparatory: KL-001 stays `seeded`.

The two exposures this layer owns are designed against, not discovered again:

  M1  the scope is DERIVED from the repository, and cannot be supplied. FC1's W3
      showed that a declaration which simply omits the uncovered files earns a
      clean `absent_within_declared_scope` -- the evaluator is honest about the
      scope it is given and the scope was a lie.
  M2  one scanner family is one root. Per-finding roots would let a single
      scanner reporting five times manufacture five independent witnesses, which
      is the exact failure the programme exists to refuse.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys

SCOPE_PATTERNS = ("**/*.py",)          # registered; see MAPPING-RULES.md M1


class ScopeSuppliedError(TypeError):
    """Raised when a caller tries to declare the scope instead of deriving it."""


def derive_scope(repo: pathlib.Path, **kwargs) -> list[str]:
    """M1. Enumerate the scope from the repository.

    `**kwargs` exists only to catch a caller passing `scope=` or `locations=`
    and refuse loudly. Silently ignoring such an argument would reintroduce W3
    through the interface rather than through the data.
    """
    for forbidden in ("scope", "locations", "declared", "files"):
        if forbidden in kwargs:
            raise ScopeSuppliedError(
                f"{forbidden!r} may not be supplied: the declared scope is derived "
                "from the repository (M1). Supplying it is ADV-001 through the "
                "interface -- see FC1's W3."
            )
    seen: set[str] = set()
    for pattern in SCOPE_PATTERNS:
        for path in repo.glob(pattern):
            if path.is_file():
                seen.add(str(path.relative_to(repo)))
    return sorted(seen)


def scope_digest(scope: list[str]) -> str:
    return hashlib.sha256("\n".join(scope).encode()).hexdigest()


def map_repository(repo: pathlib.Path, scanners: dict, **kwargs) -> dict:
    """Repository plus scanner outputs -> {evidenceLedger, searchLedger, mapping}.

    `scanners` maps familyId -> {"read": [relative paths opened],
                                 "findings": [{"file": ..., "kind": ...}],
                                 "errored": [relative paths that raised]}
    """
    scope = derive_scope(repo, **kwargs)

    # M3 -- searched means read; the three terminal states stay distinct.
    read: set[str] = set()
    errored: set[str] = set()
    for report in scanners.values():
        read |= set(report.get("read", ()))
        errored |= set(report.get("errored", ()))
    locations = []
    for rel in scope:
        if rel in errored:
            status = "unavailable"
        elif rel in read:
            status = "searched"
        else:
            status = "not_searched"
        locations.append({"id": rel, "status": status})

    # M2 -- one family, one root, however many findings it reported.
    records, collapsed = [], {}
    for family, report in sorted(scanners.items()):
        findings = report.get("findings", ())
        collapsed[family] = len(findings)
        for i, finding in enumerate(findings):
            records.append({
                "recordId": f"{family}#{i}",
                "rootId": family,                       # never per-finding
                "side": "oppose",                       # a finding opposes cleanliness
                "locationId": finding["file"],
            })

    return {
        "transactionId": f"kl001:{repo.name}",
        "schema": "kl/v0.1",
        "claim": {"proposition": f"No target-class defect exists in {repo.name}",
                  "type": "absence"},
        "evidenceLedger": {"records": records},
        "searchLedger": {"locations": locations},
        # M4 -- the mapping records itself, so M1 and M2 are checkable rather
        # than merely asserted.
        "mapping": {
            "rules": "MAPPING-RULES.md",
            "scopePatterns": list(SCOPE_PATTERNS),
            "scopeSize": len(scope),
            "scopeDigest": scope_digest(scope),
            "families": sorted(scanners),
            "findingsCollapsedPerRoot": collapsed,
            "statusCounts": {s: sum(1 for l in locations if l["status"] == s)
                             for s in ("searched", "not_searched", "unavailable")},
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--scanners", required=True, help="JSON: familyId -> report")
    ap.add_argument("--json")
    args = ap.parse_args()
    out = map_repository(pathlib.Path(args.repo),
                         json.loads(pathlib.Path(args.scanners).read_text()))
    if args.json:
        pathlib.Path(args.json).write_text(json.dumps(out, indent=2) + "\n")
    m = out["mapping"]
    print(f"  scope {m['scopeSize']} files  digest {m['scopeDigest'][:12]}...")
    print(f"  statuses {m['statusCounts']}")
    print(f"  roots {len(m['families'])}  findings collapsed {m['findingsCollapsedPerRoot']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
