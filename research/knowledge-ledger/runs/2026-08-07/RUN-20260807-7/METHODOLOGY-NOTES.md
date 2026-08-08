# Methodology notes — RUN-20260807-7

M1–M25 in force. One addition, written twice because its cause was corrected
mid-run.

## M26 — A packet is its members: the close enforces the enumeration, and a brief that requires a packet enumerates it

**The defect:** RESEARCH-BACKLOG-v1.json absent from two consecutive closed
runs, unnoticed by the runs and by the operator's own packet verification.

**The cause, evidenced (owner correction, replacing this run's briefed
"no natural trigger" speculation):** instruction decay. Only RUN-1's brief
enumerated the packet's members; every later brief said "the full versioned
packet" — a concept. RUN-2/3 produced complete packets from the enumeration
still fresh in context as precedent; by RUN-5 the precedent had aged out,
and the concept-only instruction produced exactly what it named: a packet
minus the member nobody named. The artifact was never attempted — it appears
nowhere in either run's files. Output tracked instruction exactly. This is
M24 — *concepts are not quantifiers* — one layer up, in the instructions:
the same run that wrote M24 after its own E4 failure was executing under a
brief carrying the identical defect.

**The fix is two-sided, both mechanical:**

1. **The close enforces the enumeration.**
   `tests/test_closing_packets.py` fails the suite if any run directory
   containing `END-UTC.txt` lacks any required packet artifact, or ships one
   empty (an empty placeholder is an absent file wearing a filename — this
   run briefly committed one and is the first specimen). The `REQUIRED` list
   in that file is the enumeration of record. In the I12 spirit:
   enforcement, not prose — this paragraph could decay too; the test cannot.
2. **A requirement on operator briefs, not advice:** a brief that requires a
   packet enumerates its members, or cites the enumeration of record by path
   (`tests/test_closing_packets.py::REQUIRED`). A brief that names only the
   concept is **defective**, and a run receiving one says so before
   executing — the same standing a defective registration has. The layer
   that caused the loss is the layer that must carry the check.

The general form, now seen at three layers in one day: an expectation (E4),
a specification (G2's unregistered receipt object), and an instruction (the
briefs) each named a concept where members belonged, and each failed exactly
at the members nobody named. Enumerate, or lose whatever the concept was
quietly holding.
