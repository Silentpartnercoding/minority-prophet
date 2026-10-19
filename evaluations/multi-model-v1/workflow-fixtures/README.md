# Workflow decision evaluation — exploratory development fixtures

This extends the existing evaluation area; it does not replace the frozen
capability tournament or the historical September 26 benchmark. The latter's
claimed 100-case artifact has not been located or reconstructed here.

Question: does a proposed MP composition improve invoice triage beyond ordinary
code? This first diagnostic is **not a real customer workflow or confirmatory
benchmark**. It is 15 small, hand-authored synthetic fixtures. The builder has
seen all labels. Builder, runner and reviewer share one operator/control domain.

## Reproduce without model credentials

From the repository root:

```sh
python3 evaluations/multi-model-v1/workflow_evaluation.py
python3 evaluations/multi-model-v1/workflow_evaluation.py --export
PYTHONPATH=. python3 -m pytest -q tests/test_workflow_evaluation.py
```

`--export` produces only the task policy and contestant-visible packets. The
reference file is read only by the scorer after local predictions are complete.
Both lanes receive the same projected packet. This is a code-level information
boundary, not a sandbox: future external runners must get only exported bytes,
in an environment without the repository/answer key or tools that can read them.

The report binds input, reference and source hashes and records repository
revision/dirty state. A source commit must accompany a retained run. This is
exploratory provenance, not retrospective preregistration.

## Policy and contestant scope

The artificial policy permits invoices up to USD 10,000. Above that, it requires
fresh, attributed, unanimously consistent approval evidence. Conflicts require
review. Missing or invalid evidence is not approval. All records in this fixture
are statements about the same authorization state, not a voting committee in
which a majority is sufficient. Timestamp units are synthetic integer ticks.

- `ordinary_rules`: ordinary conservative validation and consistency checks.
- `mp_root_vote_composition`: exactly the same amount/freshness/provenance guards,
  followed by the real `aggregation.root_vote.verdict` implementation. This
  deliberately naive composition is **not MP's full product, an existing policy
  engine, or a proposal for production authorization**. Root counts assess
  evidence under their assumptions; they do not grant permission.

There are structured, threshold, missing, stale/future, contradictory, copied,
unknown-origin and narrative-only cases. Origins are declared fixtures, not
authenticated real-world independence. Neither local lane performs text
extraction. The text-only USD 500 case therefore exposes an unnecessary review;
it must not be silently normalized using the answer key. The text-injection case
does not establish prompt-injection resistance because no model was run.

## Initial development result

| Lane | Correct / attempted | Wrong approvals | Reviews | Unnecessary reviews |
| --- | --- | --- | --- | --- |
| Ordinary rules | 14 / 15 | 0 | 10 | 1 |
| MP root-vote composition | 13 / 15 | 1 | 9 | 1 |

The MP composition's one fewer review is an incorrect approval, not useful
automation. Two positive origins and one contradictory origin lead root voting
to ALLOW where the workflow requires REVIEW. This is a mismatch between the
chosen aggregator and the task, not a defect in the counting theorem. Keep this
adverse result; do not tune it away and call the same fixtures confirmation.

Jev, OpenJev and frontier model lanes are explicitly **not run**. No paid API
calls, estimated competitor scores, production effects or superiority claims.
No customer savings, statistical generalization, or market demand established.

## Next experiment, if pursued

### Adapter correction (development regression only)

The original result above and `mp_root_vote_composition` remain unchanged as a
historical failed ablation (original commit `517faf33bc97d700c666a55e6cd12e076c655cd8`).
The corrected `mp_shared_policy` lane uses the **same** `rules()` decision as
the baseline. MP's actual root-vote output is recorded separately in
`mp_evidence`, including root sets, conflicts and unknown provenance; it cannot
override the workflow rule. The majority-conflict case therefore returns REVIEW
even while the diagnostic root vote is true. Repeated declared roots collapse
in the diagnostic, but declared IDs do not authenticate independence.

On these already-seen fixtures both current lanes score 14/15, with zero wrong
approvals and one unnecessary review of narrative-only input. This tie is by
construction: it verifies the policy boundary, **not added decision value from
MP**. Text extraction remains absent. No inputs or reference labels were changed.
These are post-result development regressions, not a new confirmatory run.
Establishing incremental value requires the fresh evaluation described below.

1. Select an actual anonymized workflow with its owner. Establish correct
   decisions from its policy and authoritative records, not model agreement.
2. Separate development from a newly frozen, unseen evaluation set. Freeze
   policy, MP adapter, ordinary-code baseline, extraction configuration,
   thresholds, versions, allowed tools and budgets before results are inspected.
3. Use a common evidence extraction stage or explicitly compare end-to-end
   pipelines with the same raw inputs; include its errors, latency and cost.
4. Compare ordinary conservative code, an existing MP-supported composition,
   and available external systems. Do not substitute the scoring oracle for MP.
5. Count every assigned case, invalid response, timeout and abstention. Report
   wrong approvals/holds, coverage, necessary/unnecessary reviews, per-family
   outcomes, paired differences and uncertainty; never reward abstaining on all
   cases or dropping failures. Price any paid runs before execution.
6. Primary success: fewer unnecessary reviews without more wrong approvals
   under predeclared risk limits. Preserve negative and inconclusive outcomes.

The development fixture demonstrates why a proper workflow adapter and ordinary
code comparator matter. It does not justify starting another product, publishing
a Jev takedown, or treating evidence assessment as authority.
