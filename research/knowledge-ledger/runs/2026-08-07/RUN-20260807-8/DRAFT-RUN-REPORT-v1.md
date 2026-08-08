# DRAFT RUN REPORT v1 — RUN-20260807-8

The SCH-001 migration is done, and the answer to the brief's closing
question is plain: **yes — eleven kernels are now able to preregister.**
`minority-prophet.preregistration.v0.2` carries every one of
RESEARCH-METHOD.md's twelve required items in a dedicated field (the mapping
is itself test-checked), and KL-000's four registrations — which validate
against the new definition unchanged — are the end-to-end proof the schema
can carry a complete confirmatory program. What remains for the eleven is
**content at registration** (population, endpoints, seeds — the science) and
scaffolding (ENG-001), not schema. One caveat stated rather than glossed:
KL-006 and KL-008 additionally need the *receipt*-schema dependency
extension (ADV-005, open BL-003) before their subject matter is
representable — a different schema, honestly outside this repair.

## The two owner items, first

**A1 is decided and recorded** (KL-000 STATUS `permanentLimits`): complete
coverage with an empty evidence ledger yields
`absent_within_declared_scope` — silence across a fully searched declared
scope is the finding. Recorded as a decision, not a derivation; the rejected
reading (an empty ledger is indistinguishable from a search never run — the
independent implementer's F7, maintained through all three of its runs)
preserved with its reasoning, per the R1/R5.2 discipline. The count was
**confirmed by enumeration, not trusted: exactly 4 worlds**, all already
concluding absent under the registered function — zero numeric effect, like
the R5.2 ratification. **A2 (19,152 worlds) is now the last undecided
conclusion-function decision.**

**The BL-035 audit ran first**, as authorised
(`BL-035-BRIEF-AUDIT.md`): **7 of 9 packet-requiring briefs were defective
under BRF-101** — all predating the rule — and defect tracked loss exactly
as BRF-101 predicts: zero losses while an enumeration or fresh precedent
was in context, two once neither was, zero after enforcement. **This brief
passes**, via its citation-with-precedence clause — and carries a noted
defect, stated plainly as instructed: its "exactly, by name" list names 7
of REQUIRED's 15 members, so its own precedence rule activated on first
use. The audit's standing recommendation: **cite the enumeration of record;
don't re-type it** — an authoritative-sounding partial enumeration is more
dangerous than a bare concept.

## The migration

- **Schema registered as a definition**, not a practice:
  `research/knowledge-ledger/schemas/preregistration-v0.2.json` — required
  fields mapped to the method's twelve items, the unanswered convention
  (`{"status": "unanswered", "reason": …}`; bare null forbidden except the
  registered `protocolCommit` design), scope and enforcement declared.
- **Eleven kernels migrated by committed, idempotent script**
  (`scripts/migrate_preregistrations_v02.py`): populated v0.1 values carried
  verbatim; unanswerable fields recorded as unanswered *with kernel-grounded
  reasons*; safety boundaries and authorization requirements **populated
  now, per kernel, from the program record** — retrospective-only for
  KL-004, simulation-only for KL-009, founder authorization for KL-002's
  metered inference / KL-007's human participants / KL-003's dataset
  licences, KL-011's inherited A2/SCH-005/ADV-001/F11 constraints.
- **All eleven states stay `seeded`** — a schema with more fields is not
  evidence. Each STATUS discharges its schema blockers with the superseded
  text retained.
- **Enforcement, not prose**: `tests/test_preregistrations.py` — twelve
  documents validated; the method-coverage claim checked; and the validator
  itself tested against six planted defects (missing field, bare null,
  null-without-note, reasonless unanswered, empty collection, nested null).
- **KL-000 untouched**: four frozen registrations unmodified, all four
  chains verify, its 88 tests green.

## Two incidents of this run, on the record

1. **A commit landed on a red suite.** The migration's first commit used an
   invented status string (`seeded-migrated-v0.2`) that the program's own
   standing guard — *a seeded experiment must not look preregistered* —
   correctly rejected in favour of the registered `incomplete-seed`
   vocabulary (the NAM-101 one-vocabulary lesson, relearned at the schema
   layer). It landed because the verification pipeline piped pytest into
   `tail`, masking the exit code (VER-102). Fixed in the immediate follow-up;
   every subsequent verification in this run, including the close, runs with
   `pipefail` armed. The guard did its job; my pipeline muzzled it.
2. **The migration script wasn't idempotent** on first writing (rejected its
   own output); made re-runnable in the same fix.

## Suite and state

**123 passing** (102 inherited including the merged Codex work, untouched;
21 new preregistration tests), 88 KL-000, chains intact, canonical files
still byte-identical to main, nothing pushed. KL-000 `adversarial-passed`
at v1.3.0 throughout.

The first-transaction gate remains **NOT REACHED**. Eleven kernels remain
`seeded` — now able to preregister, with what stops each of them written
inside its own preregistration as reasons instead of nulls.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
