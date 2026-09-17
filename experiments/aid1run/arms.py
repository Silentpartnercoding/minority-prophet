"""AID-1 arms. All four are named in AID-1-DESIGN-DRAFT.md section 4.

Every arm answers the same question the same way: count each side's effective
witnesses against the decision's error class, then settle by
`provenance.dependence_robustness.settle_counts`. The arms differ only in which
independence relation feeds the count, so nothing but the policy under test
varies between them.

- `ladder` — `canon.proximity.independent_for`, unchanged. An unstated claim is
  placed at `TEXT`, the bottom rung, because the legacy ladder has no `UNSTATED`
  and a witness that says nothing has always been read as hearsay. That default
  is the thing the policy refuses to make, so the baseline must make it.
- `attested` — `aggregation.attested_independence.effective_witnesses_for` with
  `Use.PERMIT_ACTION`. The policy, unmodified.
- `attested_declared_only` — the same function on witnesses whose backing has
  been set to the strongest available (`DEVICE_ATTESTED`, `BONDED`), which makes
  `admissible_depth` return the claim itself. Declared depth at face value,
  computed by the policy's own code rather than by a reimplementation of it, so
  a null result here is a statement about the backing machinery and not about a
  copy of it.
- `refuse_all_unrecorded` — refuse whenever any pair lacks recorded ancestry,
  exactly as the spec words it. In this world almost no pair shares recorded
  ancestry, so this arm refuses almost everything; that is what makes it an
  upper bound on cost, and it is also why criterion 4 is a low bar. Said in the
  preregistration rather than fixed here.
"""

from __future__ import annotations

import dataclasses
import itertools
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from aggregation.attested_independence import ScopeViolation, Use, Witness
from aggregation.attested_independence import effective_witnesses_for as attested_effective
from aggregation.independence_axes import DepthBasis, WitnessIdentity
from canon.independent_set import DEFAULT_BUDGET
from canon.proximity import ErrorClass, Rung, Source
from canon.proximity import effective_witnesses_for as ladder_effective
from experiments.aid1run.world import Campaign, Decision
from provenance.dependence_robustness import settle_counts

ARMS = ("ladder", "attested", "attested_declared_only", "refuse_all_unrecorded")
BASELINE = "ladder"
POLICY = "attested"
THEATRE = "attested_declared_only"
REFUSE = "refuse_all_unrecorded"


@dataclasses.dataclass(frozen=True)
class Outcome:
    terminal: str
    effective_true: int
    effective_false: int


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


def effective(
    arm: str, witnesses: Sequence[Witness], error: ErrorClass, budget: int = DEFAULT_BUDGET
) -> int:
    if arm in (BASELINE, REFUSE):
        return ladder_effective(
            tuple(ladder_source(w) for w in witnesses), error, budget=budget
        )
    if arm == POLICY:
        return attested_effective(witnesses, error, use=Use.PERMIT_ACTION, budget=budget)
    if arm == THEATRE:
        return attested_effective(
            tuple(at_face_value(w) for w in witnesses),
            error,
            use=Use.PERMIT_ACTION,
            budget=budget,
        )
    raise ValueError(f"unknown arm {arm}")


def settle_decision(
    arm: str,
    campaign: Campaign,
    decision: Decision,
    error: ErrorClass,
    budget: int = DEFAULT_BUDGET,
) -> Outcome:
    true_side, false_side = sides(campaign, decision)
    if arm == REFUSE and not every_pair_shares_ancestry(campaign.witnesses):
        return Outcome("unsettled", 0, 0)
    n_true = effective(arm, true_side, error, budget)
    n_false = effective(arm, false_side, error, budget)
    return Outcome(settle_counts(n_true, n_false, decision.threshold), n_true, n_false)


def run_campaign(
    arm: str, campaign: Campaign, error: ErrorClass, config: Mapping[str, Any]
) -> list[Outcome]:
    budget = int(config.get("counting_budget", DEFAULT_BUDGET))
    return [
        settle_decision(arm, campaign, decision, error, budget)
        for decision in campaign.decisions
    ]


def survival_call_is_refused(witnesses: Iterable[Witness], error: ErrorClass) -> bool:
    """Does the policy refuse a count that decides whether a claim survives?

    It does -- when the caller says that is what it is doing. The minority family
    exists because nothing in a record distinguishes the two uses, and a caller
    settling a decision declares `PERMIT_ACTION` truthfully while the same count
    deletes a claim.
    """
    try:
        attested_effective(witnesses, error, use=Use.DECIDE_SURVIVAL)
    except ScopeViolation:
        return True
    return False


__all__ = [
    "ARMS",
    "BASELINE",
    "POLICY",
    "REFUSE",
    "THEATRE",
    "Outcome",
    "at_face_value",
    "effective",
    "every_pair_shares_ancestry",
    "ladder_source",
    "run_campaign",
    "settle_decision",
    "sides",
    "survival_call_is_refused",
]
