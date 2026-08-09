# Lineage-inference series closure

**Status:** LIR-1 through LIR-4 are complete. The series closes at recorded-root
reconstruction under typed provenance availability and degradation.

## Closed question

Can Minority Prophet infer enough lineage to avoid counting obvious copies as
independent evidence, and which observable information is load-bearing?

## Result chain

1. **Text and time were insufficient on recorded PHEME reply lineage.**
   LIR-1/PHEME-R2 rejected hidden-parent recovery, and the constructed LIR-2
   grouper did not transfer to PHEME.
2. **Controlled constructed recovery was possible but bounded.** LIR-1E
   recovered useful roots with material abstention; LIR-2 materially improved
   constructed root coverage on a fresh holdout.
3. **Typed counterpart identity bridged the recorded-lineage gap.** LIR-3 kept
   reply-target author identity while hiding exact parent-status IDs and
   perfectly recovered recorded roots on its sealed PHEME holdout.
4. **The bridge was load-bearing and brittle.** LIR-4 rejected graceful
   degradation: at 50% missing target identity, recall fell to `0.4329` while
   precision remained `1.0`.

## Defensible conclusion

Content similarity and timing cannot be presumed to recover real recorded
lineage. Typed provenance can be substantially more informative than content,
but missing provenance must produce explicit fragmentation or uncertainty—not
new independent roots. Recorded reply ancestry still does not establish causal
evidence ancestry, root authenticity, evidence independence, or truth.

## Why the series stops here

PHEME is exhausted as a clean source for the next claim. Its final holdout had
only one multi-root case, so it cannot power a general test of forged identity
causing false cross-root merges. Reusing more PHEME would add volume without
answering the missing scientific question.

Any LIR-5 must be separately preregistered and must use either a balanced
multi-root adversarial construction or a genuinely different platform with
strong lineage labels. It is a new chapter, not unfinished evidence from this
series.

## Canonical records

- `results/lir1-pheme-r2-v0.1/canonical-manifest.json`
- `results/lir1e-confirmatory-v0.1/canonical-manifest.json`
- `results/lir2-confirmatory-v0.1/canonical-manifest.json`
- `results/lir2-pheme-transfer-v0.1/canonical-manifest.json`
- `results/lir3-confirmatory-v0.1/canonical-manifest.json`
- `results/lir4-confirmatory-v0.1/canonical-manifest.json`
