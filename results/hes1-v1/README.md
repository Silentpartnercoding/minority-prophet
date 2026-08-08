# HES-1 canonical result

HES-1 tested whether a dependency-aware verifier can seek one missing
independent evidence root after abstaining. Candidate selection was frozen from
provenance, availability, and cost before candidate values were inspected. The
decision threshold was not lowered, and dependent duplicates were null controls.

The preregistered primary claim was **supported**, with a material subgroup
limitation. All seven frozen hypotheses passed, but the pooled result must not be
read as evidence that every independent source is safe or useful.

## Environmental evidence

The nearest eligible independent EPA site recovered 85.05% of 214 negative-shift
abstentions and 88.98% of 2,531 positive-shift abstentions. Conditional recovery
accuracy was 72.53% and 97.11%, respectively. Recovered false-confident-error was
23.36% for negative shifts and 2.57% for positive shifts, compared with 100% for
the activated head-count trap by construction.

This is evidence that blind acquisition can restore substantial coverage, not
that geographic proximity guarantees correctness. The asymmetry between shift
directions is operationally important.

## Software evidence

Cppcheck recovered 71.05% of 38 software abstentions with 70.37% conditional
accuracy. The pooled recovered false-confident-error rate was 21.05%, with a wide
95% interval from 0% to 47.06%.

The pooled number hides a decisive limitation. On false-positive attacks,
recovered conditional accuracy was 100%. On stale replay it was 66.67%. On
false-negative attacks it was only 40%, and six of eleven unresolved cases became
wrong answers. Cppcheck therefore cannot be treated as a universally safe deciding
root. For negative software claims, the evidence policy needs a stricter stopping
rule, another genuinely independent root, or human review.

## Interpretation

HGD-2's brake can be turned into limited steering, but independence is necessary
and not sufficient. A new source may be structurally independent yet weak for the
particular claim direction. The next research target is claim-conditional evidence
qualification: preregister what each source is competent to establish, rather than
allowing one generic vote to decide both presence and absence.

Dependent duplicates changed no state or effective mass, already answered cases
triggered no query, and unknown evidence still escalated. Two executions at
implementation commit `7281e1571e4c52122286d94c0f4f99e792372318` produced
byte-identical scientific JSON. The result grants no authority, certifies no tool,
and does not discover hidden dependence.
