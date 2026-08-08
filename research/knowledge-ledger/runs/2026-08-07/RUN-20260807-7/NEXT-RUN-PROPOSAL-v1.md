# NEXT-RUN-PROPOSAL v1 — after RUN-20260807-7

No committed gate exists; the owner decision list stands as at RUN-6
(PR #17 follow-up, KL-001 real gate, KL-011 v0.2 prereg, A1/A2, promotion),
now preceded by BL-035: audit the brief layer against BRF-101 before the
next run executes anything, and BL-033 (the SCH-001 v0.2 migration, the
highest-leverage open item) as the natural next bounded run. Any future
brief that requires "the full packet" without enumerating members or citing
tests/test_closing_packets.py::REQUIRED is defective per BRF-101, and the
run receiving it should say so before executing.
