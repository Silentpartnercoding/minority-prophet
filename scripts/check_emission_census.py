#!/usr/bin/env python3
"""Which declared fields does nothing actually emit?

A field can be declared in a schema, enforced by a checker, and read by a
consumer, and still be written by nothing outside a fixture. That gap is
invisible to every test in this repository, because a test that supplies the
field passes whether or not any real producer ever would.

The attested-independence series ended on exactly that shape: `origin_type` and
`parent_roots` are declared in the vendor-neutral contract, enforced by
`conformance/authority_evidence.py` (a copy may not mint a fresh root), honoured
independently by the knowledge ledger — and written by no production path at
all. The link that would break the identical-record theorem had a socket and no
wire.

This census generalises that question over every schema in the corpus.

Producers are bucketed, because "something writes it" is not one claim:

  production  the paths a deployed decision actually runs through
  research    generators, experiments, demos and interop samples
  tests       test files and fixtures

A field **consumed or enforced in production but written only in research or
tests** is an emission gap. It is not necessarily a defect — plenty of fields
are legitimately supplied by callers outside this repository — but each one is
a place where the corpus cannot demonstrate its own plumbing, and the series
closure argues at least one of them was load-bearing.

Read-only. Emits counts and paths, never file contents.

    python3 scripts/check_emission_census.py
    python3 scripts/check_emission_census.py --json
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

PRODUCTION = (
    "provenance/", "aggregation/", "canon/", "knowledge_ledger/",
    "conformance/", "app/", "worker/", "border/",
)
RESEARCH = (
    "benchmark/", "research/", "experiments/", "interop/", "evaluations/",
    "audit/", "verification/", "scripts/",
)
TESTS = ("tests/",)

SKIP_DIRS = {".git", "node_modules", "__pycache__", "dist", "build", ".venv"}

#: Fields whose names are too generic to attribute by grep. Counting them would
#: produce confident nonsense, so they are declared out rather than silently
#: mis-measured.
TOO_GENERIC = {
    "id", "name", "path", "type", "value", "status", "schema", "version",
    "commit", "sha256", "timestamp", "confidence", "text", "title", "items",
    "properties", "required", "description", "enum", "const", "format",
    "evidence", "result", "results", "data", "key", "keys", "count",
    # Ordinary English that appears throughout unrelated code. Grep cannot
    # attribute these, and reporting them produces confident nonsense — the
    # first run of this census listed `action`, `model` and `question` as
    # emission gaps purely because the words are common.
    "action", "model", "question", "mode", "kind", "protocol", "manifest",
    "memory", "producer", "attempt", "explanation", "relationship", "artifacts",
    "reason", "source", "target", "label", "score", "notes", "summary",
    "outcome", "method", "context", "prompt", "answer", "message", "role",
}

#: Schemas that describe what a *deployed decision* runs on. A gap here is worth
#: reporting; a gap in an experiment's own receipt schema usually just means the
#: experiment is finished. Both are still computed — this only ranks them.
LOAD_BEARING_SCHEMAS = (
    "contracts/", "provenance/", "research/integrity/",
)


def bucket(relative: str) -> str:
    if relative.startswith(TESTS):
        return "tests"
    if relative.startswith(PRODUCTION):
        return "production"
    if relative.startswith(RESEARCH):
        return "research"
    return "other"


def declared_fields(document: object, found: set[str]) -> set[str]:
    """Every property name declared anywhere in a JSON Schema."""
    if isinstance(document, dict):
        properties = document.get("properties")
        if isinstance(properties, dict):
            found.update(properties.keys())
        for value in document.values():
            declared_fields(value, found)
    elif isinstance(document, list):
        for value in document:
            declared_fields(value, found)
    return found


def python_files() -> list[pathlib.Path]:
    out = []
    for path in ROOT.rglob("*.py"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        out.append(path)
    return sorted(out)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()

    schemas = sorted(
        [p for p in ROOT.rglob("*.schema.json") if not any(d in p.parts for d in SKIP_DIRS)]
        + [p for p in ROOT.glob("contracts/*/schema.json")]
    )

    fields: dict[str, set[str]] = {}
    for schema in schemas:
        try:
            document = json.loads(schema.read_text(encoding="utf-8"))
        except ValueError:
            continue
        relative = schema.relative_to(ROOT).as_posix()
        for field in declared_fields(document, set()):
            if field in TOO_GENERIC:
                continue
            fields.setdefault(field, set()).add(relative)

    sources = [(p.relative_to(ROOT).as_posix(), p.read_text(encoding="utf-8", errors="ignore"))
               for p in python_files()]

    report: dict[str, dict] = {}
    for field in sorted(fields):
        # A write is an assignment, a keyword argument, a dict-literal key, a
        # subscript assignment, or a setdefault.
        #
        # The subscript case was missing on the first run of this census, which
        # reported `recheck_reference` as written by nothing while
        # `provenance/warrant_recheck.py:101` writes it as
        # `updated["recheck_reference"] = reference`. Grep-shaped evidence fails
        # in exactly one direction here — it invents gaps rather than hiding
        # them — so every remaining gap in the output is a candidate to confirm
        # by reading, never a finding on its own.
        escaped = re.escape(field)
        write = re.compile(
            rf'(\b{escaped}\s*=(?!=))'              # binding, kwarg, attribute
            rf'|(["\']{escaped}["\']\s*:)'          # dict literal key
            rf'|(\[["\']{escaped}["\']\]\s*=(?!=))' # subscript assignment
            rf'|(setdefault\(\s*["\']{escaped}["\'])'
        )
        mention = re.compile(rf'\b{re.escape(field)}\b')
        producers: dict[str, list[str]] = {"production": [], "research": [], "tests": [], "other": []}
        consumers: dict[str, list[str]] = {"production": [], "research": [], "tests": [], "other": []}
        for relative, text in sources:
            if not mention.search(text):
                continue
            where = bucket(relative)
            if write.search(text):
                producers[where].append(relative)
            else:
                consumers[where].append(relative)
        report[field] = {
            "declaredIn": sorted(fields[field]),
            "producers": {k: v for k, v in producers.items() if v},
            "consumers": {k: v for k, v in consumers.items() if v},
        }

    gaps = {
        field: entry for field, entry in report.items()
        if (entry["consumers"].get("production") or entry["producers"].get("production") == [])
        and not entry["producers"].get("production")
        and (entry["producers"].get("research") or entry["producers"].get("tests")
             or entry["consumers"].get("production"))
    }

    unwired = {
        field: entry for field, entry in report.items()
        if not entry["producers"] and not entry["consumers"]
    }

    if args.json:
        print(json.dumps({"fields": report, "emissionGaps": sorted(gaps),
                          "neverReferenced": sorted(unwired)}, indent=2, sort_keys=True))
        return 0

    print(f"Emission census over {len(schemas)} schemas, {len(fields)} declared field names, "
          f"{len(sources)} Python files.\n")

    print("EMISSION GAPS — consumed or enforced in production, written by no production path:")
    if not gaps:
        print("  (none)")
    for field in sorted(gaps):
        entry = gaps[field]
        prod_writers = entry["producers"]
        where = ", ".join(f"{k}:{len(v)}" for k, v in sorted(prod_writers.items())) or "nothing"
        cons = ", ".join(f"{k}:{len(v)}" for k, v in sorted(entry["consumers"].items())) or "nothing"
        print(f"  {field:28} written by {where:24} read by {cons}")
        for schema in entry["declaredIn"]:
            print(f"    declared: {schema}")

    print("\nDECLARED BUT NEVER REFERENCED IN ANY PYTHON FILE:")
    if not unwired:
        print("  (none)")
    for field in sorted(unwired):
        print(f"  {field:28} {', '.join(unwired[field]['declaredIn'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
