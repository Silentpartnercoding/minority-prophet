# HEO-1 — Evidence-origin independence across separate controllers

**Status: preregistered before implementation or confirmatory execution**

## Question

Can supported evidence-origin lineage prevent genuinely separate controllers
from multiplying one underlying observation into apparent independent evidence,
while retaining genuinely separate observations?

## Boundary

HVI-1 established control-domain independence, not causal evidence
independence. HEO-1 tests declared or externally supported evidence derivation
inside a synthetic model. It cannot discover an undisclosed common source,
prove causal evidence independence beyond the supported record, prove that a
root observation is true, or grant authority.

## Unit of independence

One supported origin observation is one evidence root. Copies, summaries,
translations, paraphrases, format conversions, and model-generated
transformations remain descendants of that root. Separate controllers do not
create new roots merely by receiving or transforming the same observation.

An asserted parent or origin is accepted only when bound by a supported
derivation receipt. Unknown, conflicting, revoked, cyclic, or gapped lineage
produces `ESCALATE`.

## Frozen model

- seeds `501–520` inclusive;
- `250` base worlds per seed;
- one binary proposition;
- six independent honest observations, correct with probability `0.85`;
- one adverse observation, correct with probability `0.25`;
- every controller is genuinely separate and HVI-1-valid; and
- stable identifiers derived from seed, world, and role.

Each base world yields matched variants preserving the underlying claims:

1. `single_origin` — one adverse observation;
2. `byte_copy_8` — eight byte-identical copies across eight controllers;
3. `paraphrase_8` — eight different bytes derived from the adverse root;
4. `translation_8` — eight translated representations derived from the root;
5. `summary_8` — eight summaries derived from the root;
6. `model_transform_8` — eight model transformations derived from the root;
7. `mixed_transform_32` — thirty-two mixed descendants of the root;
8. `unknown_origin_8` — eight claims with unsupported origin lineage;
9. `forged_parent_8` — eight claims asserting an unbound independent parent;
10. `genuine_origins_8` — eight separately captured root observations.

## Frozen comparators

1. receipt head count;
2. byte-digest deduplication;
3. controller-domain deduplication;
4. fixed token-Jaccard similarity clustering at `0.85`;
5. fixed embedding-free normalized-text clustering;
6. supported evidence-origin aggregation.

The evidence-origin method follows only supported derivation edges to an
origin, rejects cycles and gaps, and counts each surviving origin once. Binary
ties return `ABSTAIN`; uncertain lineage returns `ESCALATE`.

## Metrics and bootstrap

- false-independent-root acceptance;
- genuine-origin retention;
- decision error at matched abstention;
- abstention and escalation;
- root-mass change caused solely by transformation; and
- forged-parent acceptance.

World-clustered 95% bootstrap intervals use seed `20260808` and exactly
`10,000` resamples. Base worlds are the resampling unit.

## Frozen hypotheses

- **HEO-1a — transformation invariance:** every supported copy or transform
  variant changes evidence-origin root mass by exactly zero.
- **HEO-1b — uncertainty preservation:** all `unknown_origin_8` worlds escalate.
- **HEO-1c — forged-parent rejection:** no unbound asserted parent mints a root.
- **HEO-1d — genuine-origin retention:** at least 95% of supported separate
  observations in `genuine_origins_8` remain distinct.
- **HEO-1e — false-root reduction:** the upper bound of the paired bootstrap
  interval for evidence-origin false-root rate minus controller-domain
  false-root rate is at most `-0.80`.
- **HEO-1f — matched decision preservation:** at the evidence-origin method's
  answered worlds, the upper bound of its paired decision-error difference
  from the best non-oracle comparator is at most `0.02`.

The primary claim is supported only if HEO-1a through HEO-1f all hold. Null,
adverse, incomplete, and contradictory outcomes must remain public.

## Integrity controls

- No confirmatory world may be inspected before this protocol is public.
- Seeds, variants, thresholds, methods, and success rules cannot be tuned later.
- The implementation must record protocol/source hashes and environment.
- Two detached-worktree runs must produce byte-identical scientific JSON.
- Timings remain separate observational output.
