# DRI-2 v2 — preregistration

**Status: FROZEN, 2026-09-15. NOT RUN.** Frozen before any v2 world is generated or
scored.

DRI-2 v2 is the final version of DRI-2. It uses the frozen DRI-2 v1 protocol and
implementation **byte for byte**, with exactly the changes listed below. Every
section of `experiments/dri2/PREREGISTRATION.md` applies except where this document
changes it. That file and the shared code are pinned here by SHA-256, as frozen at
v1 protocol commit `574a6a626845215244f03fa85a5cd689f0ed350c`:

| File | SHA-256 |
|---|---|
| `experiments/dri2/PREREGISTRATION.md` | `8d05327d3505d943aa7947aacefcd656be0d59be5f6b1d881d8ec2fc0cc2a94e` |
| `experiments/dri2/world.py` | `30327cc6a46542f1dba52cbaf4faf5fd2386510cd5b9bcd7d5b5078c4db24161` |
| `experiments/dri2/arms.py` | `39bee408c92072ef0b55bfe06d18070dbae843621101b0063ebb4a0d1d47e7a8` |
| `experiments/dri2/stats.py` | `6f65060ff5cd366e6ca2a65fe85395210212e32f2abc3dfb0f72e7e3f06c9257` |
| `experiments/dri2/scoring.py` | `e9e9275d2e8b9f22d844b4e9e62e2e9b67f46e7a83a67e77d9390570b67a1be1` |

## Why a second version

DRI-2 v1 (`results/dri2-v1/`) was rejected under its registered criterion, and that
verdict stands. Its speed checks were misplaced: speed was carried in from a
different benchmark and is not a criterion for DRI-2. All 44 non-speed checks passed.
v1 also let an arm hand hard decisions to a scripted human who always answered
correctly, so escalating borrowed the right answer.

v2 asks the intended question cleanly: can the method count evidence without a
human, when it has to decide on its own when to settle, when to look and when to
abstain?

## Changes from v1

1. **No human.** An `escalate` action is an **abstention**. No answer is supplied.
   Decisions within a world do not use each other's answers, so nothing computed
   changes except the clock. Output fields keep the v1 names, read as follows:
   - `humanCalls` means abstentions;
   - `excessHumanCalls` means unneeded abstentions;
   - `required_handover` means a required abstention;
   - `incorrect_stall` means an unneeded abstention;
   - `lookedBeforeAsking` means looked before abstaining.
2. **Clock.** An abstention costs 1 virtual ms like any other action
   (`wrong_time_escalation_cost_ms: 0`), and a probe still costs 1,000 ms. **Time is
   measured and reported but is not a success criterion.** Because abstaining is
   cheap on this clock, time mostly measures the cost of looking, and the write-up
   says so.
3. **Success criterion.** v1's section 10 with the speed checks removed:
   - **Structured families** (single domain, joint domain, separate control with
     shared origin), each: the method crosses significantly more often than agent
     headcount and all four fixed cuts, and no comparison arm crosses significantly
     more often than it. Tested with exact McNemar and Holm correction at a
     family-wise α of 0.05.
   - **Genuinely independent family:** crossing non-inferior to every comparison
     arm, with the lower 95% bound of the paired difference at least −0.02.
   - **Reproducibility:** two complete executions produce identical semantic
     results.

   Supported only if all hold. Unneeded abstentions are reported for every arm as a
   secondary measure. They are not a criterion.
4. **Fresh worlds.** Confirmatory salt `minority-prophet-dri2-v2-confirmatory`. No
   v1 world is reused, and no v2 world has been generated.

## Disclosure

This version was specified after the v1 result was known. That result showed the
method crossing as often as determined-or-escalate, and far more often than
headcount or any fixed cut, with far fewer unneeded escalations. The criterion is
v1's registered criterion minus the speed checks. Nothing was added, and the method
code is unchanged. What v2 adds is fresh worlds and the removal of the human. It is
not a blind test of a newly conceived criterion.

DRI-2 v2 is authored in the same control domain as the method, has no held-back
worlds, and makes no real-world or authority claim, exactly as v1.
