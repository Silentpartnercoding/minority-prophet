# Capability Tournament v1 — adversarial validity review

Status: public claim-boundary review

Reviewed: 2026-08-11

Review lane: routine documentation and presentation hardening after the frozen
result; no protocol, packet, score, or recorded outcome was changed.

## Outsider's strongest fair criticism

The result can be misread as a 128-trial scientific demonstration that Minority
Prophet improves models. It is not. It is an eight-case conformance exercise in
which every lane receives complete, truthful lineage and the canonical lane is
deterministic code. Its strongest defensible result is narrower: the pinned code
exactly executed its own declared distinct-root rule on the frozen packets, while
the sampled model runs did so inconsistently.

## What was legitimately controlled

- The public packet bytes were identical across the local A, B, C, and fixed
  method lanes.
- The protocol, manifest, canonical implementation, scoring rule, and failure
  handling were frozen and content-bound before the recorded executions.
- No contestant received the hidden reference, a precomputed root map, root
  count, or canonical answer.
- Failures and workspace-boundary violations remain visible; raw Claude answers
  were preserved separately from protocol scores.
- The Claude extension was labeled as an extension rather than silently pooled
  into the initial model grid.

Those controls make the result inspectable and reproducible. They do not create
external validity or causal evidence of Minority Prophet lift.

## Threats to validity

### 1. Construct validity

The reference answer is the distinct-origin rule used by the canonical method.
A perfect C score therefore demonstrates implementation conformance to a known
rule. It is not independent validation that the rule discovers truth.

### 2. Wrong conditions for the lift hypothesis

Tournament A and B both receive complete lineage. B adds optional tools, not
provenance. Tournament C replaces the model with deterministic code. Therefore:

- A-to-B is not provenance gain;
- B-to-C is not Minority Prophet gain;
- C-to-A is not total epistemic gain; and
- the tournament does not test H1, H2, or H3.

The required lift study must hold the model and world fixed while changing only
the available epistemic information.

### 3. Pseudoreplication

There are eight generated packets. Each contains 16 related propositions, so
128 dispositions are scored, but the dispositions inside a packet share the
same generated case and execution. Treating all 128 as independent trials would
overstate precision. The case is the appropriate replication unit here.

### 4. No variance estimate

Each model and lane has one clean replicate. There are no repeated seeds,
confidence intervals, paired tests, or multiplicity controls for model or lane
comparisons. The table is descriptive and cannot establish a stable ranking.

### 5. Favorable provenance assumption

Parent links are complete, acyclic, truthful, and semantically sufficient by
construction. The exercise excludes missing edges, forged lineage, colluding
roots, stale evidence, root compromise, circular fabrication, and ambiguity
about whether two roots are actually controlled independently.

### 6. Provider and execution comparability

Hosted aliases may change. The model lanes use subscription-backed CLIs while C
uses local deterministic code. Wall time includes different provider, harness,
and network paths. Cost figures use different telemetry sources. Time and cost
are useful run records, not controlled provider benchmarks or production
forecasts.

### 7. Tool-lane ambiguity

Lane B means tools were available. Models chose different tools—or none—and the
Claude protocol scores also include workspace-compliance penalties. B therefore
does not isolate a single intervention called “tool use.” Raw accuracy and
protocol compliance must remain separate.

### 8. Public-set contamination

The packet, protocol, and results are public. They are suitable for development,
audit, and reproduction, but not for a future hidden evaluation of memorization-
resistant model performance. Any confirmatory leaderboard needs held-out and
rotating worlds.

### 9. Shared control

Repository authors, runners, reviewers, and this adversarial review remain
within the owner's control domain unless supported external provenance shows
otherwise. Internal cross-review improves quality; it is not independent
validation.

## Claims that survive the attack

The public result may say:

1. On one frozen eight-case complete-lineage packet, the pinned canonical
   implementation matched all 128 within-case reference dispositions.
2. The sampled AI runs often selected rules other than exact distinct-origin
   counting, especially on thin margins and ties.
3. Tool availability did not reliably force the model to choose the frozen
   invariant.
4. The protocol, failures, raw results, telemetry, and limitations are publicly
   inspectable.

It must not say or imply:

- Minority Prophet improved the same model by a measured amount;
- 128 independent trials support statistical certainty;
- Minority Prophet discovered real-world truth or independent roots;
- one provider or model is stably better than another;
- the observed time or price ratio predicts production scaling; or
- this study proves H1, H2, or H3.

## What would falsify the bounded result

The conformance claim fails if a clean reproduction on the bound packet and
pinned implementation produces a different canonical disposition, if the
manifest or implementation hashes do not match, if hidden reference data entered
the canonical input, or if the published table cannot be reconstructed from the
preserved records under the frozen scorer.

The broader Minority Prophet hypothesis should be considered unsupported—or
rejected if a powered study shows no benefit—when a separately frozen,
same-model A/B/C experiment finds no reproducible B-to-C improvement under its
predeclared metric.

## Required next study

For every model, world, and seed:

1. A receives claims only.
2. B receives the exact A content plus complete provenance and no MP score.
3. C receives the exact B content plus a canonical, non-answer-leaking Minority
   Prophet analysis.

The study should use immutable worlds across conditions, repeated seeds,
case-level paired analysis, confidence intervals, contamination-resistant held-
out worlds, complete response and provider metadata, and adversarial conditions
with incomplete or misleading provenance. Standalone deterministic C should
remain a conformance control, not replace the same-model augmented condition.
