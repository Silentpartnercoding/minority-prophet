"""KL-005 — the two-sided metric, built before any data.

The blocker this discharges: "a single-endpoint design would let indefinite
abstention win; the two-sided metric is the prerequisite, not a refinement."

A one-sided false-confirmation rate is minimised by a system that never
confirms anything. That system is useless and scores perfectly, which makes the
metric single-valued in the direction that matters. The fix is not a weighting
tweak; it is a second term that only a system which eventually confirms true
events can score well on.

No inference, no randomness. Every function is total.
"""

from __future__ import annotations

from dataclasses import dataclass

# A system that never confirms must not be able to score well by waiting. The
# horizon is the deadline past which a true event is treated as never confirmed.
HORIZON = 30  # days


@dataclass(frozen=True)
class Judgement:
    """One system's verdict on one event."""
    event_id: str
    confirmed_at: int | None  # day index, or None for never confirmed


@dataclass(frozen=True)
class Event:
    event_id: str
    is_true: bool
    # Day the first genuinely independent original report existed. None if the
    # event is false, since no such report can exist.
    independently_reportable_at: int | None


def false_confirmations(events, judgements) -> int:
    """One-sided endpoint: how many false events did the system confirm?"""
    truth = {e.event_id: e.is_true for e in events}
    return sum(1 for j in judgements if j.confirmed_at is not None and not truth[j.event_id])


def one_sided_score(events, judgements) -> float:
    """Lower is better. THIS IS THE BROKEN METRIC, kept so the defect is
    demonstrable rather than asserted."""
    false_events = sum(1 for e in events if not e.is_true)
    if false_events == 0:
        return 0.0
    return false_confirmations(events, judgements) / false_events


def delay_cost(events, judgements) -> float:
    """Second side: total normalised lateness in confirming TRUE events.

    A true event never confirmed costs a full horizon. This is the term that
    makes silence expensive.
    """
    by_id = {e.event_id: e for e in events}
    total = 0.0
    true_events = [e for e in events if e.is_true]
    if not true_events:
        return 0.0
    for j in judgements:
        e = by_id[j.event_id]
        if not e.is_true:
            continue
        earliest = e.independently_reportable_at or 0
        if j.confirmed_at is None:
            total += 1.0
        else:
            late = max(0, j.confirmed_at - earliest)
            total += min(late, HORIZON) / HORIZON
    return total / len(true_events)


def two_sided_score(events, judgements, w_false: float = 1.0, w_delay: float = 1.0) -> float:
    """Lower is better. Both weights are declared, not fitted.

    Equal weights are a deliberate choice, not a tuned optimum: any weighting
    that lets one term dominate reintroduces the single-endpoint defect in the
    other direction.
    """
    return (w_false * one_sided_score(events, judgements)
            + w_delay * delay_cost(events, judgements))
