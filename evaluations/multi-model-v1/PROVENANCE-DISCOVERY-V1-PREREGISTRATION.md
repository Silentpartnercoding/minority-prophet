# Provenance Discovery v1 — preregistration

Status: **FROZEN DEMO protocol — commit before model execution**

## Purpose

The prior Epistemic Lift study supplied Condition B and Minority Prophet with explicit parent IDs, root-relevant metadata, control domains, observation IDs, and timestamps. It measured analysis of available provenance, not formation of provenance.

This separate development study removes the hidden ancestry keys. Each contestant receives only report text, document URL, publisher label, and timestamp. It must partition documents by shared underlying origin before deciding which answer has the most independently originating observations.

## Corpus

- 24 deterministic synthetic worlds; four each across explicit citation,
  syndication marker, distinctive-detail laundering, deceptive citation,
  generic boilerplate, and opaque paraphrase.
- Eleven documents per world: one false origin copied seven times and three independent truthful observations.
- Hidden evaluator state contains exact parent, root, and truth labels.
- Public packets contain none of: ground truth, asserted-answer fields, parent IDs, root IDs, direct/derived labels, control-domain IDs, or observation IDs.
- Opaque paraphrase deliberately contains no reliable observable lineage clue. A cautious system should not pretend otherwise.

## Contestants

- Candidate deterministic MP provenance former, version
  `mp-provenance-inference-candidate-v2`. It searches every temporally valid
  parent candidate but collapses only explicit same-assertion citations or
  high-entropy shared field details. Agreement on the conclusion alone never
  authorizes a collapse.
- A JavaScript comparator preserving the decision rule of EXP008's
  answer-agreement + time + citation heuristic. EXP008 originally operated on
  eight-answer vectors; its inclusion here tests whether that rule transfers
  safely to one-answer reports.
- GPT-5.6 Sol, medium effort, no tools or external retrieval.
- Claude Sonnet, medium effort, no tools or external retrieval.

The candidate provenance former is new experimental upstream code. It is not the previously validated MP evidence-analysis engine and must not be represented as an existing production capability.

## Scoring

Primary: macro mean pairwise same-origin F1. Every unordered document pair is classified as same origin or different origin. This is invariant to arbitrary group names and to choosing a grandparent instead of an immediate parent.

Also report pairwise precision, pairwise recall, inferred root-count error, downstream truth recovery, latency, tokens, parse failures, and provider-reported cost.

For the two information-insufficient families, abstention is the safe outcome;
truth recovery is not credited when ancestry is deliberately unobservable.

All worlds and failures remain in the denominator. No result will be published automatically.

## Interpretation boundary

This can show whether observable citations, syndication notices, or distinctive shared details permit useful provenance reconstruction in a controlled corpus. It cannot establish real-world accuracy, resolve deliberately unobservable copying, verify source ownership, or prove that semantic similarity implies common origin.
