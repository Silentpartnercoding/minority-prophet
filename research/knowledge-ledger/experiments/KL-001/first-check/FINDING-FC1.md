# KL-001 first check — finding

Executed by RUN-20260807-6 against the unchanged KL-000 evaluator
(`sha256:15dfd500…3a3e21f`). Registrations FC1 (`1bcf474`) and FC1.1
(`d76055b`) preceded their executions; results are committed beside them.

## The verdict, plainly: (a) — this check is I2 restated

The incomplete-coverage repository (W1: four mandatory files declared, two
searched, one unavailable, one not searched, two scanners supporting
cleanliness) **cannot obtain a clean conclusion**: `not_established`, reason
"The declared search space was not exhaustively searched." The complete
variant (W2) gets `absent_within_declared_scope`. So the named check
passes — and it passes for exactly the reason any incomplete-coverage world
fails: the evaluator saw nothing repository-shaped at all.

The demonstration: W4, the same structure re-labelled into KL-000's
enumeration vocabulary, sits inside KL-000's declared bounds — it **is one
of the 176,120 worlds two independent implementations already agreed on** —
and its receipt is identical to W1's in every name-free field (conclusion,
reason, all of search, and the five numeric evidence members). The receipts
diverge on exactly three members: `claim.proposition`,
`evidence.supportingRoots`, and the `contentDigest` those strings induce.
"Mandatory file" maps to "declared location" by pure renaming. **No new
evidence about the evaluator was produced, and KL-001's named first gate was
already paid by KL-000** (fixture C08 is literally this shape; I2 held over
the full enumeration in both implementations).

Answering (a) is the result. It cost four synthetic worlds and two small
registrations instead of a corpus.

## What the run also demonstrated on purpose (W3)

The same repository reality with the two uncovered files simply **omitted
from the declaration** — declared 2, searched 2 — obtains
`absent_within_declared_scope` cleanly. That is ADV-001 in repository
costume: the evaluator honours the declared scope and cannot see what the
declaration left out. The layer that decides *which files are mandatory* is
where KL-001's real risk lives, and that layer does not exist yet.

## What the real first gate is, and what it costs

The genuinely new objects, none of which FC1 touched:

1. **The mapping pipeline** — the component that turns a repository into
   ledgers: what counts as a mandatory file, what counts as searched, which
   scanner outputs become which roots. This is where scope-declaration
   honesty (ADV-001, W3) and root-attribution honesty (ADV-004 class) live;
   its rules need registering as carefully as the evaluator's were.
   Estimate: 200–400 lines plus its own registered mapping rules.
2. **The frozen corpus** — N synthetic repositories with machine-checkable
   planted defects and clean controls, produced by a seeded generator and
   digest-manifested **before** any evaluation. Estimate: 300–500 lines of
   generator plus the manifest discipline the program already practises.
3. **The registered endpoints** — the false-clean rate over planted-defect
   repositories, and (existing blocker, still binding) baseline
   true-positive recall measured **before** the dual ledger is applied,
   without which the registry's 95%-preservation target is unfalsifiable.
4. **The v0.2 preregistration** (SCH-001) carrying all of the above.

Zero spend if the pipeline under test is deterministic tooling; any metered
model in the pipeline requires founder authorization first (the KL-002
condition applies equally here). Altogether roughly one focused run of work
— comparable to KL-000's original build.

## A registration defect of this run, on the record

FC1's E4 **failed as registered**: it demanded identity of "all of
`evidence`" between W1 and W4, but `supportingRoots`/`opposingRoots` echo
declared rootId strings by the registered receipt object — the expectation
quantified over name-carrying fields. The failure is a drafting error of
this run (the M15/H1 family: a concept written down instead of the fields it
quantifies over), preserved in `results/fc1-result.json`; FC1.1 corrected
the expectation by new registration and confirmed verdict (a). E1–E3 passed
under the original registration and were not re-judged.

## What this does and does not change for KL-001

- The kernel **stays `seeded`**. A check discharged by a prerequisite
  advances nothing; the ladder's next state still requires KL-001's own
  preregistration.
- The record now says the named first check is discharged and names the real
  first gate with its cost. That gate is **not committed** — committing it
  is the owner's act, as it was for I12.
