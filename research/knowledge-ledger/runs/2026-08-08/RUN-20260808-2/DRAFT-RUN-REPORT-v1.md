# RUN-20260808-2 — draft run report

A logging run, opened because the answer to "did you log these findings to
github" was no.

## What was unrecorded

**BL-044's result** — the answer to the program's sharpest open question — lived
only in a working directory outside the repository and in an owner conversation.
`BL-044` appeared in eight files on the published branch; every one was the
commission, none the answer.

Three more, all found while monitoring: duplicate registration history, two gaps
in the public-boundary check, and an M27 enforcement file written on a branch,
never added, and recovered as zero bytes.

## Recorded here

- **`FINDING-BL044.md`** — the F11 repair is necessary but not sufficient. Both
  pre-declared readings missed; matches were found by sweeping 96 enumeration
  orders and 72 draw-schedule readings, one correct each. Recorded as sweep
  results, per the implementer's own pre-registered protocol.
- **`FINDING-CHAIN-101.md`** — the registrations are intact (4/4 verified by
  content against their pins); the check tests a proxy and main carries duplicate
  registration history, introduced by this program's own delivery, not by Codex.
- **`FINDING-PBC-101.md`** — the boundary check misses 11 of 37 real leaked
  lines, and does not block the one internal term the owner named.
- **`LIVE-COMMISSIONS.json`** — M27's machine-readable half, with its checker
  recorded as unbuilt rather than described as if it existed.
- **`lineage/results/independent/IND-LIN000-*`** — the implementer's report,
  frozen decisions, and both phase outputs, imported verbatim.

## What LIN-000 established beyond the F11 answer

Theorem 1 and Lemma 1 are no longer shadow-tested: zero violations across both
phases including 975,782 randomized rewirings, negative controls firing
(cross-side rewiring changed the verdict 164,456 times), both ablations caught.

The M27 leak did less damage than feared — the implementer declined to consult
the public repository, so their counters were computed rather than recognised.
Protection by their choice, not by our control; the discipline still stands.

Verified before accepting the report: stream byte-lengths 1,189,512 and 4,250,451
appear nowhere in the commission package and match the reference exactly. They
cannot be produced without generating the stream.

## Repaired: nothing

Four findings, four backlog items, zero repairs. BL-049, BL-050, BL-048 and
BL-051 are the repairs this run declined to fold into a logging run.

## Recorded against the monitor

The monitor told the owner LIN-000 had matched on the pre-declared reading, first
attempt, no sweep. False, and it inverted the finding: `out/confirmed.txt` was
read, `out/primary.txt` — in the same notification, holding both misses — was
not. Corrected before anything was committed, but stated as fact first. M30.
