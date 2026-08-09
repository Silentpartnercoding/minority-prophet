# LIR-1 PHEME confirmatory attempt v0.1

**Verdict: invalid; no confirmatory result.**

The first execution scored all recorded edges rather than only the edges hidden
from the inference method. Visible edges therefore inflated the exact-parent
metric. The attempted output is retained under `superseded/` for auditability;
its `criterionSupported` field is void and must not be cited as a result.

See `experiments/lir1/DEVIATIONS.md` D1. The original confirmatory cases are no
longer untouched. A valid next claim requires corrected development selection
and a preregistered disjoint holdout.
