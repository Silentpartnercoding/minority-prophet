#!/usr/bin/env python3
"""KL-016 v0.2 BL-060 negative control.

COLLECTION-SPEC-v0.2.json registers, as effectRequires.negativeControlPopulation,
"a size-matched random sample of mathematics works from the same era with no
citation relationship to the conjecture; the probe must report below the minimum
there".

Without this, a low root ratio in a conjecture's citing set could simply be how
mathematics cites. The control answers that: an unrelated sample from the same
era should be almost all roots, because its members do not cite each other.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request

API = "https://api.openalex.org/works"
SAMPLES = [("2002-2010", 200), ("2011-2019", 88), ("2011-2019", 84), ("2012-2020", 200)]
SEED = 42  # fixed here; a seed chosen after seeing a result is not a control


def sample(era: str, n: int, mailto: str) -> list[dict]:
    url = f"{API}?" + urllib.parse.urlencode({
        "filter": f"publication_year:{era},primary_topic.field.id:fields/26,has_references:true",
        "select": "id,referenced_works", "per_page": min(200, n),
        "sample": n, "seed": SEED})
    request = urllib.request.Request(url, headers={"User-Agent": f"mailto:{mailto}"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read())["results"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mailto", default="silentpartnerholdings@gmail.com")
    parser.add_argument("--out", default="-")
    args = parser.parse_args()

    rows = []
    for era, n in SAMPLES:
        works = sample(era, n, args.mailto)
        ids = {w["id"] for w in works}
        edges = sum(len([r for r in (w.get("referenced_works") or []) if r in ids])
                    for w in works)
        roots = sum(1 for w in works
                    if not [r for r in (w.get("referenced_works") or []) if r in ids])
        rows.append({"era": era, "requested": n, "returned": len(works),
                     "root_ratio": round(roots / len(works), 4) if works else None,
                     "internal_edges": edges})
        time.sleep(0.5)

    payload = {
        "control": "kl016.v0.2.negative-control", "seed": SEED, "samples": rows,
        "interpretation": (
            "Root ratio 1.0 with zero internal edges means an unrelated sample "
            "is entirely roots. A conjecture's citing set measured far below "
            "that is therefore a property of that literature, not of how "
            "mathematics cites in general."),
    }
    text = json.dumps(payload, indent=2) + "\n"
    (sys.stdout.write(text) if args.out == "-" else open(args.out, "w").write(text))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
