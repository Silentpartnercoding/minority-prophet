#!/usr/bin/env python3
"""KL-001 gate item (3): baseline true-positive recall, before the dual ledger.

The registered target is "preserve 95% of true positives". **95% of what** has
never been measured, and until it is the target cannot fail -- which makes it
decoration rather than a goal, the same defect this programme removed from two
LIN-000 tests.

This measures the denominator. A plain scanner, no dual ledger, no evidence
ledger, no search ledger: pattern matching of the kind any team already has.
Whatever it finds is the number 95% is 95% of.

The scanner is deliberately unimpressive. Making it clever would lower the bar
the dual ledger has to clear, which would flatter the product by understating
what it must beat.

Usage:
    python3 measure_baseline.py --corpus DIR [--json OUT]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys

# One pattern per planted class. A team's existing grep-based CI, no more.
PATTERNS = {
    "hardcoded-credential": re.compile(r"""(?:API_KEY|SECRET|TOKEN)\s*=\s*["'][A-Za-z0-9]{12,}"""),
    "unchecked-return":     re.compile(r"^\s*result\s*=\s*risky_call\(\)", re.M),
    "bare-except":          re.compile(r"^\s*except\s*:", re.M),
    "shell-injection":      re.compile(r"os\.system\([^)]*\+"),
    "missing-timeout":      re.compile(r"requests\.get\([^)]*\)(?![^)]*timeout)"),
}


def verify_manifest(corpus: pathlib.Path) -> bool:
    """The corpus must be the one whose ground truth was frozen. A recall figure
    measured against a corpus that moved afterwards is not a measurement."""
    man = json.loads((corpus / "MANIFEST.json").read_text())
    for rel, digest in man.items():
        p = corpus / rel
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != digest:
            return False
    return True


def scan(corpus: pathlib.Path) -> dict[str, set[tuple[str, str]]]:
    found: dict[str, set[tuple[str, str]]] = {}
    for repo in sorted(p for p in corpus.iterdir() if p.is_dir()):
        hits = set()
        for f in sorted(repo.rglob("*.py")):
            text = f.read_text()
            for kind, pat in PATTERNS.items():
                if pat.search(text):
                    hits.add((str(f.relative_to(repo)), kind))
        found[repo.name] = hits
    return found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--json")
    args = ap.parse_args()
    corpus = pathlib.Path(args.corpus)

    if not verify_manifest(corpus):
        print("corpus does not match its manifest; refusing to measure", file=sys.stderr)
        return 1

    truth = json.loads((corpus / "GROUND-TRUTH.json").read_text())
    found = scan(corpus)

    tp = fn = fp = 0
    per_class: dict[str, dict[str, int]] = {}
    for entry in truth["groundTruth"]:
        planted = {(d["file"], d["kind"]) for d in entry["defects"]}
        hits = found.get(entry["repo"], set())
        for item in planted:
            bucket = per_class.setdefault(item[1], {"planted": 0, "found": 0})
            bucket["planted"] += 1
            if item in hits:
                tp += 1
                bucket["found"] += 1
            else:
                fn += 1
        fp += len(hits - planted)

    clean = [e for e in truth["groundTruth"] if e["clean"]]
    false_clean = sum(1 for e in truth["groundTruth"]
                      if e["defects"] and not found.get(e["repo"]))
    report = {
        "schema": "minority-prophet.kl001-baseline.v0.1",
        "corpusManifestDigest": truth["manifestDigest"],
        "plantedDefects": tp + fn, "truePositives": tp, "falseNegatives": fn,
        "falsePositives": fp,
        "baselineRecall": round(tp / (tp + fn), 4) if tp + fn else None,
        "falseCleanRate": round(false_clean / max(len([e for e in truth["groundTruth"]
                                                       if e["defects"]]), 1), 4),
        "cleanRepos": len(clean),
        "falsePositiveReposAmongClean": sum(1 for e in clean if found.get(e["repo"])),
        "perClass": per_class,
        "note": ("Baseline for a plain pattern scanner with no dual ledger. This is "
                 "the denominator the registered 95%-preservation target is a "
                 "percentage of. Deliberately unimpressive: a cleverer baseline "
                 "would lower the bar the dual ledger must clear."),
    }
    if args.json:
        pathlib.Path(args.json).write_text(json.dumps(report, indent=2) + "\n")

    print(f"  planted defects      : {report['plantedDefects']}")
    print(f"  true positives       : {tp}")
    print(f"  false negatives      : {fn}")
    print(f"  false positives      : {fp}")
    print(f"  BASELINE RECALL      : {report['baselineRecall']:.1%}")
    print(f"  false-clean rate     : {report['falseCleanRate']:.1%}")
    print()
    for kind, b in sorted(per_class.items()):
        print(f"    {kind:24s} {b['found']:>3d}/{b['planted']:<3d} "
              f"= {b['found']/b['planted']:.0%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
