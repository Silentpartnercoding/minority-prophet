# LIR-2 preregistration — precision-constrained root coverage

**Status:** frozen before candidate evaluation, method selection, new holdout
generation, model requests, or LIR-2 outcome inspection.

## Question

Can a root-specific grouping method answer more cases than the LIR-1E parent
baseline without introducing any false evidence-family merges?

LIR-2 is a new experiment. The completed 48 LIR-1E cases are development data
for LIR-2 and provide no confirmatory evidence for this new claim. The LIR-1E
canonical record remains unchanged.

## Development data

Use all 12 LIR-1E development cases and all 36 now-open LIR-1E confirmatory
cases as a 48-case LIR-2 development set. No new model calls are needed for
method selection. Their private claim files are bound by SHA-256:

- LIR-1E development claims:
  `93d6b2bc6d9bbe93811d756a42e7703a74977f2a61d9042db01a65dab5c3deb3`
- LIR-1E confirmatory claims:
  `5ffff9f790b9849574ed3648ccb88674e0884e97a8432c7af34ec57c31e19084`

## Frozen candidate method

For each case, start with one node per claim. Add every exposed direct-parent
edge. For every remaining unordered pair in the same case and proposition:

1. order the pair by timestamp, with claim ID as the deterministic tie-break;
2. compute the existing LIR score from observable fields only:
   `0.82 * token-Jaccard + 0.16 * exp(-hours/24)`;
3. add an undirected root-link when the score reaches the candidate threshold;
4. define inferred evidence families as connected components.

This method estimates record-root grouping directly. It does not claim an exact
parent for a similarity-created link. It receives no constructed truth, root,
source ID, expected answer, assignment cell, transformation label, or hidden
edge.

Candidate thresholds are:

`0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95`.

Evaluate candidates at the registered 40% deterministic edge hiding level on
the 48 development cases. A candidate is eligible only if:

- root-pair precision is exactly `1.0`; and
- inferred collapse never changes a raw-majority-correct case into an incorrect
  answer.

Among eligible candidates, select by this lexicographic rule:

1. greatest inferred answer coverage;
2. greatest root-pair recall;
3. greatest all-case correct yield (`correct inferred answers / all cases`);
4. higher threshold.

If no candidate is eligible, LIR-2 stops as a development failure and no new
holdout is generated.

## New confirmatory holdout

After the method and threshold are committed, generate exactly 36 new cases
with the already committed LIR-1E case generator and a new private 256-bit seed.
Commit the seed hash, request hash, construction-label hash, generator hash, and
prompt hash before model execution. Any case ID present in LIR-1E is excluded;
any collision fails closed and requires a new registered seed commitment before
model calls.

Use the same response roles, prompt, mutation plan, and exact models as LIR-1E:
Claude Fable 5 in `model-a` and GPT-5.6 in `model-b`. Use subscription billing,
180 planned calls, one mechanical retry for malformed output, and a 190-call
hard ceiling. Commit the response and receipt hashes before opening labels.

## Confirmatory metrics

At 40% hidden edges, report:

- root-pair precision, recall, and F1;
- root-count error;
- inferred answer coverage, accuracy among answered cases, all-case correct
  yield, and abstentions;
- majority, declared-collapse, and inferred-collapse accuracy and Brier score;
- declared-advantage survival;
- exact hidden-parent metrics from LIR-1E as a non-gating comparator;
- LIR-1E parent-baseline results on the same new cases;
- source adherence, retries, failures, token counters, and recorded billing; and
- 10,000 whole-case bootstrap intervals with seed `20260808`.

## Primary success criterion

All conditions must hold on at least 30 complete new cases:

1. zero false root-pair merges, so root-pair precision is exactly `1.0`;
2. root-pair recall is at least `0.80`;
3. inferred answer coverage is at least `0.80`;
4. inferred accuracy among answered cases is at least `0.80`; and
5. all-case correct yield is at least `0.65`.

The point criteria are primary. Bootstrap intervals describe uncertainty and do
not replace them. Failure of any condition rejects the joint LIR-2 claim.

## Integrity and interpretation

- Freeze the selected method before creating the new seed.
- Never tune on the new holdout, silently replace a provider, or drop an
  adverse case.
- Two clean materialization and scoring runs must be byte-identical before
  promotion.
- Publish success, failure, abstention, and blocked execution unchanged.
- A successful result would establish only higher-coverage constructed
  record-root recovery under these frozen conditions. It would not establish
  causal evidence independence, authenticate sources, prove content truth, or
  guarantee real-world performance.
