# LIR-3 confirmatory result

The preregistered observable-provenance bridge criterion is **supported** on the
sealed PHEME holdout.

At 40% hidden recorded edges across 425 previously unused cases (5,000 claims),
the frozen reply-target-author rule achieved root-pair precision `1.0`, recall
`1.0`, and F1 `1.0`, with root-count mean absolute error `0.0`. Frozen LIR-2 on
the same cases achieved precision `1.0`, recall `0.2534`, F1 `0.4043`, and
root-count MAE `3.9718`. The registered gains were `0.7466` recall and `0.5957`
F1; all six joint conditions passed.

## What the result means

PHEME retains the author targeted by a reply even when the experiment hides the
exact parent-status ID. Connecting a reply to an earlier record by that author
was sufficient to reconstruct every recorded reply component in this holdout.
The simpler author-only rule won development selection; mentions, URL domains,
hashtags, and free text were not needed as fallbacks.

This identifies a real and useful interface distinction: a system can conceal
an exact edge yet preserve enough typed provenance to recover the recorded
component. For a knowledge ledger, recording counterpart identity can therefore
be far more informative than retaining content similarity alone.

## What the result does not mean

The label is PHEME's recorded reply-tree root. A reply relationship is not proof
that one person copied another's evidence, that two people share a causal source,
that an author is independent, or that any statement is true. The corpus family
was previously studied, although these cases were unused and held out. Perfect
performance here therefore supports a narrow platform-lineage claim, not general
real-world provenance recovery.
