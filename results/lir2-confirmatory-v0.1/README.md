# LIR-2 confirmatory result

The precision-constrained root grouper **supported all five preregistered
conditions** on the new 36-case holdout.

At 40% hidden edges, root-pair precision was `1.0`, recall was `0.9522`, and F1
was `0.9755`. Inferred collapse answered 34 of 36 cases and was correct on all
34, for coverage and all-case correct yield of `0.9444`. It abstained twice.

On the same new cases, the frozen LIR-1E parent baseline answered 29 and was
correct on 25. LIR-2 therefore supplied nine more correct answers, reduced
abstentions from seven to two, and introduced no wrong answer in this
constructed holdout.

This supports the narrower design insight that root grouping should be treated
as its own task rather than forced through exact-parent reconstruction. It does
not prove causal evidence independence, authentication, general truth recovery,
or performance on uncontrolled real-world records.
