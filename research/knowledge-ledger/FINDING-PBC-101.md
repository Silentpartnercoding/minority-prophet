# PBC-101 — two gaps in the public-boundary check

Recorded by RUN-20260808-2 against `scripts/check_public_boundary.py`, added by
PR #26. Tested rather than reviewed: every claim below is a measured result.

The check is well-designed and correctly scoped. It inspects **only newly added
lines**, so frozen historical records — which still contain operator paths and
must not be rewritten, for the reasons in `FINDING-CHAIN-101.md` — are left
alone. That is the right call and it is the same conclusion RUN-20260808-1
reached the expensive way.

Two gaps, both narrow, both in the blocking rules rather than the design.

## Gap 1 — the local-path rule misses a third of real occurrences

The rule requires the path to be preceded by start-of-line, whitespace, a quote,
or `(`. Replayed against the 37 real leaked lines that RUN-20260808-1 removed:

    would block:  26
    would MISS:   11

Missed forms, both of which are the *most common* shapes in the run records:

    python_executable=/Users/james/Development/.mp-runner-venv/bin/python
    origin  james@100.101.32.77:/Users/james/.../minority-prophet

An `=` or a `:` before the path defeats it. Every per-run `environment-lock.txt`
writes the interpreter path in the first form, so the highest-frequency instance
in the repository is the one that slips through.

**Fix:** allow any non-path delimiter before the path, not an enumerated set.

## Gap 2 — the term the owner named is not on the list

The "internal strategy wording" rule blocks phrases such as *shadow lane*,
*master plan*, *our moat*. It does not block **`lockpick`** — the one internal
term the owner has explicitly said must never appear in public, and the term
that had to be redacted from a run brief on 2026-08-07 before publication.

Measured:

    "cross-reference the trust-lockpick toolbox before closing"  ->  allowed

**Fix:** add the internal-tooling vocabulary to the rule.

## Not a gap — the class it cannot cover

The check catches **secrets** leaving. It cannot catch **answers** leaving.

RUN-20260808-1's other leak was publishing twelve outcome counters that retired a
live commission's pass condition. Those are ordinary integers in a results table;
no pattern distinguishes them from any other figure. Confirmed: zero hits against
that publication.

That needs a different mechanism — comparing additions against the withheld set
of every live commission — which is `LIVE-COMMISSIONS.json` plus the unbuilt
checker recorded as **BL-048**. It is not a defect in PR #26 and should not be
folded into it.

## Disposition

Both gaps recorded as **BL-050**, unrepaired. They belong to the author of PR #26
or to a deliberate tooling run, not to a logging run; and the second requires the
owner's judgement about which internal vocabulary belongs in a public blocklist,
since the blocklist itself is public and names what it protects.
