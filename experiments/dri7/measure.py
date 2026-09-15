#!/usr/bin/env python3
"""DRI-7 observational measurement.

Reproduces section 6 of OBSERVATIONAL-REPORT.md against a job-control plane's
own ledger. Read-only. Emits aggregates only: no identifiers, no paths, no
message text, no repository names. Cells below MIN_CELL are suppressed so a rate
cannot be reconstructed from a small group.

The corpus measured in the write-up is an operator's private ledger and is not
distributed here. This script is the artifact; its input is not, and nothing it
prints identifies a job, a machine, or a file.

Usage:
    DRI7_LEDGER_STATE=/path/to/state.json \
    DRI7_CONTENT_STORE=/path/to/content-addressed-store \
    python3 experiments/dri7/measure.py
"""

from __future__ import annotations

import hashlib
import json
import os
import pathlib
import subprocess

MIN_CELL = 10

# The corpus is an operator's private ledger and is NOT distributed with this
# repository. Point these at your own control plane to reproduce the method;
# the numbers you get will be your system's, not the ones in the write-up.
LEDGER_STATE = pathlib.Path(os.environ.get("DRI7_LEDGER_STATE", ""))
CONTENT_STORE = pathlib.Path(os.environ.get("DRI7_CONTENT_STORE", ""))

SHA40 = lambda v: isinstance(v, str) and len(v) == 40 and all(c in "0123456789abcdef" for c in v)
SHA64 = lambda v: isinstance(v, str) and len(v) == 64 and all(c in "0123456789abcdef" for c in v)


def suppress(n):
    return n if n == 0 or n >= MIN_CELL else "1-9"


def rate(found, total):
    return round(found / total, 3) if total >= MIN_CELL else None


def corpus_a(jobs):
    """Recorded result commits: a git object identifier plus the repository."""
    records = []
    for job in jobs:
        sha = job.get("resultCommit") or (job.get("workerExit") or {}).get("resultCommit")
        if sha:
            records.append({"sha": sha, "where": job.get("repository")})
    return records


def corpus_b(jobs):
    """Recorded QA artifacts: a content hash plus an absolute filesystem path."""
    records = []
    for job in jobs:
        for artifact in (job.get("verificationEvidence") or {}).get("artifacts") or []:
            if artifact.get("sha256") and artifact.get("reference"):
                records.append({"sha": artifact["sha256"], "where": artifact["reference"]})
    return records


def rule_a(records, well_formed):
    """Record-only: the identifier is well formed and a location is named."""
    return sum(1 for r in records if well_formed(r["sha"]) and r["where"])


def rule_b_commits(records):
    """One dereference of a git object in the repository the record names."""
    checkable = absent = 0
    for record in records:
        where = record["where"]
        if not where or not os.path.isdir(os.path.join(where, ".git")):
            continue  # unverifiable on this host: not a failure
        checkable += 1
        found = subprocess.run(
            ["/usr/bin/git", "-C", where, "cat-file", "-e", f"{record['sha']}^{{commit}}"],
            capture_output=True,
        ).returncode == 0
        if not found:
            absent += 1
    return checkable, absent


def rule_b_paths(records):
    """One dereference of a filesystem path."""
    absent = sum(1 for r in records if not os.path.exists(r["where"]))
    return len(records), absent


def rule_c(records):
    """For absent referents, look by content instead of by location."""
    have = set()
    if CONTENT_STORE.is_dir():
        for path in CONTENT_STORE.rglob("*"):
            if path.is_file():
                try:
                    have.add(hashlib.sha256(path.read_bytes()).hexdigest())
                except OSError:
                    pass
    missing = [r for r in records if not os.path.exists(r["where"])]
    recovered = sum(1 for r in missing if r["sha"] in have)
    return len(missing), recovered


def main():
    if not LEDGER_STATE.name:
        raise SystemExit(
            "set DRI7_LEDGER_STATE to a job-control-plane state file; "
            "no corpus is bundled with this repository"
        )
    jobs = json.loads(LEDGER_STATE.read_text())["jobs"]
    a, b = corpus_a(jobs), corpus_b(jobs)

    a_accepts = rule_a(a, SHA40)
    a_checkable, a_absent = rule_b_commits(a)
    b_accepts = rule_a(b, SHA64)
    b_total, b_absent = rule_b_paths(b)
    c_missing, c_recovered = rule_c(b)

    result = {
        "corpus_a_recorded_result_commits": {
            "n": suppress(len(a)),
            "rule_a_accepts": suppress(a_accepts),
            "rule_a_detects": suppress(len(a) - a_accepts),
            "rule_b_checkable_on_this_host": suppress(a_checkable),
            "rule_b_unverifiable_on_this_host": suppress(len(a) - a_checkable),
            "rule_b_absent": suppress(a_absent),
            "rule_b_rate": rate(a_absent, a_checkable),
            "share_found_only_by_looking_twice":
                rate(a_absent, (len(a) - a_accepts) + a_absent),
        },
        "corpus_b_recorded_qa_artifacts": {
            "n": suppress(len(b)),
            "rule_a_accepts": suppress(b_accepts),
            "rule_a_detects": suppress(len(b) - b_accepts),
            "rule_b_absent": suppress(b_absent),
            "rule_b_rate": rate(b_absent, b_total),
            "rule_c_recoverable_by_content": suppress(c_recovered),
            "rule_c_rate": rate(c_recovered, c_missing),
            "genuinely_unrecoverable": suppress(c_missing - c_recovered),
        },
        "boundary": (
            "Unverifiable is not absent: a record naming a repository that does not exist "
            "on this host has not failed. Rates are over what one machine can dereference. "
            "One host, one control plane, six weeks; not a population estimate."
        ),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
