# Registry audit — `EXPERIMENT-REGISTRY.json` against `RESEARCH-METHOD.md`

Produced by `scripts/audit_preregistrations.py` (machine output preserved at
`logs/registry-audit.txt` and `logs/registry-audit.json`).

**Nothing in this audit is repaired by this run.** Every disagreement below is
recorded and left in place. Repairing them changes protocol documents, which the
program's own rules require to happen in a dedicated PR, separate from a run
that also reports a confirmatory result.

## Agreements

- All twelve registry ids (`KL-000`..`KL-011`) have a matching directory. No
  registry-only ids, no disk-only ids.
- Every directory carries `PROTOCOL.md`, `preregistration.json`, `STATUS.json`.
- Every registry entry's `question`, `null`, `target`, and `primaryEndpoint`
  match its preregistration verbatim.
- Registry `status` is `seeded-not-executed`, which agrees with all twelve
  `STATUS.json` files (`state: seeded`) and all twelve preregistrations
  (`status: incomplete-seed`). The registry does not overclaim.

## Disagreement D1 — the preregistration schema cannot express four of the twelve required fields

`RESEARCH-METHOD.md` requires twelve numbered preregistration fields.
`minority-prophet.preregistration.v0.1` has **no key at all** for four of them,
in all twelve experiments:

| RESEARCH-METHOD requirement | Missing key |
|---|---|
| 1. identifier and *immutable protocol version* | `protocolVersion` |
| 9. effect size, uncertainty interval, *multiple-testing correction* | `multipleTestingCorrection` |
| 11. frozen seeds, splits, code commit, *environment*, artifact paths | `environment` |
| 12. safety boundary and *required human authorization* | `humanAuthorization` |

Severity: **high**. This is not a data-entry gap that filling in fields would
close. A preregistration can be schema-valid and 100% populated while still
violating `RESEARCH-METHOD.md`, because the schema has nowhere to put these
four facts. `RESEARCH-METHOD.md` says an experiment "is incomplete until all
fields below are committed" — under v0.1 that condition is unsatisfiable.

Consequence for this run: KL-000's preregistration is written against
`minority-prophet.preregistration.**v0.2**`, a superset that adds exactly these
four keys and changes nothing else. v0.1 files are left untouched for the other
eleven experiments. The v0.1 -> v0.2 migration for KL-001..KL-011 is deliberately
**not** performed here; it is proposed in `RESEARCH-BACKLOG-v1.json` as its own
PR.

## Disagreement D2 — five of eight required directory entries are absent everywhere

The run prompt requires each `experiments/KL-NNN/` to contain `PROTOCOL.md`,
`preregistration.json`, `fixtures/`, `src/`, `tests/`, `results/`,
`REPRODUCE.md`, `STATUS.json`.

All twelve directories are missing the same five: **`fixtures/`, `src/`,
`tests/`, `results/`, `REPRODUCE.md`**.

Severity: **medium**. This blocks the program-success criterion "every kernel
has at least a complete preregistration, fixture, tests, status, and exact next
gate" for all twelve kernels.

This run closes the gap for KL-000 only. KL-001..KL-011 remain at 3/8 and their
`STATUS.json` files now name this as part of their next gate.

## Disagreement D3 — `firstGate` conflates three different concepts

The registry's `firstGate` field carries a different kind of statement in
different entries:

| Entry | `firstGate` is actually a… |
|---|---|
| KL-000 | **stop condition** ("One violation rejects the invariant and blocks every downstream kernel") — duplicated verbatim in `preregistration.stopCondition` |
| KL-001, KL-005, KL-008 | **decision rule** constraining permitted conclusions |
| KL-004, KL-006, KL-009 | **safety boundary** ("Retrospective research only; no patient recommendation") |
| KL-011 | **reporting/promotion rule** |

Severity: **medium**. `RESEARCH-METHOD.md` treats stop conditions (field 10) and
safety boundaries (field 12) as distinct required fields. A single registry key
that silently means "stop condition" for KL-000 and "safety boundary" for KL-004
cannot be machine-checked against either, and a reader who mechanically copies
`firstGate` into `stopCondition` — as the KL-000 seed did — will leave
`safetyBoundary` null while appearing to have transcribed the registry
faithfully.

Not repaired here. Splitting `firstGate` into `stopCondition`,
`decisionRule`, and `safetyBoundary` is proposed in the backlog.

## Disagreement D4 — `RESEARCH-METHOD.md` requires ten controls "everywhere"; the registry encodes none

