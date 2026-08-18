#!/usr/bin/env python3
"""KL-016 v0.2 gate 1: can each conjecture's originating publication be found?

COLLECTION-SPEC-v0.2.json's invalidationCondition: "If the originating
publication of a conjecture cannot be identified in the index ... that case is
reported as unassignable and is NOT replaced."

Every search string below is fixed here and recorded with its result, so the
identification is auditable rather than asserted. A case that needs a search
string invented after seeing what returns nothing is unassignable, not
retried.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request

API = "https://api.openalex.org/works"

# (case, registered search, expected year, note on what the origin IS)
CANDIDATES = [
    ("borsuk", "Drei Satze uber die n-dimensionale euklidische Sphare", 1933,
     "Borsuk 1933, Fundamenta Mathematicae"),
    ("hirsch", "Linear Programming and Extensions", 1963,
     "Hirsch stated the conjecture in a 1957 letter; its first published "
     "appearance is Dantzig's 1963 monograph"),
    ("hedetniemi", "Homomorphisms of graphs and automata", 1966,
     "Hedetniemi 1966, University of Michigan technical report"),
    ("connes-embedding", "Classification of injective factors", 1976,
     "Connes 1976, Annals of Mathematics"),
    ("fermat", "", 1637,
     "NO PUBLICATION EXISTS. A marginal note in Fermat's copy of Diophantus, "
     "published posthumously in 1670 by his son. Registered as a known-null "
     "case: it tests that the gate reports unassignable rather than "
     "substituting a proxy."),
    ("poincare", "Cinquieme complement a l'analysis situs", 1904,
     "Poincare 1904, Rendiconti del Circolo Matematico di Palermo"),
    ("sensitivity", "On the degree of boolean functions as real polynomials", 1992,
     "Nisan and Szegedy 1992, where the conjecture is posed"),
]


def search(query: str, mailto: str, per_page: int = 5) -> list[dict]:
    if not query:
        return []
    url = f"{API}?" + urllib.parse.urlencode(
        {"search": query, "per_page": per_page,
         "select": "id,doi,display_name,publication_year,cited_by_count,type"})
    request = urllib.request.Request(url, headers={"User-Agent": f"mailto:{mailto}"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read())["results"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mailto", default="silentpartnerholdings@gmail.com")
    parser.add_argument("--out", default="-")
    args = parser.parse_args()

    findings = []
    for case, query, year, note in CANDIDATES:
        hits = search(query, args.mailto)
        # A hit counts only if the year matches within one year. Anything else
        # would be choosing a work because it is convenient.
        matches = [h for h in hits
                   if h.get("publication_year") and abs(h["publication_year"] - year) <= 1]
        findings.append({
            "case": case,
            "registered_search": query,
            "expected_year": year,
            "note": note,
            "identified": bool(matches),
            "match": ({"id": matches[0]["id"], "doi": matches[0].get("doi"),
                       "title": matches[0]["display_name"],
                       "year": matches[0]["publication_year"],
                       "cited_by_count": matches[0]["cited_by_count"]}
                      if matches else None),
            "top_non_matching": [
                {"title": h["display_name"], "year": h.get("publication_year")}
                for h in hits[:3]] if not matches else [],
        })
        time.sleep(0.4)

    identified = [f["case"] for f in findings if f["identified"]]
    unassignable = [f["case"] for f in findings if not f["identified"]]
    payload = {
        "gate": "kl016.v0.2.origin-identification",
        "findings": findings,
        "identified": identified,
        "unassignable": unassignable,
        "note": ("Search strings are registered in this file and were not "
                 "revised after seeing results. A case identified only by a "
                 "search invented afterwards would be selection, not "
                 "identification."),
    }
    text = json.dumps(payload, indent=2) + "\n"
    (sys.stdout.write(text) if args.out == "-"
     else open(args.out, "w").write(text))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
