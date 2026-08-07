# ORIENTATION — RUN-20260807-5

Opened 2026-08-07T22:45:21Z on branch `agent/knowledge-ledger-run-20260807-1`,
HEAD `ffbdb60` (RUN-20260807-4's final commit). Worktree clean at start
except this run directory. Environment unchanged (freeze identical to run-4).
Prompt capture: agent transcription, unverified, fifth consecutive run
(PROV-004/008/009/010 line).

## 1. The reopening, recorded

**The program was closed at RUN-20260807-4.** This run reopens it
deliberately, on owner direction, for exactly one purpose — the single
committed gate `v1.3.0-I12-decision-enforcement` recorded in STATUS
`committedGates` — and closes it again at the end. The close-out's own
reasoning anticipated this: the gate was made a *committed gate* rather than
a candidate precisely so that the program's closure could not silently
retire it. This is that gate being paid, not a continuation of open-ended
work. Nothing else reopens: A1 and A2 remain undecided by explicit
instruction, the eleven kernels remain seeded, and no promotion occurs.

## 2. The gate, as registered (not redesigned)

I12, hard invariant: `conclusion == conclusionFunction(world)` AND
`margin == abs(count(supportingRoots) − count(opposingRoots))`. Pass
condition already registered with numbers measured on both sides
(IND-20260807-3; reference reproductions in RUN-3 and RUN-4 logs): the
R1-inverting ablation caught by I12 on exactly **22,440** worlds, the
R5.2-inverting ablation on exactly **38,760**, with **no fixture involved**,
B5 recording **zero** I12 violations, and **no other number moving** —
including C11/C12's digests. A different caught-count means I12 is wrong,
not the measurement: stop and report.

## 3. Design decisions taken this run (registration-level, stated up front)

- **I12 emits at most one violation per world** (detail names whether
  conclusion, margin, or both diverged), so caught-counts equal world
  counts and the registered 22,440/38,760 are exact match targets.
- **The ablation phase contains no fixture comparison at all** — the two
  inversion evaluators run over the exhaustive stream through the checker
  only, which is what "no fixture involved" requires.
- **Baseline continuity metric preserved; I12 power reported beside it.**
  B1–B4's registered totals (634,440 / 26,880 / 26,208 / 189,720) are sums
  over I1–I11 and must not move; naively folding I12 into them would move
  them for every baseline whose conclusions differ from the reference's
  (all four do). v1.3.0 therefore reports baselines as the preserved
  I1–I11 total plus a separate `i12Violations` figure — new information
  beside the preserved metric, nothing hidden and nothing moved. I12's
  *power* is established by the two dedicated ablations at exact registered
  counts, not by the blunt B1–B4 instruments; the registration says all of
  this explicitly.
- **I12 is skipped where no receipt exists** (fail-closed and inadmissible
  worlds), like every receipt-referential check.

## 4. Plan of record

1. Register v1.3.0 (protocol + preregistration + sidecar; fixtures C01–C12
   unchanged, digests unchanged; v1.0.0–v1.2.0 untouched).
2. Implement I12 and the decision-ablation phase; permanent tests.
3. Full confirmatory re-run; exact-equality comparison including the two
   pinned digests; ablation pass condition verified.
4. FINAL-RECORD.md updated by **appendix**, v1.2.0 text preserved.
5. Packet; close; then rebuild `agent/kl-000-conformance` as a range
   cherry-pick covering every commit including this run's closing commits;
   rebind sidecars; test; record delivery state in a post-close addendum.
   Push nothing — publication is the owner's after review of the exact
   public text.
