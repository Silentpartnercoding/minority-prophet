# Provenance primitives

This package implements the recorded evidence graph and root-issuance reference
used by Minority Prophet.

- [`graph.py`](graph.py) — append-only evidence DAG, ancestry traversal, and
  side/proposition consistency checks.
- [`root_registry.py`](root_registry.py) — bounded, authenticated root issuance
  reference with durable receipts.
- [`decision_relative.py`](decision_relative.py) — explicit decision-relative
  cut assessment.
- [`ROOT-IDENTITY.md`](ROOT-IDENTITY.md) — root identity assumptions and trust
  boundary.
- JSON Schemas define evidence lineage, claim warrants, and decision context.

The implementation validates recorded structure. It cannot prove that two
declared roots are causally independent or recover ancestry that was never
recorded. Read [`PROVENANCE-REQUIREMENTS.md`](../PROVENANCE-REQUIREMENTS.md) and
[`formal/CLAIM-SCOPE.md`](../formal/CLAIM-SCOPE.md) for the exact boundary.
