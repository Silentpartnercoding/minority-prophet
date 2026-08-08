# ORIENTATION — RUN-20260807-8

Opened 2026-08-08T00:25:27Z on HEAD `485b172` — the operator's merge of
`github/main` into the run branch. PR #17 is **MERGED**; main carries the
whole program through RUN-5 plus third-party work (Codex EXP009, a
verifier-independence experiment, PRs #18–#20); the branch is 57 ahead /
0 behind. Per the brief: no re-branch, no rebase — the sync is done.

## State verification — every brief claim checked, all hold

HEAD `485b172`; tree clean; `git rev-list --left-right --count
github/main...HEAD` = 0/57; all four KL-000 registration chains verify
post-merge; CANONICAL-RECORDS.md, EVIDENCE-ALIGNMENT.md, PUBLIC-CLAIMS.md
byte-identical to main (the merge took main's promotions and added none);
**102 tests passing** (the suite grew with main's merged experiments).

## The run, in order

1. **BL-035 brief audit first** (authorised; "before executing anything
   else"): every operator brief captured in the run records, judged against
   BRF-101, including this run's own brief.
2. **A1 owner decision recorded** — complete coverage over an empty evidence
   ledger yields `absent_within_declared_scope`; decided, not derived;
   rejected reading preserved; the 4-world count confirmed by enumeration,
   not trusted.
3. **The SCH-001 migration** — design and register
   `minority-prophet.preregistration.v0.2` as a definition document, migrate
   the eleven seeded kernels, and add suite enforcement (a v0.2 document
   omitting a required field or carrying a bare null without a stated reason
   fails). KL-000's four frozen registrations untouched; chains must still
   verify; eleven kernels stay `seeded` — a schema with more fields is not
   evidence.
4. Close with the packet, whose authority is
   `tests/test_closing_packets.py::REQUIRED` — noting now that this brief's
   own 7-member list disagrees with the 15-member REQUIRED list and the
   brief itself pre-resolves the disagreement in REQUIRED's favour.

## Boundaries

KL-000 stays `adversarial-passed` at v1.3.0; all 102 tests keep passing; no
canonical record, paper, or PUBLIC-CLAIMS edit; nothing pushed.
