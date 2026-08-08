# Methodology notes — RUN-20260808-2

## M29 — a finding that exists only in conversation is not recorded

The owner asked "did you log these findings to github". The answer was no. The
BL-044 result -- the answer to the program's sharpest open question -- existed
only in a working directory outside the repository and in an owner conversation.
`BL-044` appeared in eight files on the published branch, every one of them the
commission rather than the answer.

The same was true of three further findings discovered while monitoring:
duplicate registration history, two gaps in the public-boundary check, and an
M27 enforcement file written but never committed (recovered as empty, because it
had been created on a branch and never added).

**Rule.** A monitoring session produces findings, and monitoring is not a
recording mechanism. Anything discovered while watching a run is unrecorded until
it is in a run packet, however thoroughly it was explained to the owner at the
time.

## M30 — reading the artifact named "confirmed" instead of the one named "primary"

The monitor reported to the owner that LIN-000 had reproduced both digests **on
the pre-declared reading, first attempt, with no sweep.** That was false, and it
inverted the headline: both pre-declared readings missed, and the matches were
found by sweeping 96 and 72 enumerated readings.

`out/confirmed.txt` was read and its MATCH lines relayed. `out/primary.txt` had
appeared in the same watch notification and was never opened -- it holds both
misses. The stronger claim was asserted from the artifact that happened to be
read first.

This is the same defect as the LAN-mirror misreading (RUN-20260808-1) and the
proxy-versus-property errors recorded throughout the KL-000 program. It is
recorded here because a run record that captures only the implementer's errors
and not the monitor's is the flattering account this program exists to refuse.

## Screening defects hit while monitoring, all mine

Three false alarms, all from matching a cheap proxy over unsuitable data:

- A `gh pr checks` screen used `awk '{print $2}'`; the first field contains a
  space, so it read the Python version as the CI status and would have reported
  every check green.
- A withheld-value screen used BSD `sed` for comma formatting, which failed
  silently, so only bare digits were compared -- the exact LEAK-101 defect.
- The LIN-000 watcher matched the substring `contaminat` inside a 2.5 MB word
  list and reported a contamination alert on a dictionary entry.

All three rewritten: verdicts computed in Python, source and documentation files
only, size-capped, phrase-level patterns rather than substrings.
