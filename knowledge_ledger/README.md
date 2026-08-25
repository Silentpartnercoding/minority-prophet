# Knowledge-ledger reference code

This package contains deterministic evaluators for a declared search ledger and
evidence ledger. It is conformance-oriented reference code, not a truth engine.

- [`transaction.py`](transaction.py) is the frozen v0.1 evaluator bound by
  preregistered hashes.
- [`transaction_v2.py`](transaction_v2.py) adds explicit doubt, uncertainty, and
  abstention information without modifying the frozen evaluator.
- [`presentation.py`](presentation.py) handles presentation of transaction
  results.

The broader public method, conformance profile, findings, and experiments live
under [`research/knowledge-ledger/`](../research/knowledge-ledger/). A ledger
records the declared search and evidence state; it cannot prove hidden causal
independence.
