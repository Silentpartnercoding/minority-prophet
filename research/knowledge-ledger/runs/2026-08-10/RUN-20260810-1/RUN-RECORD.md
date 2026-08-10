# RUN-20260810-1 — internal adversarial review of the four-repository stack

> **NOT AN INDEPENDENT AUDIT.** Performed by an agent directed by the repository
> owner. Under `AGENTS.md` rule 2 that is one control domain; under rule 3 the
> result is **internal replication, not independent validation**. Agreement with
> the repositories' own tests is not evidence of correctness.

## Why it was internal

An external reviewer's tooling refused the audit brief. The brief was legitimate —
scoped to local clones, no production probing, no secrets, private disclosure —
but it opened with attack objectives and never stated that the repositories were
the owner's or that testing was permitted. Read cold, that is an unattributed
offensive mandate against named GitHub organizations.

Two things followed. An authorization and safe-harbour section was added to
`SECURITY.md` in all four repositories, so a future external reviewer can confirm
from the repositories themselves that testing is invited — narrow on purpose:
your own copy, no systems, no secrets, no change to the LICENSE. And this review
was run internally and labelled as such rather than described as the independent
audit it is not.

## Findings, both fixed

**ECI-01 — assurance weakness.** A package whose verifier checks only that its
input file is non-empty, never reading the verdict it exists to verify, passes all
four Epistemic CI checks. Afterwards, flipping `PASS` to `FAIL` in both the source
fixture and the generated result leaves both verifiers exiting 0. No documented
claim was falsified; the mechanical defences are sound and were tested (empty
mutation lists rejected, no-op mutations caught). The gap was that `status: pass`
carried no qualifier while each check's own reason correctly said "every
**declared** mutation".

Fixed upstream: every result now carries an `assurance_bound` object stating the
declared count and what the run does not establish, machine-readable so a badge or
a summary cannot drop it. Reported rather than enforced, because deciding whether
a declared mutation set is representative requires knowing which defects matter —
the thing under study.

**GATE-01 — documentation gap.** `attest.origin` was documented as "root id this
claim descends from" and as collapsing claims "into that family". Every executable
use of `origin` classifies freshness policy; the aggregator never reads it.
Collapse works only through `derived_from`. Fifty claims sharing one origin count
as fifty roots and convert a correctly-escalating tie into a proceed — the
manufactured independence `SECURITY.md` names as central.

Fixed upstream by correcting the documentation, not the behaviour: establishing
that one controller yields one root is the verifier's job, and implementing
origin-based collapse would change semantics and needs its own registration. Two
regression tests pin the contract in both directions.

## No counterexample within the declared search

- Deterministic deny never overridden: 486 evidence shapes enumerated, zero escapes.
- T2 copy invariance holds: fifty properly derived copies leave a tie escalating.
- Wrong-subject evidence escalates rather than proceeding.
- Epistemic CI's advisor security tests do run, in a dedicated CI job.

## Two reviewer errors, recorded rather than deleted

The review reported a counterexample to T2 built on a top-level `parent` key that
does not exist in the envelope contract; the real field is `attest.derived_from`.
**T2 holds.** And the first Gate pass ran entirely under `TrustAllVerifier`
without registering that its own docstring says it provides no security.

Both were caught by reading source, neither by re-running. That is the same
pattern this programme keeps finding: the tooling catches mechanical error and is
blind to design error.

## What was not done

Border, the cross-repository composition harness, KL-011 readiness and the
claim/adoption audit. Silence about those is silence, not a clean result. The
composition harness is the stated gap and is tested separately.

## Artifacts

`audit/` — executive summary, `AUDIT-STATE.json`, both findings, and a standalone
reproduction for GATE-01.
