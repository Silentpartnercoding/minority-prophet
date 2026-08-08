# BL-035 — audit of the operator-brief layer against BRF-101

Executed first, before any other work of RUN-20260807-8, as authorised.
Scope: every operator brief captured in the run records
(`RUN-20260807-1..8/inputs/PROMPT*.txt`), including this run's own brief.
BRF-101's requirement: **a brief that requires a closing packet enumerates
its members, or cites the enumeration of record
(`tests/test_closing_packets.py::REQUIRED`) by path.** A brief naming only
the concept is defective. Briefs older than BRF-101 (established
RUN-20260807-7) are judged retroactively for the record — a defect finding,
not a fault finding.

## Verdicts

| Brief | Packet instruction (verbatim core) | Verdict | Loss caused |
|---|---|---|---|
| RUN-1 `PROMPT.txt` (operator-file, master-loop) | "create and commit this versioned closing packet" followed by a **named member list with content requirements** (`DRAFT-RUN-REPORT-vN.md`, `CONSTRAINTS-vN.json`, `RESEARCH-BACKLOG-vN.json`, `KERNEL-STATUS-SNAPSHOT-vN.json`, `NEXT-RUN-PROPOSAL-vN.md`, `HANDOFF-vN.md`) | **conforming** (predates BRF-101; meets it) | none |
| RUN-1 `PROMPT-ADDENDUM.txt` | no packet requirement | n/a | — |
| RUN-2 | "versioned closing packet" (discipline preamble); "Close the run with the full versioned packet **as before**" | **defective (retroactive)** — concept plus a precedent pointer; "as before" resolves only through context, which is exactly the mechanism that later decayed | none — RUN-1's enumeration still fresh in context |
| RUN-3 | "Same discipline: run directory, provenance, versioned closing packet…" — **no closing enumeration anywhere** | **defective (retroactive)** | none — precedent still effective |
| RUN-4 | "Close with the full versioned packet." | **defective (retroactive)** | none — precedent still effective |
| RUN-5 | "Close with the full versioned packet and state plainly whether the program is closed again." | **defective (retroactive)** | **RESEARCH-BACKLOG-v1.json omitted** (PKT-101) |
| RUN-6 | "Close with the full versioned packet and state whether the program is closed again…" | **defective (retroactive)** | **RESEARCH-BACKLOG-v1.json omitted** (PKT-101) |
| RUN-7 | "Close with your own full packet, **backlog included**." | **defective as written** — names exactly one member (the previously lost one), enumerates nothing else, cites nothing; predates BRF-101 by hours (the correction that created BRF-101 arrived mid-run) | none — the run built the enforcement that now catches the class |
| RUN-7 `PROMPT-CORRECTION.txt` | no packet requirement; **establishes BRF-101** | n/a (source of the rule) | — |
| RUN-8 (this brief) | "Write the full closing packet. Its required members are **exactly, by name**: [7 members] … and `tests/test_closing_packets.py::REQUIRED` **is the authority if this list and that list ever disagree**" | **conforming, with a defect noted below** | none (the citation clause governs) |

## This brief's own audit, as instructed

The brief **passes BRF-101** — it both enumerates and cites the enumeration
of record with an explicit precedence rule. And it carries a defect worth
stating plainly: its inline list says "exactly, by name" while naming **7 of
REQUIRED's 15 members**, omitting `START-UTC.txt`, `git-status-before.txt`,
`git-status-after.txt`, `inputs/PROMPT.txt`, `METHODOLOGY-NOTES.md`,
`run-manifest.json`, `environment-lock.txt`, and `pip-freeze.txt`. The two
lists *do* disagree, so the brief's own precedence rule activates on first
use, and REQUIRED governs this run's close. **Without the citation-and-
precedence clause, this brief would be defective under BRF-101 in the exact
PKT-101 pattern — an authoritative-sounding partial enumeration is more
dangerous than a bare concept, because it looks complete.** The clause is
what saves it, and the clause is the part of BRF-101 that matters: the
enumeration of record is one place, cited, not re-typed.

## Findings

1. **7 of 9 packet-requiring briefs were defective under BRF-101** (all
   retroactive except none — every defective brief predates the rule).
   Defect tracked loss exactly as BRF-101 predicts: zero losses while an
   enumeration or fresh precedent was in context (RUN-2/3/4), two losses
   once neither was (RUN-5/6), zero losses after enforcement existed
   (RUN-7).
2. **Re-typed enumerations drift** (this brief's 7-vs-15): the citation
   form of BRF-101 compliance is strictly safer than the enumeration form.
   Recorded as a recommendation on the standing requirement: briefs SHOULD
   cite `tests/test_closing_packets.py::REQUIRED` rather than re-type the
   list, and MUST include the precedence rule if they re-type.
3. The audit itself is cheap (one grep pass per brief) and is now part of
   the run-open discipline recorded in the handoff.
