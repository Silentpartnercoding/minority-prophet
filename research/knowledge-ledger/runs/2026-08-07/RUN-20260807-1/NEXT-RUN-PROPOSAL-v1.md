# NEXT-RUN-PROPOSAL v1 — RUN-20260808-1

## The smallest run that resolves the highest-value uncertainty

**Commission an independent reimplementation of the transaction evaluator and
diff it against the reference across all 176,120 exhaustive worlds.**

Nothing else in the backlog is close. This one artifact unblocks two gates at
once:

- it is **KL-000's exact next gate** — `RESEARCH-METHOD.md` forbids the
  implementation author being the sole verifier, and KL-000's evaluator, world
  generator, invariant checker, and reproduction were all produced in one
  session by one agent;
- it is **half of KL-011's two-implementation requirement**, which is the
  binding prerequisite for any first-transaction attempt.

Commissioning it once serves both. Commissioning it twice would be waste, and
attempting KL-011 before it exists is not possible at all.

## Scope, deliberately narrow

**In scope**

1. One evaluator implementing `minority-prophet.knowledge-transaction.v0.1`,
   written from the public schema and `RESEARCH-DIRECTION.md` alone.
2. A differ that runs both evaluators over the frozen exhaustive enumeration and
   reports every disagreeing world.
3. A KL-011 preregistration at schema v0.2, written **only if** step 2 is clean.

**Explicitly out of scope**

- The full five-stage KL-011 transaction. That is the run after this one.
- Any schema change (`BL-002`, `BL-003`, `BL-006`). Each reopens KL-000 by
  invalidating the frozen evaluator hash, and mixing that with an independence
  test would confound both.
- Any promotion to `CANONICAL-RECORDS.md` or `PUBLIC-CLAIMS.md`.
- Durable-history anchoring. Still ineligible.

## Independence conditions — the part that determines whether the run means anything

These are the deliverable. A second implementation that fails them is a wrapper
wearing a different name, and would produce a confident, worthless agreement.

1. **No access to `knowledge_ledger/transaction.py`**, nor to
   `KL-000/src/kl000_baselines.py`, which contains four near-complete
   reimplementations and would defeat the purpose entirely.
2. **Different language or runtime.** Preferred, since it forecloses accidental
   shared idiom. Rust, Go, or TypeScript.
3. **No shared evaluator code**, including no shared canonical-JSON helper. The
   digest is part of what is being independently derived: `sort_keys`,
   `separators`, and `ensure_ascii` are exactly where two honest readings of
   "canonical bytes" diverge.
4. **Written against the schema, not against the reference output.** Given
   `reference-receipt.json` as a target, an implementer can fit it without ever
   understanding the rules — which is the failure this run is trying to detect.

Condition 4 is the one most easily lost by accident and the hardest to recover
from, because a fitted implementation agrees perfectly and proves nothing.

## Method

1. Freeze the exhaustive world stream to a file with a digest, so both
   evaluators consume identical input.
2. Run both. Compare `conclusion`, every `search` field, every `evidence` field,
   and `contentDigest`, world by world.
3. Classify each disagreement as: schema ambiguity, reference defect,
   reimplementation defect, or canonicalisation difference.
4. **Publish disagreements as the primary result.** They are more informative
   than agreement: each one localises a sentence in the schema that two
   competent readers understood differently, which is precisely what will break
   a real cross-system transaction.

## Success, failure, and what each licenses

| Outcome | Meaning |
|---|---|
| Zero disagreements across all 176,120 | KL-000 → verified-independent; KL-011 becomes eligible |
| Disagreements only in canonicalisation | The schema under-specifies canonical bytes. Fix and re-run; this is a **finding**, not a failure |
| Disagreements in conclusions | One implementation is wrong, or the schema is ambiguous on a load-bearing rule. **KL-000 reopens.** Highest-information outcome |

A clean diff does **not** establish that either implementation is *correct* —
only that two independent readings of the schema agree. Both could share a
misreading the schema invites. That residual is irreducible without a third
reading or a formal specification, and should be stated rather than glossed.

## Prerequisites

| | Status |
|---|---|
| Frozen exhaustive enumeration | ready, deterministic from `kl000_worlds.py` |
| Public schema | ready |
| Reference evaluator | ready, hash-frozen |
| Second implementer with enforced isolation | **required — not yet arranged** |
| Human authorization | none for execution; needed only to publish |

The single blocking prerequisite is arranging an implementer who genuinely has
not seen the reference. If that isolation cannot be enforced, **say so and do not
run the experiment** — a reimplementation by an author who has read the reference
produces an agreement that cannot be distinguished from independence, which is
worse than no result, because it looks like one.

## Estimated resources

- Reimplementation: 200–400 lines in the chosen language.
- Differ and analysis: ~150 lines.
- Compute: minutes. 176,120 worlds is ~10s per evaluator in Python.
- Spend: **zero**, unless a paid model is used for the reimplementation — which
  requires founder authorization and an approved budget first.
- No data acquisition, no human subjects, no network dependency.

## If it comes back clean

The run after next is KL-011 proper: five stages, one bounded claim, with
paraphrase, retry, reordering, duplication, partial failure, one malicious
duplicate, and one unavailable location injected — then a third-environment
reproduction. Only after all of that passes does a `Candidate First
Transmission` become nameable, and only with a durable-history receipt does the
`First Transmission` title apply.

Both titles remain unclaimed and unclaimable until then.
