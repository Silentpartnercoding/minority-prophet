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

**Confirmed in production while recording this finding.** The two missed forms
above appear literally in this document, as evidence. CI's public-boundary job
inspected them as newly added lines and **passed them** — while correctly
blocking a different line in this same file. The gap is not hypothetical; it is
demonstrated by the check's own output on the commit that documents it.

## Gap 2 — the term the owner named is not on the list

The rule carries a short list of internal-strategy phrases. It does not include
the internal tooling term the owner has explicitly said must never appear in
public — the term that had to be redacted from a run brief on 2026-08-07 before
publication. A sentence naming that toolbox was measured as **allowed**.

The phrases the rule *does* carry are deliberately not quoted here; see
`scripts/check_public_boundary.py`. Reproducing a blocklist inside a public
document publishes the vocabulary the list exists to keep out of public
documents — an earlier draft of this section did exactly that and CI blocked it,
which is the rule working correctly.

**Fix:** add the internal-tooling vocabulary to the rule. This needs an owner
call, because the blocklist is itself public and every addition names one more
thing worth hiding.

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
