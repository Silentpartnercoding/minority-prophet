#!/usr/bin/env python3
"""KL-016 v0.2 primary endpoint: root ratio of a conjecture's pre-cutoff citers.

For origin work W and cutoff year T:

  S     = works citing W published before T
  edges = for each work in S, the subset of its references that are ALSO in S
  roots = works in S with no reference inside S
  ratio = |roots| / |S|

This is `rootSet` from formal/lean/MinorityProphetCore/Defs.lean applied to a
real citation graph: a work whose support descends from other support in the
same set is not a root. Mechanical throughout -- no judgement about content.

WHAT THE RATIO IS NOT. It is the root structure of the literature CITING the
origin work, which is only a proxy for "support for the conjecture". Where the
origin work is a landmark cited for other reasons the proxy is weak, and that is
reported per case rather than averaged away.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request

API = "https://api.openalex.org/works"
MIN_CITING = 30  # registered in COLLECTION-SPEC-v0.2.json invalidationCondition


def _get(url: str, mailto: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": f"mailto:{mailto}"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read())


def citing_before(origin_id: str, cutoff_year: int, mailto: str) -> list[dict]:
    """Every work citing `origin_id` published strictly before `cutoff_year`."""
    short = origin_id.rsplit("/", 1)[-1]
    cursor, out = "*", []
    while cursor:
        url = f"{API}?" + urllib.parse.urlencode({
            "filter": f"cites:{short},publication_year:<{cutoff_year}",
            "select": "id,publication_year,referenced_works",
            "per_page": 200, "cursor": cursor})
        page = _get(url, mailto)
        out.extend(page["results"])
        cursor = page["meta"].get("next_cursor")
        time.sleep(0.3)
        if not page["results"]:
            break
    return out


def root_ratio(works: list[dict]) -> dict:
    ids = {w["id"] for w in works}
    roots, derived = [], []
    blind_roots = []   # root ONLY because the index records no references at all
    internal_edges = 0
    for w in works:
        refs = w.get("referenced_works") or []
        inside = [r for r in refs if r in ids]
        internal_edges += len(inside)
        if inside:
            derived.append(w["id"])
        else:
            roots.append(w["id"])
            if not refs:
                blind_roots.append(w["id"])
    n = len(works)
    informative = n - len(blind_roots)
    informative_roots = len(roots) - len(blind_roots)
    return {
        "citing_works": n,
        "roots": len(roots),
        "derived": len(derived),
        "internal_edges": internal_edges,
        "root_ratio": round(len(roots) / n, 4) if n else None,
        # THE CONFOUND, MEASURED. A work whose references the index does not
        # record is a root by default -- HRI1-BLOCKER-20260816.md's population,
        # appearing inside this measurement. Without this split the ratio cannot
        # be told apart from an indexing artefact.
        "blind_roots": len(blind_roots),
        "blind_root_share_of_roots": round(len(blind_roots) / len(roots), 4) if roots else None,
        "works_recording_references": informative,
        "root_ratio_among_works_recording_references":
            round(informative_roots / informative, 4) if informative else None,
    }


CASES = [
    # case, origin OpenAlex id, cutoff year, arm
    ("hirsch", None, 2010, "refuted"),
    ("hedetniemi", None, 2019, "refuted"),
    ("connes-embedding", None, 2020, "refuted"),
    ("sensitivity", None, 2019, "proved"),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--origins", required=True)
    parser.add_argument("--mailto", default="silentpartnerholdings@gmail.com")
    parser.add_argument("--out", default="-")
    args = parser.parse_args()

    origins = {f["case"]: f for f in json.load(open(args.origins))["findings"]}
    results = []
    for case, _, cutoff, arm in CASES:
        found = origins.get(case, {})
        if not found.get("identified"):
            results.append({"case": case, "arm": arm, "status": "unassignable",
                            "reason": "origin not identified at gate 1"})
            continue
        works = citing_before(found["match"]["id"], cutoff, args.mailto)
        row = {"case": case, "arm": arm, "cutoff_year": cutoff,
               "origin": found["match"]["id"], "origin_title": found["match"]["title"]}
        if len(works) < MIN_CITING:
            row.update(status="unassignable",
                       reason=f"pre-cutoff citing set {len(works)} < {MIN_CITING}",
                       citing_works=len(works))
        else:
            row.update(status="measured", **root_ratio(works))
        results.append(row)
        print(f"  {case}: {row['status']} "
              f"({row.get('citing_works','-')} citers, ratio {row.get('root_ratio','-')})",
              file=sys.stderr)

    payload = {"endpoint": "kl016.v0.2.root-ratio.primary", "minCiting": MIN_CITING,
               "results": results}
    text = json.dumps(payload, indent=2) + "\n"
    (sys.stdout.write(text) if args.out == "-" else open(args.out, "w").write(text))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
