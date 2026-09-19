# Aggregation methods

<!-- mp-status: {"id":"aggregation-index","class":"current","asOf":"2026-09-19","replacement":null,"immutable":false,"theorems":["DR1","DR2","DR3"],"researchRecords":["AID-1-V1","AID-2-V1","AID-3-V1","AID-4-V1"],"describesMechanisms":["recorded_graph_roots","recorded_dependence_robust_settlement","attested_independence_point_policy","attested_independence_bounds_policy","collapse_robust_margin_policy","priced_exposure_policy"],"recommendedMechanisms":["recorded_graph_roots","recorded_dependence_robust_settlement"]} -->

This package contains transparent reference methods. They do not share one
maturity or claim status.

- [`baselines.py`](baselines.py) — agent-count majority and declared
  confidence/competence weighting.
- [`root_vote.py`](root_vote.py) — guarded root-aware verdict used by new work;
  its correspondence to the formal model is documented in the module.
- [`semantic.py`](semantic.py) — finite semantic experiments, including a frozen
  historical implementation bound into EXPERIMENT-001.
- [`markets.py`](markets.py) — provider-neutral aggregation of public binary
  market behavior.
- [`attested_independence.py`](attested_independence.py) — hash-pinned research
  implementation for the rejected AID-1 through AID-4 policies. It is preserved
  so the canonical results remain reproducible; it is not a recommended package
  method. Current status:
  [`ATTESTED-INDEPENDENCE-SERIES-CLOSURE.md`](../experiments/ATTESTED-INDEPENDENCE-SERIES-CLOSURE.md).

Read [`formal/CLAIM-SCOPE.md`](../formal/CLAIM-SCOPE.md) before describing any
implementation as proved. Run the related tests through `make verify-python`.
