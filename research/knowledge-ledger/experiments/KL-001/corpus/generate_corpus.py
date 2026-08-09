#!/usr/bin/env python3
"""KL-001 corpus: seeded repositories with machine-checkable planted defects.

Gate item (2). Deterministic and dependency-free: no metered model touches this,
so it carries zero spend. Every defect is planted by construction, so ground
truth is known exactly rather than adjudicated -- which is the only way the
recall numbers in `measure_baseline.py` mean anything.

Digest-manifested BEFORE any evaluation, per the gate: a corpus whose manifest
is written after the scanner has seen it cannot support a recall claim.

Defect classes are chosen to be detectable by a plain scanner without semantic
analysis, because the baseline this corpus exists to establish is what a plain
scanner achieves. A corpus only a clever scanner can solve would flatter the
dual ledger by making its baseline artificially low.

Usage:
    python3 generate_corpus.py --out DIR [--repos 60] [--seed 20260809]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import struct

DEFECTS = {
    "hardcoded-credential": 'API_KEY = "{tok}"  # planted',
    "unchecked-return": "result = risky_call()  # planted: return value never checked",
    "bare-except": "try:\n    step()\nexcept:  # planted: bare except\n    pass",
    "shell-injection": 'os.system("rm -rf " + user_input)  # planted',
    "missing-timeout": "requests.get(url)  # planted: no timeout",
}
CLEAN = [
    "def add(a, b):\n    return a + b\n",
    "def normalise(items):\n    return sorted(set(items))\n",
    'def load(path):\n    with open(path, encoding="utf-8") as fh:\n        return fh.read()\n',
]


class Words:
    """The LIN-000 generator, reused so the corpus is reproducible from a seed
    with no language-specific PRNG -- the F11 lesson, applied here from the
    start rather than after a failed commission."""

    def __init__(self, seed: int) -> None:
        self._seed, self._i = struct.pack(">Q", seed), 0

    def below(self, n: int) -> int:
        limit = (1 << 32) - ((1 << 32) % n)
        while True:
            blk, off = divmod(self._i, 8)
            word = struct.unpack(">I", hashlib.sha256(
                self._seed + struct.pack(">Q", blk)).digest()[4 * off:4 * off + 4])[0]
            self._i += 1
            if word < limit:
                return word % n


def build(out: pathlib.Path, repos: int, seed: int) -> dict:
    words = Words(seed)
    truth = []
    for r in range(repos):
        repo = out / f"repo-{r:03d}"
        (repo / "src").mkdir(parents=True, exist_ok=True)
        n_files = 2 + words.below(4)
        planted: list[dict] = []
        for f in range(n_files):
            lines = [CLEAN[words.below(len(CLEAN))] for _ in range(1 + words.below(3))]
            # roughly one file in three carries exactly one planted defect
            if words.below(3) == 0:
                kind = sorted(DEFECTS)[words.below(len(DEFECTS))]
                # Deliberately NOT a real credential shape. An earlier version
                # emitted AKIA-prefixed tokens -- the genuine AWS access-key
                # format -- and the public-boundary check rejected the corpus.
                # It was right: 60 repositories of AKIA strings would trip every
                # secret scanner that ever sees this repo and would be
                # indistinguishable from a real leak. Synthetic fixtures must
                # look synthetic.
                body = DEFECTS[kind].format(tok="EXAMPLEONLYNOTREAL" + "".join(
                    "0123456789"[words.below(10)] for _ in range(8)))
                at = words.below(len(lines) + 1)
                lines.insert(at, body + "\n")
                planted.append({"file": f"src/mod_{f}.py", "kind": kind})
            (repo / "src" / f"mod_{f}.py").write_text("\n".join(lines))
        truth.append({"repo": repo.name, "files": n_files,
                      "defects": planted, "clean": not planted})
    return {"schema": "minority-prophet.kl001-corpus.v0.1", "seed": seed,
            "repos": repos, "defectClasses": sorted(DEFECTS),
            "groundTruth": truth,
            "totalDefects": sum(len(t["defects"]) for t in truth),
            "cleanRepos": sum(1 for t in truth if t["clean"])}


def manifest(out: pathlib.Path) -> dict:
    files = sorted(p for p in out.rglob("*.py") if p.is_file())
    return {str(p.relative_to(out)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in files}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--repos", type=int, default=60)
    ap.add_argument("--seed", type=int, default=20260809)
    args = ap.parse_args()
    out = pathlib.Path(args.out)
    truth = build(out, args.repos, args.seed)
    man = manifest(out)
    truth["manifestDigest"] = hashlib.sha256(
        json.dumps(man, sort_keys=True).encode()).hexdigest()
    (out / "MANIFEST.json").write_text(json.dumps(man, indent=2, sort_keys=True) + "\n")
    (out / "GROUND-TRUTH.json").write_text(json.dumps(truth, indent=2) + "\n")
    print(f"  repos {truth['repos']}   files {len(man)}   "
          f"planted defects {truth['totalDefects']}   clean repos {truth['cleanRepos']}")
    print(f"  manifest digest {truth['manifestDigest'][:16]}... "
          f"(written before any evaluation)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
