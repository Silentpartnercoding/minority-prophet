"""AID-2 arms. All five are named in AID-2-DESIGN-DRAFT.md section 3.

Every arm answers the same question the same way: count each side's witnesses
against the decision's error class, then settle by
`provenance.dependence_robustness.settle_counts`. The arms differ only in what
they hand that function, so nothing but the instrument under test varies.

- `ladder` — `canon.proximity.independent_for`, unchanged. An unstated claim is
  placed at `TEXT`, the bottom rung, because the legacy ladder has no `UNSTATED`
  and a witness that says nothing has always been read as hearsay. That default
  is the thing the policy refuses to make, so the baseline must make it. This
  arm reads the *claimed* depth: the ladder has no backing test.
- `attested_bounds` — **the primary**. `witness_bounds` for each side, the
  settlement evaluated at the lower end and at the upper end, and settled only
  when both ends give the same disposition. Otherwise refuse and escalate. This
  is section 2 of the spec, implemented to its letter, including the part of its
  letter that is a defect: see `range_settlements` below.
- `attested_point` — the same repaired policy through `effective_witnesses_for`
  with `Use.PERMIT_ACTION`, a single count. It differs from the primary in
  exactly one thing — a number where the primary has a range — so the gap
  between them is what the range buys.
- `attested_declared_only` — the primary with backing neutralised, by setting
  each witness's backing to `DEVICE_ATTESTED` / `BONDED`, which makes
  `admissible_depth` return the claim itself. It is the *bounds* rule, not the
  point rule: the theatre check must differ from the primary in backing alone,
  or criterion 3 confounds "the backing machinery does nothing" with "the range
  does nothing". Computed by the policy's own code rather than by a
  reimplementation of it, so a null result here is a statement about the backing
  machinery and not about a copy of it.
- `refuse_all_unrecorded` — refuse whenever any pair lacks recorded ancestry,
  exactly as the spec words it. In this world almost no pair shares recorded
  ancestry, so this arm refuses almost everything; that is what makes it an
  upper bound on cost, and criterion 4 was repaired in advance precisely because
  of it.

**On `range_settlements`.** The spec's rule consults two points: (lower, lower)
and (upper, upper). The set of settlements the range actually permits is the
whole box `[t_lower, t_upper] x [f_lower, f_upper]`, and the two diagonal corners
the rule reads are not the corners that bound it. `settle_counts` is monotone in
each side's count, so the box is bounded by the *anti*-diagonal corners —
(t_upper, f_lower) and (t_lower, f_upper) — which is the argument
`provenance/dependence_robustness.py` already makes over its own root ranges.
`range_settlements` reproduces that argument over a pair of `WitnessBounds`, and
is used for a reported diagnostic only. It is **not** substituted for the rule
the spec named. Exposing the gap is the world's job; closing it is not.
"""

from __future__ import annotations

import dataclasses
import itertools
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from aggregation.attested_independence import ScopeViolation, Use, Witness
from aggregation.attested_independence import effective_witnesses_for as attested_effective
from aggregation.attested_independence import witness_bounds
from aggregation.independence_axes import DepthBasis, WitnessBounds, WitnessIdentity
from canon.independent_set import DEFAULT_BUDGET
from canon.proximity import ErrorClass, Rung, Source
from canon.proximity import effective_witnesses_for as ladder_effective
from experiments.aid2run.world import Campaign, Decision
from provenance.dependence_robustness import (
    SETTLED_FALSE,
    SETTLED_TRUE,
    UNSETTLED,
    settle_counts,
)

ARMS = (
    "ladder",
    "attested_bounds",
    "attested_point",
    "attested_declared_only",
    "refuse_all_unrecorded",
)
BASELINE = "ladder"
PRIMARY = "attested_bounds"
POINT = "attested_point"
THEATRE = "attested_declared_only"
REFUSE = "refuse_all_unrecorded"

