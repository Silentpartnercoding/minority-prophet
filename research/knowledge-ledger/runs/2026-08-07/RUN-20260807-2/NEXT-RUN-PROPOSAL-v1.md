# NEXT-RUN-PROPOSAL v1 — after RUN-20260807-2

## The smallest step that resolves the highest-value uncertainty

**Commission the independent implementation's re-run against protocol
v1.1.0.** This is KL-000's registered next gate, it is the other half of
KL-011's two-implementation prerequisite, and it is the direct test of
whether R1–R4 close the 22,440-world divergence. Nothing else in the backlog
approaches its information density.

**It is an owner commission, not an agent task.** This repository's agents
must not execute it and must not touch `impl-rs`; an in-house "independent"
re-run would produce an agreement worth nothing. What a repository run *can*
do is prepare the commission package and, afterwards, adjudicate the results.

## The commission package (repo-side work, ~1 commit)

1. The v1.1.0 registration set: `PROTOCOL-v1.1.0.md`,
   `preregistration-v1.1.0.json`, fixtures C01–C11.
2. **Artifacts listed as roles, not paths** — the v1.0.0 package leaked five
   reference paths through its `artifacts` list (IND-101); the operator's own
   remediation is adopted: redact to roles ("world generator", "invariant
   checker") or omit the list.
3. Isolation upgrade: run the implementer on a machine that does not hold the
   reference at all (OPERATOR-DISCLOSURE.md's remediation). This is the only
   change that upgrades the independence adjective from "qualified" to
   "environmental".

## Exact pass condition, registered before the results come back

- Identical conclusion distribution on all 110,840 receipt-producing
  exhaustive worlds (i.e., the 22,440 divergence closes to 0), and identical
  receipt/fail-closed partitioning as before.
- C11's `contentDigest` reproduced exactly — the first cross-implementation
  digest agreement the protocol has ever made possible.
- Randomized phase: 0 violations at a statistically consistent fail-closed
  rate; **counts are not compared** (replication, F11/SPEC-102).
- Adversarial: R2 and R3 refusals present (empty scope, duplicate ids).

Any residual conclusion disagreement after R1 localises a *new* ambiguity and
reopens the specification loop — that outcome is more informative than
agreement and must be published as the primary result, not smoothed over.

## What NOT to do in the same run

- Do not fold v1.2.0 repairs (F1/F2/F3/F4/F5/F11/F12/F13/F14, NAM-101) into
  the commission window. The commission target must not move while the
  implementer is working; that is the point of versioned registration.
- Do not touch the evaluator (any behaviour change reopens KL-000 entirely).
- Do not promote anything: `verified-independent` becomes claimable only if
  the re-run passes, and promotion is a separate owner-reviewed commit even
  then.

## If the re-run passes

KL-000 reaches `verified-independent` (pending owner promotion), KL-011's
two-implementation prerequisite is satisfied, and the run after next is the
v1.2.0 repair bundle followed by KL-011 preregistration at schema v0.2 — in
that order, because F1/F2's receipt-internal invariants are exactly the sort
of hole a five-stage cross-system transaction would fall into.

## If it fails

The disagreeing worlds are the deliverable. Classify each as: new ambiguity
(specification loop continues at v1.2.0), reference defect (KL-000 reopens),
or reimplementation defect (commission feedback). The v1.1.0 exact-equality
discipline of this run applies symmetrically: no smoothing, no averaging, the
divergence is the result.

## Estimated resources

Repo-side: one package-preparation commit, zero spend. Commission-side: the
implementer's time on a clean machine; no network beyond delivery; no data;
no authorization beyond the owner's decision to commission.
