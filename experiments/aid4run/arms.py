"""AID-4 arms. All five were named in AID-4-DESIGN-DRAFT.md before this world.

None of these is my policy. Two of them are somebody else's proposals and this
file implements them as written, including the reading that makes them losable.

Where the draft left an operational choice, the choice is made here, stated
here, and stated again in `PREREGISTRATION.md` section 4 — never adjusted after
a number is seen:

- **What "unattested" means for policy B.** The draft's reason for the floor is
  that `j` unattested witnesses "might all be one source". Being tellable apart
  is an identity question, not a completeness question: the repaired policy's
  own docstring says a witness may not attest to what it does not know it
  shares. So a witness is unattested for B when the record cannot count it
  apart — `identity is ANONYMOUS`. B's floor is then exactly the lower bound
  `aggregation.independence_axes.effective_witness_bounds` already computes
  (`identified + 1`), restricted to the winning side.
- **What B does when the floor fails.** The draft says settle "only if the side
  still wins at that floor", and abstain in a tie as the baseline does. So the
  floor is a *gate on the baseline's answer*, not a second election: B never
  re-decides which side won at the floor, and therefore never settles in a
  direction the baseline did not. The consequence is recorded in the
  preregistration and in the report: under this reading B cannot fail criterion
  4 on any world whatever, because its settlements are a subset of the
  baseline's, in the same direction. That is a fact about the criterion, and
  writing the world does not entitle me to fix it.
- **What C's exposure figure is.** `unattested_exposure` returns four counts.
  The one the draft describes — "how much of it rests on witnesses who stated
  nothing" — is `ancestry_not_attested`, taken over every witness in the
  decision, both sides. The full dict is carried alongside so the figure is
  auditable, and the share variant is reported as a diagnostic because a raw
  count confounds exposure with decision size.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from itertools import combinations
from typing import Any

from aggregation.attested_independence import Use, Witness, effective_witnesses_for
from aggregation.attested_independence import unattested_exposure
from aggregation.independence_axes import WitnessDepth, WitnessIdentity
from canon.proximity import ErrorClass, Rung, Source
from canon.proximity import effective_witnesses_for as ladder_count
from experiments.aid4run.world import (
    ABSTAIN,
    SETTLED_FALSE,
    SETTLED_TRUE,
    Decision,
    RealizedWitness,
    error_class,
)

ARMS = (
    "ladder",
    "margin",
    "priced",
    "attested",
    "refuse_all_unrecorded",
)
BASELINE = "ladder"
PRIMARY_B = "margin"
PRIMARY_C = "priced"
KNOWN_BAD = "attested"
CEILING = "refuse_all_unrecorded"


def _ladder_source(witness: Witness) -> Source:
    """The baseline's view: the depth the witness claims, taken at face value.

    `canon.proximity` has no notion of backing. Handing it the claimed depth is
    the baseline this series has always measured against — the rule that reads
    silence in the ancestry record as independence and believes declarations.
    """
    rung = Rung(int(witness.claimed)) if witness.claimed is not WitnessDepth.UNSTATED else Rung.TEXT
    return Source(witness.name, rung, witness.ancestry, witness.markers)


def _side(witnesses: Iterable[RealizedWitness], side: bool) -> list[Witness]:
    return [item.witness for item in witnesses if item.vote is side]


def _ladder_count(items: list[Witness], error: ErrorClass) -> int:
    if not items:
        return 0
    return ladder_count([_ladder_source(w) for w in items], error)


def is_unattested(witness: Witness) -> bool:
    """True when the record cannot count this witness apart from another.

    See the module docstring. This is the predicate B's floor is built on, and
    it is deliberately *not* `ancestry_complete`: a completeness tick is a claim
    about an absence the witness cannot see, which is the inference the repaired
    policy removed.
    """
    return witness.identity is WitnessIdentity.ANONYMOUS


def collapse_floor(items: list[Witness], error: ErrorClass) -> int:
    """`n - j + 1`: the winning count if every unattested witness were one source.

    Clamped at 1 for a non-empty side, matching `effective_witness_bounds`,
    whose lower bound is `identified + 1` whenever anything is anonymous. The
    clamp only binds when recorded dependence has already collapsed the side
    below its headcount, which does not arise in this world — nothing is
    recorded — but the clamp is here so the arm is total.
    """
    n = _ladder_count(items, error)
    if n == 0:
        return 0
    j = sum(1 for w in items if is_unattested(w))
    if j == 0:
        return n
    return max(1, n - j + 1)


def _any_unrecorded_pair(items: Iterable[Witness]) -> bool:
    frozen = list(items)
    return any(not (a.ancestry & b.ancestry) for a, b in combinations(frozen, 2))


def _wins(n_side: int, n_other: int, threshold: int) -> bool:
    return n_side >= threshold and n_side > n_other


def n_eff(arm: str, items: list[Witness], error: ErrorClass) -> int:
    """The count each arm keeps. `margin` and `priced` count every witness."""
    if arm in (BASELINE, PRIMARY_B, PRIMARY_C, CEILING):
        return _ladder_count(items, error)
    if arm == KNOWN_BAD:
        if not items:
            return 0
        return effective_witnesses_for(items, error, use=Use.PERMIT_ACTION)
    raise ValueError(f"count not defined for {arm}")


def settle(arm: str, decision: Decision, error: ErrorClass) -> str:
    """One arm's terminal on one decision."""
    items = [item.witness for item in decision.witnesses]
    true_side = _side(decision.witnesses, True)
    false_side = _side(decision.witnesses, False)
    threshold = decision.threshold

    if arm == CEILING:
        if _any_unrecorded_pair(items):
            return ABSTAIN
        arm = BASELINE

    if arm == PRIMARY_C:
        # Policy C settles exactly as the baseline settles. Not "the same
        # computation repeated" — the same call, so no edit to this file can
        # make the exposure figure change a settlement.
        return settle(BASELINE, decision, error)

    if arm == PRIMARY_B:
        n_true = _ladder_count(true_side, error)
        n_false = _ladder_count(false_side, error)
        if _wins(n_true, n_false, threshold):
            floor = collapse_floor(true_side, error)
            return SETTLED_TRUE if _wins(floor, n_false, threshold) else ABSTAIN
        if _wins(n_false, n_true, threshold):
            floor = collapse_floor(false_side, error)
            return SETTLED_FALSE if _wins(floor, n_true, threshold) else ABSTAIN
        return ABSTAIN

    n_true = n_eff(arm, true_side, error)
    n_false = n_eff(arm, false_side, error)
    if _wins(n_true, n_false, threshold):
        return SETTLED_TRUE
    if _wins(n_false, n_true, threshold):
        return SETTLED_FALSE
    return ABSTAIN