#: The arms that answer by consulting the range rather than a single count.
RANGE_ARMS = (PRIMARY, THEATRE)


@dataclasses.dataclass(frozen=True)
class Outcome:
    """What an arm did with one decision, and — for a range arm — how it got there."""

    terminal: str
    true_bounds: tuple[int, int] | None = None
    false_bounds: tuple[int, int] | None = None
    lower_terminal: str | None = None
    upper_terminal: str | None = None
    reachable: tuple[str, ...] | None = None
    """Every settlement the range permits, by the monotone corner argument.
    `None` for arms that do not compute a range."""

    @property
    def consulted_a_range(self) -> bool:
        return self.true_bounds is not None

    @property
    def ends_disagreed(self) -> bool:
        """The rule refused because its two ends gave different dispositions."""
        return (
            self.consulted_a_range
            and self.lower_terminal != self.upper_terminal
        )

    @property
    def range_is_wide(self) -> bool:
        """At least one side's count is not pinned by the record."""
        if not self.consulted_a_range:
            return False
        return (
            self.true_bounds[0] != self.true_bounds[1]
            or self.false_bounds[0] != self.false_bounds[1]
        )

    @property
    def ends_agree_interior_does_not(self) -> bool:
        """The two ends agreed on a settlement the range does not determine.

        The defect in the rule as specified, counted rather than corrected.
        """
        if not self.consulted_a_range or self.ends_disagreed:
            return False
        return len(self.reachable or ()) > 1


def ladder_source(witness: Witness) -> Source:
    """The ladder's view: the depth the witness *claimed*, with no backing test."""
    return Source(
        witness.name,
        Rung(min(int(witness.claimed), int(Rung.TEXT))),
        witness.ancestry,
        witness.markers,
    )


def at_face_value(witness: Witness) -> Witness:
    """The same witness with its declaration honoured whatever backs it.

    `admissible_depth(claimed, DEVICE_ATTESTED, BONDED)` is `claimed`, so this is
    the policy with `admissible_depth` neutralised and nothing else changed. An
    `UNSTATED` claim stays `UNSTATED`: honouring a declaration is not inventing
    one.
    """
    return dataclasses.replace(
        witness, depth_basis=DepthBasis.DEVICE_ATTESTED, identity=WitnessIdentity.BONDED
    )


def sides(
    campaign: Campaign, decision: Decision
) -> tuple[tuple[Witness, ...], tuple[Witness, ...]]:
    by_name = {w.name: w for w in campaign.witnesses}
    values = dict(decision.values)
    true_side = tuple(by_name[name] for name in sorted(values) if values[name])
    false_side = tuple(by_name[name] for name in sorted(values) if not values[name])
    return true_side, false_side


def every_pair_shares_ancestry(witnesses: Sequence[Witness]) -> bool:
    return all(
        bool(left.ancestry & right.ancestry)
        for left, right in itertools.combinations(witnesses, 2)
    )


def range_settlements(
    true_bounds: WitnessBounds, false_bounds: WitnessBounds, threshold: int
) -> frozenset[str]:
    """Every settlement reachable inside both ranges. Diagnostic, never the rule.

    The same corner argument `assess_dependence_robustness` makes over its own
    root ranges: `settle_counts` is monotone in each side's count, so `true` is
    reachable exactly when the true side at its most against the false side at
    its fewest settles true, and symmetrically; and any box that is neither
    wholly true nor wholly false contains a tie.
    """
    most_true = settle_counts(true_bounds.upper, false_bounds.lower, threshold)
    most_false = settle_counts(true_bounds.lower, false_bounds.upper, threshold)
    reachable: set[str] = set()
    if most_true == SETTLED_TRUE:
        reachable.add(SETTLED_TRUE)
    if most_false == SETTLED_FALSE:
        reachable.add(SETTLED_FALSE)
    if most_false != SETTLED_TRUE and most_true != SETTLED_FALSE:
        reachable.add(UNSETTLED)
    return frozenset(reachable)


