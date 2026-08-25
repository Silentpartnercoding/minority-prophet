# Aggregation methods

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

Read [`formal/CLAIM-SCOPE.md`](../formal/CLAIM-SCOPE.md) before describing any
implementation as proved. Run the related tests through `make verify-python`.
