# ORIENTATION — RUN-20260807-6

Opened 2026-08-07T23:23:11Z on branch `agent/knowledge-ledger-run-20260807-1`,
HEAD `9646626` (RUN-20260807-5's delivery record). Worktree clean at start
except this run directory. Environment unchanged from run-5. Prompt capture:
agent transcription, unverified, sixth consecutive run.

## 1. The reopening, recorded

The program closed at RUN-20260807-5 with no committed gate outstanding.
This run reopens it deliberately, on owner direction, for two bounded tasks:
correct KL-011's stale blocker (discharged by evidence its record predates),
and execute KL-001's already-named narrow first check with an honest answer
to whether that check is anything more than KL-000's I2 in costume. Per M22,
the reopening is stated rather than smoothed over, and the run closes the
program again at its end unless KL-001's evidence commits a gate.

## 2. Delivery state, verified read-only

`agent/kl-000-conformance` exists on the github remote at exactly
`650f9ee` — the head RUN-20260807-5 built, pushed by the owner unmodified —
and **draft PR #17 is open** (base `main`, title as registered). Per
instruction, nothing this run does touches that branch or PR; anything
produced here that belongs in it is flagged in HANDOFF for the owner.

Environment observation (M5 discipline — state change, not measurement
error): the fetch surfaced a new remote branch `codex/exp009-confirmatory`,
not present at RUN-20260807-5's fetch. Someone else's work; recorded,
untouched, and out of scope.

## 3. Task 1 preview — KL-011's stale blocker

`KL-011/STATUS.json` (`reviewedByRun: RUN-20260807-1`) still reads "BLOCKED
on KL-000's next gate… the independent reimplementation that KL-000 needs is
the SAME artifact KL-011 needs, so it should be commissioned once." That
artifact exists and did exactly what the record hoped: commissioned once
(IND-20260807-1/-2/-3), zero-dependency Rust, agreeing on the evaluator, the
full conclusion function, and the canonical form for the two pinned
receipts. The record will be corrected as a correction — superseded text
preserved, evidence cited, genuine remainder stated — and the state stays
`seeded`. This is the stale-self-description family again (PROV-005's
cache-as-remote, ART-101's stale result header, TEST-101's inherited
projection, the registry's deliberate-but-different case): a record whose
truth expired while the world moved, detected only by re-deriving from
evidence rather than reading the record.

## 4. Task 2 preview — KL-001's narrow first check, and the question it must answer

The named check: construct one repository whose mandatory file coverage is
incomplete; show the pipeline cannot emit a clean conclusion. Preregistered
before running, executed with the existing evaluator (the only pipeline
component that exists). The epistemic question is answered in the finding
document, and the working hypothesis going in — to be tested, not assumed —
is (a): with only the evaluator in play, "mandatory file" maps to "declared
location" by pure renaming, the constructed world is structurally inside
KL-000's 176,120-world enumeration (C08 is literally this shape), and the
check adds no evidence about the evaluator. What the repository framing
*would* add — the pipeline that maps repository reality into ledgers, where
scope declaration honesty (ADV-001) actually lives, and a corpus with
planted defects testing the false-clean endpoint — does not exist yet and is
exactly KL-001's real first gate. The preregistration states both possible
verdicts and what each implies before anything runs.

## 5. What must not move

KL-000 `adversarial-passed` at v1.3.0, untouched. PR #17 untouched. Eleven
kernels stay seeded unless KL-001's evidence genuinely advances it — and the
working hypothesis is that it will not advance past `seeded`, gaining a
corrected record rather than a new state.
