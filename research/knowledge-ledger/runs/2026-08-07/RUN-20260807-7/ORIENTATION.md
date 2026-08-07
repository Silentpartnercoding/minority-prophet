# ORIENTATION — RUN-20260807-7

Opened 2026-08-07T23:39:01Z on HEAD `9102cd9` (RUN-20260807-6's close).
Small, bounded, the last of today: complete two missing closing-packet
artifacts, add the mechanical prevention, close with a full packet of my
own — backlog included, enforced rather than remembered.

## The defect, verified before acting

`RESEARCH-BACKLOG-v1.json` across the program:

```
RUN-1  13,684 bytes     RUN-4  6,876 bytes
RUN-2   8,714 bytes     RUN-5  ABSENT -- never committed (0 commits touch the path)
RUN-3   6,180 bytes     RUN-6  ABSENT -- never committed
```

Exactly as the owner stated: not deleted, never created; both runs declared
clean final trees with a required packet artifact missing; the operator's
own verification of RUN-5's packet also missed it. The sizes show a habit
decaying once the program felt closed — and the omission is this agent's
own, twice, in the two runs most confident the work was done.

## Plan

1. Write both files, headed as post-hoc completions by RUN-20260807-7:
   why missing, and that content is **reconstructed from committed
   artifacts, a weaker source than live reasoning**, labelled as such.
   RUN-5's covers the I12 gate run; RUN-6's covers at least the three
   operator-identified items (the mapping pipeline as KL-001's uncovered
   risk surface; the ADV-001 overlap at FC1's E3; SCH-001 under all twelve
   kernels, elevated from passing mention). Honest short lists; no padding.
2. Mechanical prevention, in the I12 spirit: a permanent test that fails
   the suite if any **closed** run directory (one containing `END-UTC.txt`)
   lacks any required packet artifact. It would have caught both omissions
   at close time and will catch the next one, including this run's own.
3. Close with a full packet. If my own close omitted the backlog, the
   defect would be reproducing itself in the run that fixes it — the new
   test makes that a suite failure rather than an observation.

## Boundary

RUN-5's and RUN-6's closed records are not reopened, amended, or backdated;
PR #17 (`650f9ee`) untouched; nothing pushed.

## Correction, mid-run (owner) — the cause above is wrong

The "habit decaying / no natural trigger" account in this document's plan
(and in the brief it came from) was **speculation, and the owner corrected
it with evidence mid-run**: the cause is **instruction decay**. Verified by
grep before adopting: only RUN-1's brief names RESEARCH-BACKLOG (1
occurrence); every later brief — including RUN-2's and RUN-3's, a refinement
to the owner's own table — says only "the full versioned packet", a concept.
RUN-2/3 produced backlogs on the enumeration still fresh in context as
precedent; RUN-5/6, driven by concept-only briefs with the precedent aged
out, never attempted the artifact — it appears in none of their files
including their manifests. Output tracked instruction exactly.

This is M24 — "concepts are not quantifiers" — one layer up, in the
operator's briefs; the same run that wrote M24 was executing under an
instruction with the M24 defect. The fix is therefore **two-sided**: the
mechanical close check (side 1, as planned), and a **requirement on operator
briefs** (side 2, not advice): a brief that requires a packet enumerates its
members or cites the enumeration of record
(`tests/test_closing_packets.py::REQUIRED`); a brief naming only the concept
is defective, and a run receiving one says so before executing. The earlier
sections of this document are preserved unrewritten; everything downstream
of this correction (the backlogs' cause fields, the test's docstring, M26,
the constraints) carries the evidenced cause.
