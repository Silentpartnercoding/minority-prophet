"""AID-1 arms. Named in AID-1-DESIGN-DRAFT.md before this world existed."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from itertools import combinations
from typing import Any

from aggregation.attested_independence import Use, Witness, effective_witnesses_for, independent_for
from aggregation.independence_axes import WitnessDepth
from canon.independent_set import maximum_independent_set_size
from canon.proximity import ErrorClass, Rung, Source
from canon.proximity import effective_witnesses_for as ladder_count
from experiments.aid1.world import (
    ABSTAIN,
    SETTLED_FALSE,
    SETTLED_TRUE,
    Decision,
    RealizedWitness,
    error_class,
)

ARMS = (
    "ladder",
    "attested",
    "attested_declared_only",
    "refuse_all_unrecorded",
)
PRIMARY = "attested"
BASELINE = "ladder"
THEATRE = "attested_declared_only"
CEILING = "refuse_all_unrecorded"


def declared_only_independent_for(a: Witness, b: Witness, error: ErrorClass) -> bool:
    """The named failure mode: honour declared depth, ignore backing.

    Copied from the policy's control flow, with `claimed` in place of
    `admissible`. If this arm matches `attested` on the freely-attesting
    family, the backing machinery is theatre.
    """
    if a.markers & b.markers:
        return False
    if a.claimed is WitnessDepth.UNSTATED or b.claimed is WitnessDepth.UNSTATED:
        return False
    if not (a.ancestry & b.ancestry) and a.ancestry_complete and b.ancestry_complete:
        return True
    return Rung(max(int(a.claimed), int(b.claimed))) <= error


def _side(witnesses: Iterable[RealizedWitness], side: bool) -> list[Witness]:
    return [item.witness for item in witnesses if item.vote is side]


def _ladder_count(items: list[Witness], error: ErrorClass) -> int:
    if not items:
        return 0
    sources = [Source(w.name, Rung.TEXT, w.ancestry, w.markers) for w in items]
    return ladder_count(sources, error)


def _declared_only_count(items: list[Witness], error: ErrorClass) -> int:
    if not items:
        return 0
    return maximum_independent_set_size(
        items, lambda a, b: not declared_only_independent_for(a, b, error)
    )


def _any_unrecorded_pair(items: Iterable[Witness]) -> bool:
    frozen = list(items)
    return any(not (a.ancestry & b.ancestry) for a, b in combinations(frozen, 2))


def n_eff(arm: str, items: list[Witness], error: ErrorClass) -> int:
    if arm == "ladder":
        return _ladder_count(items, error)
    if arm == "attested":
        if not items:
            return 0
        return effective_witnesses_for(items, error, use=Use.PERMIT_ACTION)
    if arm == "attested_declared_only":
        return _declared_only_count(items, error)
    raise ValueError(f"count not defined for {arm}")


def settle(arm: str, decision: Decision, error: ErrorClass) -> str:
    items = [item.witness for item in decision.witnesses]
    if arm == "refuse_all_unrecorded":
        if _any_unrecorded_pair(items):
            return ABSTAIN
        arm = "ladder"
    n_true = n_eff(arm, _side(decision.witnesses, True), error)
    n_false = n_eff(arm, _side(decision.witnesses, False), error)
    if n_true >= decision.threshold and n_true > n_false:
        return SETTLED_TRUE
    if n_false >= decision.threshold and n_false > n_true:
        return SETTLED_FALSE
    return ABSTAIN


def settle_over_units(decision: Decision, unit_of: Mapping[str, str]) -> str:
    """Reference-style settlement after an imposed grouping."""
    true_units = {unit_of[item.source_id] for item in decision.witnesses if item.vote}
    false_units = {unit_of[item.source_id] for item in decision.witnesses if not item.vote}
    n_true, n_false = len(true_units), len(false_units)
    if n_true >= decision.threshold and n_true > n_false:
        return SETTLED_TRUE
    if n_false >= decision.threshold and n_false > n_true:
        return SETTLED_FALSE
    return ABSTAIN


def is_pivotal(decision: Decision, focus: tuple[str, ...]) -> bool:
    """True when collapsing the focus group would move the ladder settlement."""
    if not focus:
        return False
    ladder = settle("ladder", decision, ErrorClass.FABRICATION)
    if ladder == ABSTAIN:
        return False
    units = {item.source_id: item.unit for item in decision.witnesses}
    shared = "focus:collapsed"
    collapsed = {sid: (shared if sid in focus else unit) for sid, unit in units.items()}
    return settle_over_units(decision, collapsed) != ladder


def run_decision(arm: str, decision: Decision, config: Mapping[str, Any]) -> str:
    return settle(arm, decision, error_class(config))


def policy_grants_pair(left: Witness, right: Witness, error: ErrorClass) -> bool:
    return independent_for(left, right, error)
