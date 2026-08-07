# Methodology notes — RUN-20260807-1

Practices this run adopted that are not yet in `RESEARCH-METHOD.md`. Each is
proposed for the program, with the reasoning that produced it. They are recorded
here rather than applied to `RESEARCH-METHOD.md` directly, because amending the
shared method document is its own PR.

## M1 — A preregistration is never edited after registration; commit binding lives in a sidecar

**Practice.** `preregistration.json` carries `"protocolCommit": null`
permanently. The introducing commit is recorded afterwards in a sibling
`PROTOCOL-COMMIT.txt`.

**Why.** A preregistration's whole value is that it existed, unchanged, before
the result was known. Editing it afterwards to insert its own commit hash means
modifying the artifact whose immutability *is* the claim. The amended file then
hashes differently from the registered one, and a reviewer must trust that only
the hash field changed. That is weaker precisely where it matters: it makes
"registered first" unverifiable by inspection.

The sidecar inverts the dependency. The registered document stays byte-frozen,
and the binding becomes a checkable equality between two independent sources:

```bash
git log -1 --format=%H -- <path>/preregistration.json   # last commit to touch it
cat <path>/PROTOCOL-COMMIT.txt                          # the commit we claim
```

These stay equal for exactly as long as the file is never edited again, so the
equality *is* the immutability claim. If they disagree, the registration is
void. A mutable `protocolCommit` field cannot fail that way, because there is
nothing left to disagree with — which is another way of saying it was never
evidence.

**A caveat worth carrying.** The obvious formulation of this check —
`git log --diff-filter=A`, "the commit that added the file" — is wrong whenever
registration *modifies* a pre-existing seed file rather than creating a new one.
It then returns the seed commit and mismatches the sidecar. KL-000 hit exactly
this: the check reported `2068c69` against a sidecar of `c977347`. Use
`git log -1`, the last commit to touch the file, which is the quantity the
immutability claim is actually about.

**Cost.** `"protocolCommit": null` reads as an incomplete field to anyone who
has not been told otherwise, including automated completeness checks. The
decision must therefore be **declared** in the protocol, not merely practised;
`scripts/audit_preregistrations.py` would otherwise report it as a gap.
Undeclared, a deliberate null is indistinguishable from a forgotten one.

**Proposed for.** `RESEARCH-METHOD.md` field 11, and the v0.2 preregistration
schema.

## M2 — Amendments to a registered protocol are logged in the protocol, never applied silently

**Practice.** `PROTOCOL.md` carries an amendment log recording what changed,
when relative to confirmatory execution, and whether experimental content was
affected.

**Why.** Some post-registration edits are legitimate — clarifying a decision,
declaring an undeclared practice — and some are retrospective protocol changes
that invalidate a result. The two are indistinguishable in a diff unless the
document says which it is and when it happened. A protocol whose history is
reconstructible only from git is one `--amend` away from unfalsifiable.

The load-bearing column is "experimental content affected", and the load-bearing
timestamp is *relative to confirmatory execution*, not wall-clock.

**Proposed for.** `RESEARCH-METHOD.md` "Required preregistration".

## M3 — Test power is a preregistered invalidation condition, not a review-time judgement

**Practice.** KL-000 preregisters four ablated baselines (B1–B4) that the
invariant suite **must** catch. If any passes, the run is `incomplete` — not
`passed` — regardless of how cleanly the real evaluator did.

**Why.** A conformance suite that passes everything may be measuring nothing,
and the failure is silent and flattering: a vacuous suite and a correct
implementation produce identical output. Nothing in a clean result distinguishes
"the evaluator is right" from "the checker cannot tell". Making the ablations an
*invalidation condition* rather than a sanity check means the run cannot report
success while the question is open.

The baselines must run through the **same checker code path** as the real
evaluator. A separate harness written to catch them would only prove that the
harness catches them.

**Observed value.** B1 was caught by I1 and I10, B2 and B3 by I2, B4 by I1 —
each by the invariant its ablation targets, which also confirms the invariants
are measuring the properties they are named for rather than passing for
incidental reasons.

**Proposed for.** `RESEARCH-METHOD.md` "Controls required everywhere".

## M4 — Red-team results are split into defences and pinned limits, and limits are asserted

**Practice.** `tests/test_kl000_adversarial.py` splits into `test_defends_*` and
`test_limit_*`. A `test_limit_*` asserts that the weakness **is present**.

**Why.** An attack the system cannot resist has two honest destinations: fix it,
or record it. Recording it in prose alone means it can be silently lost — a
later change might close or widen the gap with nothing failing. Asserting the
limit makes its status a tested property: if someone fixes A05b, the test breaks
and forces a deliberate protocol change instead of an undocumented improvement.
It also stops a limitation from quietly decaying into a claim.

The naming matters. A reader scanning green checkmarks must not read
`test_limit_a05b_an_under_declared_search_space_is_undetectable` as reassurance.
Seven of this suite's tests pass **because the system is vulnerable**.

**Proposed for.** `RESEARCH-METHOD.md` red-team requirements.

## M5 — Conflicting environment observations are a state-change hypothesis first

**Practice.** When a measurement contradicts an earlier one, treat "the world
changed" as the leading hypothesis until ruled out, rather than "I mismeasured".

**Why.** This run got it backwards once (constraint `PROV-006`) and nearly
erased a real event. The asymmetry is what makes it dangerous: concluding
self-error when the state actually changed *discards evidence* and looks
resolved afterwards, because the corrected reading agrees with reality. The
opposite error is loud and self-limiting.

**Proposed for.** run-provenance guidance; timestamp environment observations so
the two hypotheses are separable after the fact.

## M6 — Preservation applies to results at least as strictly as to notes; committed artifacts are corrected, never amended

**Practice.** A committed artifact that needs correcting gets a **follow-up
commit** and, where the artifact is a result document, a retained copy of the
superseded version under `results/superseded/` with its digest. Never
`git commit --amend`, never a rewrite, regardless of whether anything has been
pushed.

**Why.** This run got it wrong once, and the way it got it wrong is the
instructive part. It had already reasoned correctly about `ORIENTATION.md`:
preserve the original, append the correction, because "rewriting it would
destroy the evidence that a correction was needed." Three commits later it
amended a **results** commit away — applying the weaker standard to the stronger
artifact, and doing so without noticing the inconsistency, because "it is local
and unpushed" felt like a sufficient licence.

It is not, for two reasons.

*The record is the deliverable.* An operator had already reviewed `3ac618f` and
reported on it. A reviewed commit that no longer exists makes the review
unanchored: the reviewer's findings refer to an object the log no longer
contains.

*The failure is self-concealing.* After an amend, the history is internally
consistent and carries no marker that anything was corrected. A reconstruction
cannot distinguish "was right the first time" from "was quietly fixed". This is
the same shape as `PROV-004` (a transcription digested as the original) and
`PROV-005` (a cache measured as the remote): a derived artifact standing in for
its source, locally unfalsifiable.

There is a sharper irony worth keeping. Amending is exactly the operation that
makes a protocol's amendment log unfalsifiable — and **M2, which exists to
prevent that, was written by this same run two commits earlier.** Articulating a
principle is not the same as having internalised it, and the gap between the two
is invisible from the inside. That is an argument for mechanical enforcement
rather than for trying harder.

**Cost.** The history is longer and shows its own mistakes. That is the point:
a research log that only contains what turned out to be right is not a log, it
is a summary written afterwards.

**Proposed for.** `RESEARCH-METHOD.md` "Evidence package", alongside the
existing prohibition on selective deletion, extended from derived output to
commits. Ideally enforced by a pre-push hook rather than by intention.
