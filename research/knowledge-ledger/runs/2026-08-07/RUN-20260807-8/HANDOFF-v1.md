# HANDOFF v1 — RUN-20260807-8

The SCH-001 migration is done: eleven kernels can now preregister. A1 is
decided and recorded; the brief-layer audit ran first and its findings
stand. The program remains closed with no committed gate; everything next
is owner scheduling (BL-039).

## Where the work is

Base 485b172 (your merge of github/main; verified before acting). Commits:
e07b19a (open, brief claims verified), 7df7f89 (A1 decision + BL-035
audit), 6e286b9 (migration -- landed on a RED suite, see VER-102), 88cb850
(vocabulary + idempotency fix, suite green), then this packet. Tree clean;
123 repo + 88 KL-000 tests green with pipefail armed; all four KL-000
chains verify; canonical files byte-identical to main; nothing pushed.

## What is now true

- research/knowledge-ledger/schemas/preregistration-v0.2.json is the schema
  definition of record, test-checked against RESEARCH-METHOD's 12 items.
- All twelve kernels' preregistration.json are v0.2 and conformance-tested
  (21 new tests incl. six planted-defect checks on the validator itself).
  Eleven stay seeded ('incomplete-seed' status, per the standing guard).
- KL-000 STATUS permanentLimits: A1 DECIDED (4 worlds, re-verified;
  rejected reading preserved). A2 is the last undecided decision.
- BL-035-BRIEF-AUDIT.md: 7 of 9 packet-requiring briefs defective under
  BRF-101; your brief passes via its citation clause and its 7-of-15
  enumeration defect is noted, as you instructed. Cite, don't re-type.

## Yours

1. BL-039 -- schedule registrations (KL-001 gate and KL-011/A2 first by
   groundwork); 2. BL-037 -- the receipt-schema dependency extension
   (digest-moving, deliberately versioned, unlocks KL-006/KL-008);
3. A2; 4. whether RUN-6/7/8 commits go to main as a follow-up PR (this
   branch is 57+ ahead; delivery is yours); 5. promotion, untouched as
   always.

## Cautions for any resumer

VER-102: verification gates on exit status -- pipefail or unpiped. VOC-101:
status vocabularies are registered; migrationRecord carries migration
facts. The third-party EXP009/HVI-1 work on this branch is out of program
scope: audited for test-count only, not reviewed, not touched.
