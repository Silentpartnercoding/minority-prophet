# Methodology notes — RUN-20260808-1

## M27 — a published run report can burn a future commission's blindness

Assembling BL-044's package, the withheld-counter screen was run not only against
the package but against every file on `github/main`. Twelve of LIN-000's fourteen
outcome counters were already public, published hours earlier by the delivery of
RUN-6..10 (PR #24) inside RUN-10's draft run report. Two were public before that.

Nobody checked at publication time whether publishing a run report would
compromise an experiment the same report proposes. The proposal (BL-044) and the
numbers that make it falsifiable travelled in the same commit.

**Rule.** Before publishing a run record, screen it against the withheld set of
every experiment the record proposes or leaves open. Publication is a leak
surface, and the leak is forward in time.

The counter-equality pass condition would have been unfalsifiable-by-tuning. The
repair — pinning a world-stream digest instead — is the C11 argument reused: a
count gives no path to a SHA-256 over the stream that produced it. The primitive
is not new; the independent implementer invented `worldStreamHash` unprompted in
IND-20260807-1, and this run adopts it as a pass condition.

## M28 — a rule discovered outside the run system is still unowned until recorded

XRP-101 was found by a direct owner question after RUN-10 closed, and existed
only as merged pull requests in two product repositories. Landing a repair is not
the same as recording a finding: the repair fixes one instance, the finding is
what generalises. BL-046 exists because the audit that produced XRP-101 covered
three of six shared quantities.

## Screening bugs hit again in this run

Two, both caught before they mattered, both the same shape as prior defects:

- A shell screen used `awk '{print $2}'` on `gh pr checks` output, whose first
  field contains a space, so it reported the Python version where the status
  should be and would have shown every check as passing.
- A comma-formatting screen used BSD `sed`, which failed silently, so only bare
  digits were compared — the exact LEAK-101 defect. Rewritten in Python.

The standing lesson holds: screens that munge text in shell are not evidence.