def exposure_figure(decision: Decision) -> dict[str, int]:
    """Policy C's published figure for one decision, from the shipped function."""
    return unattested_exposure([item.witness for item in decision.witnesses])


def exposure_scalar(decision: Decision) -> int:
    """The figure C publishes as a warning: witnesses who stated nothing."""
    return exposure_figure(decision)["ancestry_not_attested"]


def exposure_share(decision: Decision) -> float:
    """Diagnostic only. A share over a handful of witnesses is not the shipped
    figure — `unattested_exposure` refuses a rate on purpose — but a raw count
    confounds exposure with decision size, and the reader is entitled to see
    whether that confound is carrying the result."""
    figure = exposure_figure(decision)
    if not figure["witnesses"]:
        return 0.0
    return round(figure["ancestry_not_attested"] / figure["witnesses"], 3)


def settle_over_units(decision: Decision, unit_of: Mapping[str, str]) -> str:
    """Reference-style settlement after an imposed grouping."""
    true_units = {unit_of[item.source_id] for item in decision.witnesses if item.vote}
    false_units = {unit_of[item.source_id] for item in decision.witnesses if not item.vote}
    n_true, n_false = len(true_units), len(false_units)
    if _wins(n_true, n_false, decision.threshold):
        return SETTLED_TRUE
    if _wins(n_false, n_true, decision.threshold):
        return SETTLED_FALSE
    return ABSTAIN


def is_pivotal(decision: Decision, focus: tuple[str, ...], error: ErrorClass) -> bool:
    """True when collapsing the focus group would move the baseline settlement.

    This is what "margin-critical" means in criterion 1: the settlement turns on
    evidence the record cannot rule out being one source.
    """
    if not focus:
        return False
    baseline = settle(BASELINE, decision, error)
    if baseline == ABSTAIN:
        return False
    units = {item.source_id: item.unit for item in decision.witnesses}
    shared = "focus:collapsed"
    collapsed = {sid: (shared if sid in focus else unit) for sid, unit in units.items()}
    return settle_over_units(decision, collapsed) != baseline


def run_decision(arm: str, decision: Decision, config: Mapping[str, Any]) -> str:
    return settle(arm, decision, error_class(config))
