#!/usr/bin/env python3
"""KL-001's registered experiment: does the dual ledger reduce false-clean?

Runs the same plain scanner as the baseline over the same registered corpus, and
routes its output through the mapping pipeline and the KL-000 evaluator instead
of reading it directly. The scanner is identical in both arms; only the
aggregation differs. Anything else would compare two changes at once.

The endpoints are registered in preregistration.json and pinned by
PROTOCOL-COMMIT.txt. This program reports against them and does not choose them.

Usage:
    python3 run_dual_ledger.py --corpus corpus/frozen-v1 [--json OUT]
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "pipeline"))
sys.path.insert(0, str(HERE / "corpus"))
sys.path.insert(0, str(HERE.parents[3]))          # repository root, for knowledge_ledger

from map_repository import map_repository          # noqa: E402
from measure_baseline import PATTERNS, verify_manifest  # noqa: E402
from knowledge_ledger import evaluate_transaction  # noqa: E402

FAMILY = "pattern-scanner"     # one scanner, therefore one root (MAPPING-RULES M2)


def scan_repo(repo: pathlib.Path) -> dict:
    """The baseline scanner, reporting what it read as well as what it found.

    `read` is the honest part the baseline arm never had to state: a plain
    scanner that silently skips a file it cannot parse still returns 'nothing
    found'. The dual ledger asks which locations were actually searched.
    """
    read, findings, errored = [], [], []
    for f in sorted(repo.rglob("*.py")):
        rel = str(f.relative_to(repo))
        try:
            text = f.read_text()
        except Exception:
            errored.append(rel)
            continue
        read.append(rel)
        for kind, pattern in PATTERNS.items():
            if pattern.search(text):
                findings.append({"file": rel, "kind": kind})
    return {"read": read, "findings": findings, "errored": errored}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--json")
    args = ap.parse_args()
    corpus = pathlib.Path(args.corpus)

    if not verify_manifest(corpus):
        print("corpus does not match its manifest; refusing to run", file=sys.stderr)
        return 1
    truth = json.loads((corpus / "GROUND-TRUTH.json").read_text())

    per_repo, tp, fn = [], 0, 0
    per_class: dict[str, dict[str, int]] = {}
    false_clean = 0
    defective = 0

    for entry in truth["groundTruth"]:
        repo = corpus / entry["repo"]
        report = scan_repo(repo)
        transaction = map_repository(repo, {FAMILY: report})
        receipt = evaluate_transaction(transaction)

        planted = {(d["file"], d["kind"]) for d in entry["defects"]}
        located = {(f["file"], f["kind"]) for f in report["findings"]}
        for item in planted:
            bucket = per_class.setdefault(item[1], {"planted": 0, "found": 0})
            bucket["planted"] += 1
            if item in located:
                tp += 1
                bucket["found"] += 1
            else:
                fn += 1

        # A false clean is a defective repository that receives a clean verdict.
        # In the dual-ledger arm the clean verdict is `absent_within_declared_scope`;
        # in the baseline arm it was "the scanner reported nothing".
        clean = receipt["conclusion"] == "absent_within_declared_scope"
        if entry["defects"]:
            defective += 1
            if clean:
                false_clean += 1
        per_repo.append({"repo": entry["repo"], "conclusion": receipt["conclusion"],
                         "defective": bool(entry["defects"]),
                         "roots": receipt["evidence"]["distinctRoots"],
                         "findings": len(report["findings"])})

    recall = tp / (tp + fn) if tp + fn else None
    fc_rate = false_clean / defective if defective else None
    report = {
        "schema": "minority-prophet.kl001-dualledger.v0.1",
        "corpusManifestDigest": truth["manifestDigest"],
        "arm": "dual ledger (mapping pipeline + KL-000 evaluator)",
        "scanner": "identical to the baseline arm",
        "plantedDefects": tp + fn, "truePositives": tp, "falseNegatives": fn,
        "recall": round(recall, 4) if recall is not None else None,
        "falseCleanRate": round(fc_rate, 4) if fc_rate is not None else None,
        "defectiveRepos": defective, "falseCleans": false_clean,
        "perClass": per_class,
        "conclusionCounts": {c: sum(1 for r in per_repo if r["conclusion"] == c)
                             for c in sorted({r["conclusion"] for r in per_repo})},
        "perRepo": per_repo,
    }
    if args.json:
        pathlib.Path(args.json).write_text(json.dumps(report, indent=2) + "\n")

    print(f"  recall            : {recall:.1%}")
    print(f"  false-clean rate  : {fc_rate:.1%}  ({false_clean}/{defective} defective repos)")
    print(f"  conclusions       : {report['conclusionCounts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
