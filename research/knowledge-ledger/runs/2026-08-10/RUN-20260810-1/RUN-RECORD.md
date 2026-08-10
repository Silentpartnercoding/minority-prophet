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

## SYS-01 — the stated gap, tested, and it failed

The composition harness was the review's own stated gap, and building it produced
the most serious finding of the run.

**Invariant 1: an allow executes the exact bound action at most once.** It did
not. `RuntimeController.apply` executed the effect and recorded the ledger entry
*afterwards*, so anything failing in between left no record and a retrying caller
executed again:

    transport fails after the effect lands    3 retries -> 3 transfers
    adapter returns an invalid receipt        3 retries -> 3 transfers

The second is the sharper one: validation rejecting a malformed receipt caused the
effect to repeat, so a defensive check made the failure worse.

The documented caveat did not cover it. It says production callers must supply a
durable transactional ledger *"with the same semantics"* — but the semantics were
the defect. No storage backend can record an execution the code does not mention
until after it has happened. The order is the guarantee, not the durability.

Fixed in gate#15: intent is recorded before the effect, and an unresolved entry on
a later attempt fails closed with a reconcile instruction rather than executing
again. Four regression tests, three of which fail against the previous ordering —
verified by reverting only the source file and leaving the tests in place, after a
first attempt at that check stashed both at once and proved nothing.

Harness: 6 of 6 invariant scenarios hold, previously 4 of 6.
`audit/system-integration/harness.py`.

**This is why the gap mattered.** Every finding before it was a documentation or
reporting weakness with no runtime consequence. The one that could double a
transfer was in the seam, which is exactly where nothing had been looked.

## Invariants 2–11, and Border

Run after SYS-01, because one broken invariant out of eleven is not a reason to
assume the other ten.

**Invariants 2–11: ten hold, zero violations, one documented gap.** Deny executes
zero times even with 100 supporting roots. Escalate executes zero times. Evidence
past its TTL, or carrying no `observed_at` under a TTL policy, escalates rather
than proceeding. Evidence bound to another subject escalates. Target substitution
under a reused idempotency key raises. Twenty claims with no attest block lose to
one opposing root. A `prepare()` failure propagates with zero effects. The
recorded result distinguishes authorization from evidence from enforcement via
`route`. The one gap is INV-9, which is GATE-01 already recorded: `origin` is not
a collapse key, and supplying independence is the verifier's job.

So the seam failure was specific to the exactly-once controller rather than
general to the composition.

**Border: 9 of 9 on DSSE/admission binding, 8 of 8 on subject-link.** Substituted
action digests, flipped decision points, extended expiries, swapped policy
digests, renamed subjects, stripped signatures, unknown key ids and foreign-key
forgeries are all rejected. Revoked, expired, wrong-audience and badly-signed
subject links are rejected; two claims from one provider do not become two
providers; different pairwise subjects do not merge.

Worth recording: on the accepting control, `establishes_provider_independence` is
**False**. Two distinct providers satisfy a count requirement and Border still
declines to call that independence — the opposite of the failure mode this
programme names as central.

**A methodological correction inside this pass.** The first Border suite ran
without a valid baseline: the envelope failed with "unknown admission statement
type", so all three tamper tests were rejected for a schema reason and would have
been recorded as security passes. Repeated with a verified baseline. A rejection
that happens for the wrong reason is not a control.

`audit/system-integration/harness_v2.py`, `audit/border/BORDER-RESULTS.md`.

## What is still not done

KL-011 readiness, the claim/adoption audit, Border's delegated-authority scope and
OpenID gateway paths, and replay across a durable store. Silence about those is
silence, not a clean result.

## Artifacts

`audit/` — executive summary, `AUDIT-STATE.json`, both findings, and a standalone
reproduction for GATE-01.
