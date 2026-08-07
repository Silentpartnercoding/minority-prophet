# KL-000: dual-ledger conformance — protocol v1.0.0

Status: **preregistered.** This document and `preregistration.json` are committed
before the implementation exists and before any confirmatory outcome is
inspected.

Supersedes the seed protocol (unversioned) that carried only the registry
question and a completion route. The seed is preserved in git history.

## Question

Can the evaluator prevent recorded copies from adding evidence, and incomplete
coverage from proving absence?

## Why this kernel is first

`EXPERIMENT-REGISTRY.json` states that one KL-000 violation "blocks every
downstream kernel". KL-001..KL-011 all assume an evaluator that collapses copies
and refuses to convert incomplete coverage into absence. If that assumption is
false, every downstream result measures the wrong object. KL-000 is therefore a
hard prerequisite, and this run does not skip it for a more impressive
demonstration.

## What is under test

`knowledge_ledger/transaction.py` at
`sha256:15dfd500…3a3e21f`, unmodified. KL-000 tests the evaluator as it stands.
No evaluator behaviour is changed by this experiment; if a violation is found it
is reported, not repaired inside the confirmatory run.

## Hypotheses

- **Null.** At least one recorded copy changes evidential mass, or one
  incomplete search yields absence.
- **Target.** Zero violations in exhaustive small worlds and one million frozen
  randomized worlds.

## The ten hard invariants

| | Invariant | Rejects the null by showing |
|---|---|---|
| I1 | copy invariance | duplicating a record cannot change any evidential quantity |
| I2 | bounded absence | absence is unreachable while any location is unsearched |
| I3 | side separation | one root on both sides fails closed |
| I4 | deterministic replay | identical input yields identical bytes and digest |
| I5 | counterexample dominance | one opposing root forces `present` at any coverage |
| I6 | digest integrity | every receipt self-verifies; every mutation is caught |
| I7 | order invariance | permutation changes nothing, including the digest |
| I8 | search arithmetic | the three coverage counts reconcile against `declared` |
| I9 | fail-closed parsing | malformed input raises, never concludes |
| I10 | copies never mint roots | `distinctRoots` tracks distinct rootIds exactly |

I1 and I10 answer the first half of the question; I2 and I5 answer the second.
I3, I4, I6–I9 are the supporting conditions under which those answers mean
anything.

Full statements are in `preregistration.json`. All ten are **hard**: one
violation halts the confirmatory run, is preserved with its complete world, and
rejects the invariant.

## Phases

Executed in order. A later phase does not run if an earlier one fails.

1. **Fixture.** The ten mandatory controls C01–C10 from `RESEARCH-METHOD.md`.
2. **Exhaustive-small.** Complete cartesian enumeration of **176,120** worlds:
   location ledgers of length 1–4 over four statuses (340), evidence ledgers of
   length 0–3 over three roots and two sides (259), two claim types.
   `340 × 259 × 2 = 176,120`. The generator asserts this count before any
   invariant is evaluated; a mismatch invalidates the run.
3. **Randomized.** 1,000,000 worlds from frozen seed `20260807`, with wider
   bounds (1–12 locations, 0–24 records, 8 roots).
4. **Adversarial.** The ten attacks in `tests/test_kl000_adversarial.py`.

## Power of the test

A conformance suite that passes everything may be measuring nothing. Four
ablated evaluators are therefore run against the same worlds and the same
checker, and each **must** be caught:

| Baseline | Ablation | Must fail |
|---|---|---|
| B1 head-count | ignores roots, concludes from record count | I1 |
| B2 source-count | counts roots, ignores the search ledger | I2 |
| B3 evidence-without-coverage | collapses roots, no coverage requirement | I2 |
| B4 search-without-collapse | full coverage, counts records not roots | I1 |
| B5 dual ledger *(under test)* | none | must pass all ten |

If any of B1–B4 records zero violations, the checker is vacuous and the run is
**invalidated** — not reported as a pass. This is the preregistered positive
control and it is as load-bearing as the result itself.

## Two preregistered limits, stated before execution

These are declared now so that they cannot later be presented as discoveries or
quietly omitted.

**C09 and C10 are indistinguishable to this evaluator.** Schema v0.1 has no
field linking an evidence record to a search location. The evaluator cannot know
where a counterexample was found. For absence claims this is conservative and
safe — one counterexample refutes absence wherever it came from — so identical
treatment of "counterexample in a searched location" and "counterexample in an
unsearched location" is the **expected and permitted** outcome, not a violation.
The genuine blind spot is the receipt that asserts a location was `unavailable`
while carrying evidence from it: the evaluator cannot detect that
contradiction. This is reported whatever the result.