`RESEARCH-METHOD.md` §"Controls required everywhere" lists ten mandatory
controls (head counting, source counting, evidence-ledger-without-coverage,
search-ledger-without-collapse, dual ledger, independent-evidence,
copied/shared-dependency, incomplete-coverage, counterexample-in-searched, and
counterexample-in-unsearched).

Neither `EXPERIMENT-REGISTRY.json` nor `preregistration.v0.1` has any field
naming controls. `baselines` (empty in all twelve) is the nearest, but baselines
and controls are different objects: a baseline is a comparator method, a control
is a world whose correct answer is known in advance.

Severity: **medium**. The ten controls are therefore unenforceable by any
machine check. This run implements all ten as named KL-000 fixtures and adds a
`controls` array to preregistration v0.2, but does not add the field to v0.1 or
to the registry.

## Disagreement D5 — phase vocabulary does not match the kernel-state ladder

`RESEARCH-METHOD.md` "Required execution phases" has **eight**:

`specification -> fixture -> exhaustive-small -> randomized -> adversarial -> retrospective-real -> prospective-shadow -> bounded-pilot`

The run prompt's kernel-state ladder has **nine**:

`seeded -> preregistered -> fixture-passed -> exhaustive-passed -> randomized-passed -> adversarial-passed -> retrospective-passed -> shadow-passed -> bounded-pilot-passed`

`seeded` and `preregistered` have no counterpart in `RESEARCH-METHOD.md`, whose
first phase `specification` maps onto the prompt's *transition* from `seeded` to
`preregistered`. Additionally every `STATUS.json` records
`lastCompletedGate: "registry-entry"`, which is not a phase in either list.

Severity: **low**. The mapping is unambiguous in practice. Recorded because the
two documents are both normative and a machine cannot currently validate a
`STATUS.json` state against `RESEARCH-METHOD.md`. This run uses the prompt's
nine-state ladder, since `STATUS.json` already does.

## Disagreement D6 — the evaluator's search vocabulary is narrower than `RESEARCH-DIRECTION.md`'s

`RESEARCH-DIRECTION.md` §"Search ledger" specifies recording locations
"searched, **failed**, **unavailable**, or **not searched**" — four statuses.

`knowledge_ledger/transaction.py` defines
`TERMINAL_SEARCH_STATUSES = {"searched", "unavailable"}` and reports only
`declared`, `searched`, `unavailable`, `complete`.

Severity: **low**, and the behaviour is *safe*: any status outside the terminal
set makes `search_complete` false, so `failed` and `not_searched` correctly
prevent an absence conclusion. But they are counted in neither `searched` nor
`unavailable`, so for a ledger containing them
`declared != searched + unavailable`, silently. A reader reconciling those three
numbers would conclude the receipt was malformed.

This run preregisters that arithmetic as an explicit KL-000 invariant (I8) and
tests it rather than assuming it. Not repaired.

## Disagreement D7 — two fields named in `RESEARCH-DIRECTION.md` are absent from the receipt

`RESEARCH-DIRECTION.md` §"Evidence ledger" requires the emitted record to carry
`flip_budget` **and** `conversions_to_reverse` "in their correct units", plus
"unattributed evidence, uncertainty, and the reason for abstention".

The receipt emits `conversionsToReverse` and `reason`. It has no `flipBudget`
and no unattributed-evidence or uncertainty field.

Severity: **low** for KL-000 (whose invariants do not depend on them), **medium**
for KL-011, whose acceptance gate requires that "protected fields" survive
crossing systems — a field the reference receipt never emits cannot be shown to
survive. Recorded in the backlog as a KL-011 prerequisite.

## Summary

| Id | Severity | Blocks |
|---|---|---|
| D1 | high | `RESEARCH-METHOD.md` compliance for all twelve preregistrations |
| D2 | medium | program-success criterion "every kernel has fixture, tests, status" |
| D3 | medium | machine-checking stop conditions vs safety boundaries |
| D4 | medium | machine-enforcement of the ten mandatory controls |
| D5 | low | validating `STATUS.json` against `RESEARCH-METHOD.md` |
| D6 | low | reconciling search arithmetic in receipts |
| D7 | low (KL-000) / medium (KL-011) | KL-011 protected-field preservation |

None of D1–D7 falsifies a KL-000 invariant, and none blocked this run's
confirmatory execution. D1 changed how this run wrote KL-000's preregistration
(v0.2 instead of v0.1); the rest are recorded only.
