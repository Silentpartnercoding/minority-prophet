# LIR-1 preregistration — lineage inference boundary pilot

**Status:** frozen before pilot implementation, data acquisition, threshold
selection, or outcome inspection.

## Question

When declared ancestry is withheld, how much of the advantage of
declared-lineage evidence aggregation can be recovered from observable text,
time, links, and mutation inheritance?

## Scientific boundary

LIR-1 estimates record descent and evidence-root groupings. It does not infer
truth from popularity, prove causal independence from textual difference, or
treat authentication as independence. Every score is reported within a label
basis and target scope. Results from proxy labels are exploratory and cannot
support the primary claim.

## Label strata

- `constructed_exact`: parent and evidence-root identity are known because the
  records were generated under a logged construction.
- `explicit_edge`: a platform or corpus records a parent edge. Withholding that
  edge tests recovery of the recorded edge, not causal independence.
- `adjudicated_lineage`: a frozen case file supports lineage through timestamped
  primary records and a documented adjudication rule.
- `heuristic_proxy`: a reproducible rule supplies a useful but unverified
  label. These observations are exploratory only.
- `unknown`: no evaluable lineage answer is asserted.

No aggregate may pool these strata as if they had equal epistemic status.

## Units and splits

The unit is a `case_id`: one rumor, quote cluster, retracted paper and its
citations, press-release story, citogenesis incident, prediction question, or
generated factual question. A case never crosses development and confirmatory
splits. Splits are deterministic by SHA-256 of `dataset|case_id`: the first
20% are development, the remaining 80% confirmatory. Thresholds may use only
development cases.

The pilot caps each dataset at 5,000 claim instances. If fewer than 30 eligible
confirmatory cases or 200 evaluable hidden edges remain, that dataset is
reported as underpowered and excluded from confirmatory synthesis.

## Frozen methods

1. **Majority:** one vote per claim instance.
2. **Declared collapse:** one vote per root supplied by the held-out label.
   This is an oracle ceiling, never a deployable result.
3. **Inferred collapse:** roots predicted without any label-only field.
4. **No-text ablation:** inference from time and exposed links only.
5. **No-time ablation:** inference from text and exposed links only.

The initial inference baseline is intentionally transparent: normalized token
similarity, mutation-token inheritance, temporal ordering/proximity, and
exposed links feed a deterministic parent score. A threshold is selected once
on development cases to maximize parent F1, with ties resolved toward the
higher threshold. No confirmatory threshold tuning is permitted.

## Perturbation

For datasets with explicit or constructed parent edges, hide a deterministic
fraction of eligible non-root edges at each level:

`0.05, 0.15, 0.25, 0.40, 0.55, 0.70, 0.85, 0.95`.

Selection uses SHA-256 of `dataset|case_id|claim_id|fraction|20260808` and is
nested: every edge hidden at a lower fraction remains hidden at higher
fractions. Labels remain in a separate evaluation view and are never included
in inference features.

## Metrics

Reported per dataset, label stratum, hidden fraction, and confirmatory split:

- hidden-parent precision, recall, and F1;
- root-pair precision, recall, and F1 (whether two records share a root);
- absolute root-count error per case;
- content-truth accuracy and Brier score where an externally supplied truth
  label exists;
- majority, declared-collapse, and inferred-collapse accuracy;
- **declared advantage survival**:
  `(inferred_accuracy - majority_accuracy) /
  (declared_accuracy - majority_accuracy)` when the denominator is positive;
- coverage and abstention for every method; and
- runtime, reported descriptively.

Undefined survival ratios remain undefined; they are never replaced by zero.
Bootstrap 95% intervals use cases as clusters, seed `20260808`, and 10,000
resamples.

## Primary pilot hypothesis

The primary confirmatory stratum is `constructed_exact`, using a held-out
multi-agent echo corpus whose generation log fixes model family, retrieval
source set, prompt, sampling parameters, and allowed cross-agent context.

- **Null:** at 40% hidden edges, inferred collapse preserves no more than 25%
  of the declared-lineage accuracy advantage over majority, or its root-pair
  F1 is below 0.60.
- **Success:** at 40% hidden edges, the lower case-bootstrap 95% bound for
  declared advantage survival exceeds 0.25 and root-pair F1 is at least 0.60.
- **Failure:** either condition fails, fewer than 30 confirmatory questions are
  successfully generated, labels leak into inference features, or generation
  logs are incomplete.

The local deterministic fixture used to test software mechanics is not the LLM
corpus and cannot satisfy this hypothesis.

## Secondary hypotheses

Each real-world dataset receives its own result and cannot rescue the primary:

- explicit-edge parent recovery stays above F1 0.50 through 40% edge hiding;
- inherited rare mutations improve root-pair F1 by at least 0.05 over the
  no-mutation ablation in MemeTracker;
- timestamp-and-text reconstruction identifies the documented source loop in
  at least 70% of eligible adjudicated citogenesis cases;
- inferred collapse improves truth accuracy over majority without more than a
  one-percentage-point loss where majority is already correct.

The retraction-context and prediction-market labels are `heuristic_proxy` in
this pilot. They receive descriptive estimates only.

## Multiple comparisons and synthesis

No single pooled “all datasets” p-value is reported. The synthesis ranks
datasets by label strength, root-recovery performance, collapse fraction, and
failure mode. Secondary confidence intervals are descriptive and accompanied
by all attempted datasets, including null, adverse, inaccessible, and
underpowered results.

## Integrity and stopping rules

- Commit this protocol before executing any LIR-1 outcome runner.
- Record source URL, retrieval time, response headers where available, license,
  raw-byte SHA-256, parser version, exclusions, and row counts.
- Preserve raw inputs outside Git when redistribution is disallowed; commit a
  content manifest and exact retrieval instructions.
- Never silently substitute a dataset, label, model, threshold, or sample.
- Deviations go in `DEVIATIONS.md`; failures and blocked sources go in
  `MISTAKES.md`.
- A blocked dataset does not block the run. It is reported and the next
  eligible dataset continues.
- Two clean executions must produce byte-identical scientific JSON before a
  canonical result may be proposed. Timing files are separate.

## Interpretation

Success would show that a specified inference method recovers a measurable
fraction of known or recorded ancestry under specified perturbations. It would
not show that inferred similarity proves causal independence or that Minority
Prophet is a general truth engine. Failure would locate the boundary at which
declared-lineage guarantees stop transferring to inferred lineage.