def bounds_for(
    arm: str, witnesses: Sequence[Witness], error: ErrorClass, budget: int
) -> WitnessBounds:
    """The policy's range for one side, under the arm's view of the witnesses."""
    if arm == PRIMARY:
        return witness_bounds(witnesses, error, budget=budget)
    if arm == THEATRE:
        return witness_bounds(
            tuple(at_face_value(w) for w in witnesses), error, budget=budget
        )
    raise ValueError(f"{arm} does not consult a range")


def effective(
    arm: str, witnesses: Sequence[Witness], error: ErrorClass, budget: int = DEFAULT_BUDGET
) -> int:
    """The single count, for the arms that ask for one."""
    if arm in (BASELINE, REFUSE):
        return ladder_effective(
            tuple(ladder_source(w) for w in witnesses), error, budget=budget
        )
    if arm == POINT:
        return attested_effective(witnesses, error, use=Use.PERMIT_ACTION, budget=budget)
    raise ValueError(f"{arm} does not answer with a point estimate")


def settle_decision(
    arm: str,
    campaign: Campaign,
    decision: Decision,
    error: ErrorClass,
    budget: int = DEFAULT_BUDGET,
) -> Outcome:
    true_side, false_side = sides(campaign, decision)
    if arm == REFUSE and not every_pair_shares_ancestry(campaign.witnesses):
        return Outcome(UNSETTLED)
    if arm in RANGE_ARMS:
        true_bounds = bounds_for(arm, true_side, error, budget)
        false_bounds = bounds_for(arm, false_side, error, budget)
        lower = settle_counts(true_bounds.lower, false_bounds.lower, decision.threshold)
        upper = settle_counts(true_bounds.upper, false_bounds.upper, decision.threshold)
        # Settle only if both ends give the same disposition; otherwise the
        # evidence does not determine the decision. Refuse and escalate rather
        # than picking the end that suits.
        terminal = lower if lower == upper else UNSETTLED
        return Outcome(
            terminal=terminal,
            true_bounds=(true_bounds.lower, true_bounds.upper),
            false_bounds=(false_bounds.lower, false_bounds.upper),
            lower_terminal=lower,
            upper_terminal=upper,
            reachable=tuple(sorted(range_settlements(true_bounds, false_bounds,
                                                     decision.threshold))),
        )
    n_true = effective(arm, true_side, error, budget)
    n_false = effective(arm, false_side, error, budget)
    return Outcome(settle_counts(n_true, n_false, decision.threshold))


def run_campaign(
    arm: str, campaign: Campaign, error: ErrorClass, config: Mapping[str, Any]
) -> list[Outcome]:
    budget = int(config.get("counting_budget", DEFAULT_BUDGET))
    return [
        settle_decision(arm, campaign, decision, error, budget)
        for decision in campaign.decisions
    ]


def survival_call_is_refused(witnesses: Iterable[Witness], error: ErrorClass) -> bool:
    """Does the point policy refuse a count that decides whether a claim survives?

    It does -- when the caller says that is what it is doing. AID-1 measured why
    that is worth nothing: the use is caller-declared and nothing in a record
    distinguishes the two, so a caller settling whether to act declares
    `PERMIT_ACTION` truthfully while the same count deletes a claim. Kept so the
    successor world can show the guard is still there and still powerless.
    """
    try:
        attested_effective(witnesses, error, use=Use.DECIDE_SURVIVAL)
    except ScopeViolation:
        return True
    return False


__all__ = [
    "ARMS",
    "BASELINE",
    "POINT",
    "PRIMARY",
    "RANGE_ARMS",
    "REFUSE",
    "THEATRE",
    "Outcome",
    "at_face_value",
    "bounds_for",
    "effective",
    "every_pair_shares_ancestry",
    "ladder_source",
    "range_settlements",
    "run_campaign",
    "settle_decision",
    "sides",
    "survival_call_is_refused",
]
