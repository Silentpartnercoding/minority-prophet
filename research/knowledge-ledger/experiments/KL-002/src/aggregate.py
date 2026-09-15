"""Confidence as a declared function of independent root count.

The function is stated here rather than tuned, so that the gate's result is a
property of the root rule and not of a fitted parameter.
"""

from __future__ import annotations


def confidence(independent_roots: int, per_root_accuracy: float = 0.7) -> float:
    """Naive-independence aggregation: 1 - (1-p)^k.

    This is the aggregator the experiment is about. It is correct exactly when
    the k roots are genuinely independent, and it is the thing that inflates
    when they are not. p is declared, not fitted.
    """
    if independent_roots < 0:
        raise ValueError("root count cannot be negative")
    return 1.0 - (1.0 - per_root_accuracy) ** independent_roots


def inflation_table(max_roots: int = 20, per_root_accuracy: float = 0.7) -> list[dict]:
    """Enumerate rather than sample. The mechanism is deterministic."""
    return [
        {"roots": k, "confidence": round(confidence(k, per_root_accuracy), 12)}
        for k in range(1, max_roots + 1)
    ]
