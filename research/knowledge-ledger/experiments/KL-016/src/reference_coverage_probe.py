#!/usr/bin/env python3
"""KL-016 feasibility probe: is the ancestry KL-016 consumes actually recorded?

KL-016's registered invalidationCondition says the experiment stops if pre-cutoff
ancestry cannot be reconstructed for three or more of the four refuted cases.
This probe measures the precondition of that condition, BEFORE any case is
scored, so the stop rule is evaluated against a number rather than an
impression.

WHAT IT MEASURES, AND WHAT IT DOES NOT.

It measures the share of works in an era and field that record ANY references at
all. A work recording none is a root by default -- it is the population
HRI1-BLOCKER-20260816.md identifies as carrying the over-count, and the
population in which the method under test has nothing to consume.

It does NOT measure whether the specific pre-cutoff literature of a specific
conjecture is reconstructable. A high field-wide rate does not guarantee any
individual case, and a low one does not quite forbid it. This is a screening
instrument: it can rule a case out cheaply and cannot rule one in.

Run:  python3 research/knowledge-ledger/experiments/KL-016/src/reference_coverage_probe.py
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request

API = "https://api.openalex.org/works"
MATHEMATICS = "fields/26"

# Each refuted case, with the era window its pre-cutoff literature sits in.
CASE_ERAS = [
    ("li-crossing", "1910-1918", 1914),
    ("polya", "1954-1962", 1958),
    ("euler-sum-of-powers", "1962-1970", 1966),
    ("mertens", "1981-1989", 1985),
]
MODERN_CEILING = ("modern-ceiling", "2005-2015", 2010)


def _count(mailto: str, filter_expr: str) -> int:
    url = f"{API}?" + urllib.parse.urlencode({"filter": filter_expr, "per_page": 1})
    request = urllib.request.Request(url, headers={"User-Agent": f"mailto:{mailto}"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read())["meta"]["count"]


def coverage(mailto: str, era: str, field: str = MATHEMATICS) -> dict[str, float | int]:
    base = f"publication_year:{era},primary_topic.field.id:{field}"
    total = _count(mailto, base)
    time.sleep(0.4)
    with_refs = _count(mailto, base + ",has_references:true")
    return {
        "era": era,
        "works": total,
        "works_recording_references": with_refs,
        "share_recording_references": round(with_refs / total, 4) if total else 0.0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mailto", default="silentpartnerholdings@gmail.com")
    parser.add_argument("--out", default="-")
    args = parser.parse_args()

    results = []
    for case_id, era, cutoff_year in CASE_ERAS + [MODERN_CEILING]:
        row = coverage(args.mailto, era)
        row["case"] = case_id
        row["cutoff_year"] = cutoff_year
        results.append(row)
        time.sleep(0.4)

    ceiling = next(r for r in results if r["case"] == "modern-ceiling")
    payload = {
        "probe": "kl016.reference-coverage.v1",
        "source": "OpenAlex works API, has_references filter",
        "field": "Mathematics (OpenAlex fields/26)",
        "results": results,
        "modern_ceiling_share": ceiling["share_recording_references"],
        "note": (
            "share_recording_references is the share of works recording ANY "
            "reference. The complement is the no-ancestry population of "
            "HRI1-BLOCKER-20260816.md, where the method has nothing to consume. "
            "The modern ceiling is reported because no era can exceed what the "
            "index records today; a case is not weak merely by being below 100%, "
            "it is weak by being far below the ceiling."
        ),
    }
    text = json.dumps(payload, indent=2) + "\n"
    if args.out == "-":
        sys.stdout.write(text)
    else:
        with open(args.out, "w") as handle:
            handle.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
