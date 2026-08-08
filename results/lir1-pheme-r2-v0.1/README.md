# LIR-1 PHEME-R2 disjoint holdout

**Status:** confirmatory execution complete; registered criterion rejected.

This holdout excludes all 317 cases touched by the first PHEME pilot. It
contains 290 different complete cases, 5,000 claims, 4,693 recorded edges, and
307 recorded platform roots. One incomplete thread was excluded before the cap
was filled. Raw and normalized tweet text remains local.

The execution used the corrected hidden-edge metric and frozen threshold 0.40.
No R2 outcome was inspected before the inventory and runner were committed.

At 40% hidden edges:

- hidden-parent F1: `0.1043932144` (case-bootstrap 95% interval
  `0.0846273292–0.1260803254`);
- root-pair precision: `0.9990288905`;
- root-pair recall: `0.2255733895`;
- root-pair F1: `0.3680449346`; and
- root-count mean absolute error: `4.9310344828` roots per case.

The registered hidden-parent F1 criterion of greater than 0.50 is rejected.
The asymmetric root result is operationally important: the baseline almost
never joins different recorded roots, but frequently fragments one recorded
root into several predicted roots. If those fragments were counted as
independent evidence, copying would regain evidential mass.

Root-pair F1 falls below 0.50 between the registered 25% and 40% hidden-edge
levels. This is a bracketed empirical collapse region for this corpus and
method, not a universal threshold.
