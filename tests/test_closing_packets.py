"""Closing-packet completeness: enforcement, not prose (methodology note M26).

RESEARCH-BACKLOG-v1.json went unwritten in two consecutive runs
(RUN-20260807-5/-6, constraint PKT-101). The evidenced cause -- owner
correction, RUN-20260807-7 -- is instruction decay, not a missing habit:
only RUN-1's brief enumerated the packet's members; every later brief said
"the full versioned packet", a concept, and output tracked instruction
exactly once the enumeration aged out of context. The M24 defect (concepts
are not quantifiers), one layer up, in the instructions themselves.

The fix is two-sided. This test is side 1: a run directory containing
END-UTC.txt has declared itself closed, and a closed run missing any
required artifact fails the suite -- the REQUIRED list below is the
enumeration of record. Side 2 is a REQUIREMENT on operator briefs (M26): a
brief that requires a packet enumerates its members or cites this list by
path; a brief that names only the concept is defective, and a run receiving
one says so before executing.
"""

from __future__ import annotations

from pathlib import Path

import pytest

RUNS_ROOT = Path(__file__).resolve().parents[1] / "research" / "knowledge-ledger" / "runs"

REQUIRED = [
    "START-UTC.txt",
    "END-UTC.txt",
    "git-status-before.txt",
    "git-status-after.txt",
    "inputs/PROMPT.txt",
    "DRAFT-RUN-REPORT-v1.md",
    "CONSTRAINTS-v1.json",
    "HANDOFF-v1.md",
    "KERNEL-STATUS-SNAPSHOT-v1.json",
    "NEXT-RUN-PROPOSAL-v1.md",
    "RESEARCH-BACKLOG-v1.json",
    "METHODOLOGY-NOTES.md",
    "run-manifest.json",
    "environment-lock.txt",
    "pip-freeze.txt",
]

# The two git-status captures are legitimately empty when the tree is clean;
# every other artifact must have content -- an empty placeholder is the same
# defect as an absent file wearing a filename.
MAY_BE_EMPTY = {"git-status-before.txt", "git-status-after.txt"}


def closed_runs():
    if not RUNS_ROOT.exists():
        return []
    return sorted(
        run for day in RUNS_ROOT.iterdir() if day.is_dir()
        for run in day.iterdir()
        if run.is_dir() and (run / "END-UTC.txt").exists()
    )


@pytest.mark.parametrize("run", closed_runs(), ids=lambda r: r.name)
def test_closed_run_carries_every_required_packet_artifact(run):
    missing = [name for name in REQUIRED if not (run / name).exists()]
    assert not missing, (
        f"{run.name} declared itself closed (END-UTC.txt exists) but is "
        f"missing required packet artifacts: {missing}. A close that omits "
        "a required artifact is not a close (PKT-101/M26)."
    )
    empty = [
        name for name in REQUIRED
        if name not in MAY_BE_EMPTY and (run / name).stat().st_size == 0
    ]
    assert not empty, (
        f"{run.name} has empty required packet artifacts: {empty}. An empty "
        "placeholder is an absent file wearing a filename."
    )


def test_the_defect_that_motivated_this_check_stays_fixed():
    """RUN-5's and RUN-6's backlogs exist, are non-empty, and carry the
    post-hoc completion label they are required to carry."""
    for run_name in ("RUN-20260807-5", "RUN-20260807-6"):
        path = RUNS_ROOT / "2026-08-07" / run_name / "RESEARCH-BACKLOG-v1.json"
        assert path.exists() and path.stat().st_size > 0
        assert "postHocCompletion" in path.read_text()
