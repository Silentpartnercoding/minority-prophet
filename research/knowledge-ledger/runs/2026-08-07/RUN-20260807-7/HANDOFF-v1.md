# HANDOFF v1 — RUN-20260807-7

Small run, fully delivered. Base a7a3f81^ (RUN-6 close 9102cd9), commits:
a7a3f81 (open + verification), 03f7524 (both backlogs written), cdb79bb
(cause correction adopted everywhere + enforcement test + prompt
transcriptions), then this packet. Tree clean; 81 repo + 88 KL-000 tests
green; PR #17 untouched at 650f9ee; no kernel state changed.

What is now mechanically true: a run directory containing END-UTC.txt must
carry every artifact in tests/test_closing_packets.py::REQUIRED, non-empty,
or the suite fails. That list is the enumeration of record for the phrase
"the full versioned packet", and BRF-101 stands: a brief naming the concept
without the members (or the citation) is defective, and the run receiving
it says so before executing.

Yours: whether RUN-6/RUN-7 commits join PR #17 or a follow-up PR; BL-035
(brief-layer audit); BL-033 (SCH-001 migration run, highest leverage);
KL-001 real gate; KL-011 v0.2 prereg; A1/A2; promotion. Nothing here is
pushed.

The program is closed again. No committed gate outstanding; the close you
are reading was validated by the new check before it was committed.
