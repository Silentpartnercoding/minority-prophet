# Canonical replication protocol v1

Status: preregistered before execution

This protocol defines fresh records `EXP003R` through `EXP008R`. They replay
the immutable archived replica implementations; they do not retroactively make
`EXP003` through `EXP008` canonical and do not establish real-world validity.

## Frozen source boundary

- `research/evidence/2026-08-04/archives/minority-prophet-handoff.zip`
- `research/evidence/2026-08-04/archives/minority-prophet-oneshot.zip`
- `experiments/exp008_shootout.py`

The runner records SHA-256 digests of both archives, every executed Python
member, the public EXP008 runner, and every derived output. To make the archive
code portable, it performs one mechanical transformation in an isolated
temporary directory: the hard-coded `/home/claude` prefix is replaced with the
temporary workspace path. No algorithm, seed, threshold, or sample size is
changed.

## Frozen executions

| Record | Archived implementation | Configuration | Required result |
| --- | --- | --- | --- |
| EXP003R | `handoff/reference/exp003.py` | 200 worlds; seed 7 | raw JSONL, summary, successful exit |
| EXP004R | `exp004.py` and corrected-axis `exp004b.py` | 300 worlds; seed 7; 21 levels | both JSON outputs, successful exits |
| EXP005R | `exp005.py` | 300 worlds; seed 7; 21 levels | JSON output, successful exit |
| EXP006R | `final/results/exp006_h5.py` | 300 worlds; seed 7; 21 levels | JSON output and explicit H5 verdict |
| EXP007R | `final/results/exp007_finisher.py` | 10 seeds x 150 worlds; optimizer budget 45 as archived | multi-seed result and completed optimizer result |
| EXP008R | `experiments/exp008_shootout.py` | 100 worlds; seeds 1–5 | complete shootout table, successful exit |

## Hypotheses and verdict rules

- EXP003R reproduces the archived lineage and aggregation table byte-for-byte
  across two clean runs.
- EXP004R reproduces both the root-set and corrected attribution sweeps
  byte-for-byte across two clean runs.
- EXP005R reproduces the side-confusion sweep byte-for-byte across two clean
  runs.
- EXP006R reproduces its H5 sweep and emits the archived hypothesis verdict
  byte-for-byte across two clean runs. The scientific verdict is whatever the
  program emits; null or rejection is retained.
- EXP007R passes only if both promised sections are implemented and produce
  results. A zero exit status alone is insufficient. Placeholders, missing
  optimizer results, or `None` results produce `incomplete`, not `pass`.
- EXP008R reproduces the complete comparison table byte-for-byte across two
  clean runs.

Each record receives one of `reproduced`, `not-reproduced`, `incomplete`, or
`execution-error`. No record or row may be selectively omitted.

## Execution and independence

The protocol commit must exist before execution. The runner must be invoked
from a clean detached worktree at that commit. Two separate invocations use new
temporary directories and child processes. Their output hashes are compared.
Python 3.10 or newer and the standard library are the only runtime dependency.
The result receipt records the exact protocol commit, Python implementation and
version, operating system, commands, exit codes, and output hashes.

## Promotion boundary

Only the new `R` record may enter the canonical registry, and only with its
honest verdict. A reproduced archived implementation validates deterministic
portability of that implementation—not the broader theory, external data, or a
repository-native reimplementation.
