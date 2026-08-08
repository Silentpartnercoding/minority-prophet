"""Acquire frozen HGD-2 software detector evidence."""

from __future__ import annotations

import hashlib
import json
import math
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = ROOT / "artifacts" / "hgd2-source"
GOOD_ROOT = SOURCE_ROOT / "extracted"
BAD_ROOT = SOURCE_ROOT / "extracted100"
GOOD_ARCHIVE = SOURCE_ROOT / "sard101.zip"
BAD_ARCHIVE = SOURCE_ROOT / "sard100.zip"
FLAWFINDER = ROOT / "artifacts" / "hgd2-tools" / "venv" / "bin" / "flawfinder"
OUTPUT = SOURCE_ROOT / "software-detector-records.json"
EXPECTED = {
    GOOD_ARCHIVE: "19b7059d067c093d078c6b34d1ec669ccd648aa5b8507ca3fb49d58324bb802b",
    BAD_ARCHIVE: "423f20e8ead850bf64cd93cd4a73dc1161d7b5bb6036328e16fc32e27d09f0d1",
}


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest(path: Path) -> dict:
    run = json.loads(path.read_text())["runs"][0]
    prop = run["properties"]
    taxa = run.get("taxonomies", [{}])[0].get("taxa", [])
    return {
        "case": path.parent.name,
        "state": prop["state"],
        "status": prop["status"],
        "pairs": tuple(prop.get("pairs", [])),
        "cwe": str(taxa[0]["id"]) if taxa else None,
        "artifacts": tuple(item["location"]["uri"] for item in run.get("artifacts", [])),
    }


def selected_pairs() -> tuple[list[tuple[dict, dict]], set[str]]:
    goods = {item["case"]: item for item in (manifest(p) for p in GOOD_ROOT.glob("*/manifest.sarif"))}
    bads = {item["case"]: item for item in (manifest(p) for p in BAD_ROOT.glob("*/manifest.sarif"))}
    pairs = []
    for good in goods.values():
        if good["status"] not in {"accepted", "candidate"} or good["state"] != "good":
            continue
        for bad_id in good["pairs"]:
            bad = bads.get(bad_id)
            if not bad or bad["status"] not in {"accepted", "candidate"} or bad["state"] != "bad":
                continue
            if good["case"] not in bad["pairs"] or good["cwe"] != bad["cwe"]:
                continue
            pairs.append((good, bad))
    ordered = sorted(pairs, key=lambda item: (
        hashlib.sha256(f"{item[0]['case']}|{item[1]['case']}".encode()).hexdigest(),
        item[0]["cwe"], item[0]["case"], item[1]["case"],
    ))
    development = set()
    for good, bad in ordered[: math.ceil(0.20 * len(ordered))]:
        development.update((good["case"], bad["case"]))
    return pairs, development


def command(name: str, source: Path) -> list[str]:
    if name == "clang_analyze":
        return ["clang", "--analyze", "-Xanalyzer", "-analyzer-output=text", str(source)]
    if name == "clang_warning":
        return ["clang", "-fsyntax-only", "-Wall", "-Wextra", str(source)]
    if name == "clang_security":
        return ["clang", "-fsyntax-only", "-Wall", "-Wformat", "-Wformat-security",
                "-Wdeprecated-declarations", str(source)]
    if name == "flawfinder_1":
        return [str(FLAWFINDER), "--csv", "--dataonly", "--quiet", "--minlevel=1", str(source)]
    if name == "flawfinder_3":
        return [str(FLAWFINDER), "--csv", "--dataonly", "--quiet", "--minlevel=3", str(source)]
    raise ValueError(name)


def tool_vote(name: str, source: Path) -> dict:
    proc = subprocess.run(command(name, source), capture_output=True, text=True, timeout=30)
    raw = proc.stdout + proc.stderr
    if proc.returncode != 0:
        return {"state": "unknown", "vote": None, "exit": proc.returncode, "raw": raw}
    if name.startswith("flawfinder"):
        lines = [line for line in proc.stdout.splitlines() if line.strip()]
        vote = len(lines) > 1
    else:
        vote = bool(re.search(r"\bwarning:|\berror:|\bnote:.*bug", raw, re.IGNORECASE))
    return {"state": "supported", "vote": int(vote), "exit": proc.returncode, "raw": raw}


DANGEROUS = re.compile(r"\b(gets|strcpy|strcat|sprintf|system|popen|scanf|memcpy|printf|syslog)\s*\(")
UNCHECKED = re.compile(r"\b(gets|scanf|fgets|read|recv)\s*\(")
SINK = re.compile(r"\b(strcpy|strcat|sprintf|system|popen|printf|syslog|memcpy)\s*\(")


def lexical_vote(name: str, text: str) -> dict:
    if name == "lexical_dangerous":
        vote = bool(DANGEROUS.search(text))
    elif name == "lexical_unchecked":
        vote = bool(UNCHECKED.search(text) and SINK.search(text))
    else:
        raise ValueError(name)
    return {"state": "supported", "vote": int(vote), "exit": 0, "raw": "matched" if vote else ""}


def case_source(root: Path, item: dict) -> Path | None:
    files = [root / item["case"] / uri for uri in item["artifacts"]]
    existing = [path for path in files if path.exists() and path.suffix.lower() in {".c", ".cc", ".cpp"}]
    return existing[0] if len(existing) == 1 else None


def main() -> None:
    for path, expected in EXPECTED.items():
        if file_hash(path) != expected:
            raise SystemExit(f"hash mismatch: {path}")
    if not FLAWFINDER.exists():
        raise SystemExit("frozen flawfinder executable is unavailable")
    pairs, development = selected_pairs()
    records = []
    detector_names = ("clang_analyze", "clang_warning", "clang_security", "flawfinder_1",
                      "flawfinder_3", "lexical_dangerous", "lexical_unchecked")
    for good, bad in sorted(pairs, key=lambda item: (item[0]["cwe"], item[0]["case"])):
        for item, root in ((good, GOOD_ROOT), (bad, BAD_ROOT)):
            source = case_source(root, item)
            if source is None:
                continue
            text = source.read_text(errors="replace")
            syntax = subprocess.run(["clang", "-fsyntax-only", str(source)], capture_output=True,
                                    text=True, timeout=30)
            if syntax.returncode != 0:
                continue
            detectors = {}
            for name in detector_names:
                detectors[name] = (lexical_vote(name, text) if name.startswith("lexical")
                                   else tool_vote(name, source))
            records.append({
                "case": item["case"], "pair": bad["case"] if item is good else good["case"],
                "cwe": item["cwe"], "truth": int(item["state"] == "bad"),
                "split": "development" if item["case"] in development else "confirmatory",
                "sourceSha256": file_hash(source), "sourcePath": str(source.relative_to(root)),
                "detectors": detectors,
            })
    packet = {"schema": "minority-prophet.hgd2.software-detector-records.v1",
              "archives": {path.name: expected for path, expected in EXPECTED.items()},
              "detectorFamilies": {
                  "compiler": ["clang_analyze", "clang_warning", "clang_security"],
                  "flawfinder": ["flawfinder_1", "flawfinder_3"],
                  "lexical": ["lexical_dangerous", "lexical_unchecked"],
              }, "records": records}
    OUTPUT.write_text(json.dumps(packet, sort_keys=True, separators=(",", ":")) + "\n")
    print(json.dumps({"records": len(records),
                      "confirmatory": sum(r["split"] == "confirmatory" for r in records),
                      "development": sum(r["split"] == "development" for r in records)}, sort_keys=True))


if __name__ == "__main__":
    main()