**Shared dependency is not representable.** Partial dependence between two
distinct rootIds cannot be expressed in schema v0.1, so KL-000 cannot test it.
`RESEARCH-METHOD.md` requires a "copied or shared-dependency condition" as a
control; C07 covers the copied half. The shared-dependency half is recorded as a
limit rather than silently counted as covered.

## Stop, failure, and invalidation

- **Stop.** First hard violation halts the confirmatory run; the world is
  preserved verbatim.
- **Failure.** Any B5 violation rejects the invariant, sets KL-000 `failed`, and
  blocks downstream promotion.
- **Invalidation.** Generator out of declared bounds; world count ≠ 176,120;
  evaluator hash mismatch; seed not reproducing an identical stream; or any of
  B1–B4 passing. An invalidated run is `incomplete` — never negative, never
  positive.

## Why `protocolCommit` is deliberately null

`preregistration.json` carries `"protocolCommit": null`, and it stays null. This
is a registration decision, not an unfilled field.

A preregistration's entire value is that it existed, unchanged, before the
result was known. Editing the registered document afterwards to insert its own
commit hash requires modifying the very artifact whose immutability is the
claim. The amended file then has a different hash from the one that was
registered, and a reviewer must take on trust that only the hash field changed.
That is a weaker guarantee than the one preregistration is supposed to provide,
and it is weaker in exactly the direction that matters: it makes
"registered first" unverifiable by inspection.

So the binding runs the other way. Git assigns the commit; a **sidecar**,
`PROTOCOL-COMMIT.txt`, records it afterwards. The preregistration is never
touched after registration, and the chain is checkable in both directions:

```bash
P=research/knowledge-ledger/experiments/KL-000
test "$(git log -1 --format=%H -- $P/preregistration.json)" \
   = "$(cat $P/PROTOCOL-COMMIT.txt)" && echo "unedited since registration"
```

The **most recent** commit touching `preregistration.json` must equal the
sidecar's contents, and that commit must precede every result commit. The two
stay equal for exactly as long as the file is never edited again, so the
equality *is* the immutability claim, mechanically checkable at any time.

If they disagree, the registration is void — which is the property a mutable
`protocolCommit` field cannot offer, because there is nothing left to disagree
with.

> A first version of this check used `git log --diff-filter=A`, asking for the
> commit that **added** the file. That is wrong here and returns `2068c69`, the
> original seed commit, because registration *modified* an existing seed rather
> than creating a new file. The error is recorded rather than quietly fixed: a
> verification procedure that reports the wrong commit while appearing to
> succeed is worse than none, and this one would have been believed.

The freeze that actually carries scientific weight is **inside** the
preregistration and predates any result: `evaluatorUnderTest.sha256`, the
declared bounds, and the frozen seed. `protocolCommit` is provenance metadata
about the document, not about the experiment.

## Amendment log

Protocol version remains **1.0.0**. Amendments are listed here rather than
applied silently.

| # | When | Change | Experimental content affected |
|---|---|---|---|
| 1 | after registration commit `c977347`, **before** any confirmatory phase was executed | Added the section above, declaring the null-`protocolCommit` decision that was previously stated only in `preregistration.json`'s `protocolCommitNote`. Prompted by operator review. | **None.** No hypothesis, bound, seed, invariant, control, baseline, endpoint, or condition changed. |

The registered content of `preregistration.json` is unmodified. Confirmatory
phases had not run when this amendment was made, so no outcome could have
influenced it.

## Safety boundary

Synthetic worlds only. No personal, patient, sealed, classified, or restricted
data. No network. No spend. No actuation. No medical, legal, governmental,
financial, or autonomous decision authority. Execution needs no human
authorization; **publishing** and **promotion** do, and neither is performed by
the run that produces the result.

## What a pass would and would not license

**Strongest supported claim if all phases pass.** Within the declared bounds,
the reference evaluator did not allow a recorded copy to change evidential mass,
and did not allow an incomplete search to yield an absence conclusion.

**Nearest unsupported extension.** That the dual ledger recovers truth; that
declared roots are genuinely independent; that the invariants hold outside the
declared bounds; that any real-world evidence process is improved. A conformance
result establishes behaviour in a frozen model and nothing beyond it.

KL-000 passing does **not** constitute a knowledge transaction, a cross-system
result, or any part of a First Transmission. It is the precondition that makes
KL-011 worth attempting.
