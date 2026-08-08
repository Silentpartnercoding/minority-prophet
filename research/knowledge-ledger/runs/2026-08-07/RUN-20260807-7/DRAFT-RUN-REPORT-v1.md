# DRAFT RUN REPORT v1 — RUN-20260807-7

Small, bounded, the last of today: the two missing backlogs written, the
cause corrected on owner evidence, and the recurrence made mechanically
impossible on both sides.

## The defect, verified then repaired

`RESEARCH-BACKLOG-v1.json` was absent from RUN-5 and RUN-6 — never created,
never named in any of their files, unnoticed by the runs and by the
operator's packet verification alike (all figures verified against the tree
and git history before acting; every one matched). Both files now exist as
**labelled post-hoc reconstructions**: headers state they were completed by
this run after their runs closed, and that content reconstructed from
committed artifacts is a weaker source than live reasoning. RUN-5's carries
the I12 gate run's items (the enforcement asymmetry BL-029; VER-101 cleanup
BL-030). RUN-6's carries the three operator-identified items that existed
nowhere else — **SCH-001 elevated to rank 1** (the v0.1 schema sits under
all twelve kernels; every kernel's next step runs through the v0.2
migration), the **mapping pipeline** as KL-001's uncovered risk surface, and
the **ADV-001 overlap** at FC1's E3 wired to BL-002's prior-commitment
mechanism — plus the multi-writer remote. No closed record was reopened;
nothing backdated.

## The cause, corrected mid-run — and it changes the fix

The brief's "no natural trigger" account was speculation; **the owner
corrected it with evidence, against the owner's own briefs**: only RUN-1's
brief enumerated the packet's members; later briefs said "the full versioned
packet" — a concept — and output tracked instruction exactly once the
enumeration aged out of context (grep-verified here, with one refinement:
RUN-2/3's briefs also never named the backlog; those runs produced it from
fresh precedent). This is M24 — *concepts are not quantifiers* — one layer
up, in the instruction layer, the layer that actually caused the loss. The
speculated cause is preserved in the corrected files' `causeCorrection`
fields rather than silently replaced.

## The two-sided mechanical fix (M26)

1. **The close enforces the enumeration.** `tests/test_closing_packets.py`
   (now in the permanent suite, 81 total): any run directory containing
   `END-UTC.txt` must carry every required artifact, non-empty. Its
   `REQUIRED` list is the enumeration of record. This run's own close is the
   first it validates — run before the closing commit, deliberately.
2. **A requirement on operator briefs, not advice (BRF-101):** a brief that
   requires a packet enumerates its members or cites the enumeration of
   record by path. A brief naming only the concept is **defective, and the
   run receiving it says so before executing.**

## This run's own specimens, on the record

The opening commit briefly carried `PROMPT.txt` as an **empty placeholder**
— the defect class's smallest instance, in the run fixing the defect —
recorded in the capture note; the new test rejects exactly that class
(non-empty required). And per the brief's own trap: this close includes this
run's own backlog, validated by the new test rather than by intention.

## What did not move

KL-000 untouched (`adversarial-passed` at v1.3.0); PR #17 untouched at
`650f9ee`; all twelve kernel states unchanged; 81 repo + 88 KL-000 tests
green. The first-transaction gate remains **NOT REACHED**. The program is
**closed again, with no committed gate outstanding** — and for the first
time, its closes are checked by machine.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
