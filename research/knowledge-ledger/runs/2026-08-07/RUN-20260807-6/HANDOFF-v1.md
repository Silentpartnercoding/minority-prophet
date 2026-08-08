# HANDOFF v1 — RUN-20260807-6

Two bounded tasks done; **the program is closed again. KL-001 carries no
committed gate** — its real first gate is named and costed in its STATUS,
and committing it is yours.

## Where the work is

```
worktree  $HOME/Development/minority-prophet-first-transmission
branch    agent/knowledge-ledger-run-20260807-1
base      9646626  (RUN-20260807-5's delivery record)
head      the closing-packet commit carrying this file
window    2026-08-07T23:23:11Z -> END-UTC.txt
```

Commits: `0e09da7` (open), `b9a30ef` (KL-011 correction), `1bcf474` (FC1
registration), `d418e7b` (FC1 execution, E4 fails as registered), `d76055b`
(FC1.1 registration), `d267e9d` (verdict (a), FINDING, KL-001 record),
plus this packet. Tests: 74 root + 88 KL-000, both green; KL-000 untouched.

## PR #17 — untouched, and this run's output belongs in it

`agent/kl-000-conformance` is pushed at `650f9ee` and draft PR #17 is open;
this run did not amend, force-push, or rebuild it, per instruction.

**Flag for you:** this run's commits *do* belong in that PR's story — the
KL-011 correction removes a stale blocker the PR's diff still carries, and
the KL-001 finding is the first downstream use of the artifact the PR
presents. Options, yours to choose: cherry-pick `0e09da7..HEAD` onto
`agent/kl-000-conformance` and push (the PR is a draft; appending commits is
ordinary), or leave PR #17 as the KL-000 close-out and deliver this run in a
follow-up PR. This run took neither action.

## Decisions that are yours

| # | Decision |
|---|---|
| 1 | Whether this run's commits join PR #17 or a follow-up (above) |
| 2 | **Commit KL-001's real first gate** (mapping pipeline + frozen corpus + false-clean/recall endpoints + v0.2 preregistration; ~one focused run; spend zero unless a metered model enters the pipeline, which needs your authorization). Until committed it is a named gate only |
| 3 | KL-011's own preregistration at v0.2 — its prerequisite blocker is discharged; everything else about it awaits its own work |
| 4 | A1/A2 — still open (4 and 19,152 worlds), untouched by this run |
| 5 | Promotion of anything into canonical records — still never performed |

## Known-stale / observations

- `EXPERIMENT-REGISTRY.json` still `seeded-not-executed` for KL-000 —
  deliberate, unchanged.
- New remote branch `codex/exp009-confirmatory` appeared (ENV-101): someone
  else's work; this program's runs should no longer assume a single-writer
  remote.
- FC1's E4 mis-registration is preserved with its failure (REG-101); FC1.1
  is the correction of record.

## How anyone resumes

Read `KL-000/FINAL-RECORD.md`, then `KL-001/first-check/FINDING-FC1.md`,
then this packet. KL-001 and KL-011 both stay `seeded` with corrected
records; ten other kernels are untouched. The first-transaction gate is
**NOT REACHED**. The program is closed with no committed gate outstanding.
