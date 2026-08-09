# LIR-4 — provenance degradation envelope

**Status:** attack rules, final-unused-holdout selection, metrics, and decision
criteria frozen before the holdout is materialized or scored.

## Question

LIR-3 perfectly reconstructed recorded PHEME reply components when 40% of exact
parent edges were hidden but reply-target author identity remained observable.
How much of that identity can disappear before reconstruction fails, how does
identity collision change the result, and can deliberately wrong identity cause
unsafe cross-root merges?

## Corpus and boundary

Use PHEME rumor cases unused by LIR-1/PHEME pilot, PHEME-R2, and both LIR-3
splits. Sort whole cases by SHA-256 of
`minority-prophet-lir4-degradation-holdout-v1|<case-id>` and admit them until
the next case would exceed 5,000 claims. Reject missing-file cases whole.

The target remains the recorded PHEME reply-tree root. It is not causal evidence
ancestry, evidential independence, content truth, or a common real-world source.
This is a new case holdout within a previously studied corpus family, not an
independent-dataset transfer.

## Frozen method and edge perturbation

Use the LIR-3 selected configuration unchanged:
`author-0.00-margin-0.00-fallback-none`. Hide 40% of exact parent edges using
the existing deterministic LIR perturbation. Do not retune, exclude cases after
scoring, or add text, mention, URL, or hashtag fallback.

## Registered identity attacks

1. **Missingness curve:** independently remove reply-target author identity from
   deterministically nested fractions `0, 0.25, 0.50, 0.75, 1.0` of records
   whose exact parent edge was hidden. Ordinary roots and exposed edges are not
   modified.
2. **Collision curve:** replace every author and reply-target author within each
   case by a deterministic hash bucket at `32, 16, 8, 4, 2, 1` buckets. This
   preserves a coarse identity link while making distinct authors ambiguous.
3. **White-box misbinding:** for every hidden-edge record with an earlier author
   from a different true recorded root in the same case, replace the target
   author with the cross-root candidate receiving the highest frozen LIR-3
   provenance score. This attack may use labels to construct the challenge;
   inference never sees them. Report the number of eligible attacked records.

The missingness and collision attacks use only fixed salted hashes. No attack is
selected or changed in response to results.

## Metrics

For every condition report root-pair precision, recall, and F1 plus root-count
mean/max absolute error. The primary point is 50% missing reply identity among
hidden edges. Report 10,000 whole-case bootstrap intervals with seed `20260809`
for that point and its recall/F1 changes from intact LIR-3.

Separately report multi-root-case metrics for intact, one-bucket collision, and
white-box misbinding. These are the only cases capable of exposing a cross-root
false merge in PHEME's case structure.

## Joint primary criterion

All conditions must hold:

1. intact root precision and recall are each at least `0.99`;
2. at 50% missing identity, root precision is at least `0.99`;
3. at 50% missing identity, root recall is at least `0.65`;
4. at 50% missing identity, root F1 is at least `0.78`;
5. at 50% missing identity, root-count MAE is below `2.5`; and
6. complete identity removal lowers recall by at least `0.30` versus intact.

Condition 6 establishes that identity is load-bearing rather than a decorative
field. Failure of any condition rejects the joint graceful-degradation claim.

## Safety diagnostic

White-box misbinding is reported as a separate red-team result, not a rescue or
part of the primary success gate. Safe resistance requires multi-root precision
of at least `0.99`. If fewer than 20 multi-root cases or fewer than 20 eligible
misbindings exist, the safety diagnostic is explicitly underpowered and no
general resistance claim is permitted even if the point estimate passes.

## Interpretation

This experiment maps a failure boundary for one recorded-reply corpus. It does
not prove resilience to identity attacks on other platforms. A supported primary
claim plus failed misbinding safety would mean honest missingness degrades
gracefully while false provenance remains dangerous—a useful systems result,
not a contradiction.
