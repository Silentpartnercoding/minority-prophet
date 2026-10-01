# AUDIT evidence-root counting Internet-Draft package

This directory contains the submission-ready source and generated renderings
for `draft-he-audit-evidence-root-counting-00`.

The package is **not submitted**, is not an adopted working-group document, and
does not claim endorsement by the people or projects cited in it.

## Build

From the repository root:

```text
make ietf-draft
```

That command uses the repository's ignored `.venv`, installs the pinned
`xml2rfc` version, and regenerates the `.txt` and `.html` files from the XML
source. The Makefile selects Python 3.12 or 3.11 when it creates that
environment, matching the repository's Python requirement.

## Check

```text
make ietf-check
```

The check rebuilds both formats, requires a clean regeneration, validates the
package contract, and scans for unresolved placeholders. The repository-wide
handoff check remains:

```text
make verify
```

The IETF Tools team's submission-mode preflight can also be run without adding
a project dependency:

```text
npx --yes @ietf-tools/idnits --mode submission --no-color --no-progress --output simple papers/ietf/draft-he-audit-evidence-root-counting-00.xml
```

## Before submission

1. Review the rendered text and HTML, including author contact information.
2. Confirm that every cited Internet-Draft revision remains current.
3. Re-run the frozen completeness and root-counting fixture at the cited
   revision.
4. Obtain scoped technical review without describing a replay as an independent
   implementation.
5. Reconcile any external contact in the private relationship ledger.
6. Upload through the IETF submission tool before the IETF 127 cutoff:
   **November 2, 2026 at 23:59 UTC**.

Submission and mailing-list outreach are intentionally outside this package.
