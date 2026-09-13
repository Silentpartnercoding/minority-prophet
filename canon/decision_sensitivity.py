"""Compare the actions two surviving models imply, not their likelihoods.

When two plausible models both survive the evidence, the usual move is to ask
which is more likely and to spend effort closing that gap. Often the gap does not
need closing, because both models imply the same action. The disagreement is then
real, unresolved, and *not decision-material*, and the honest thing is to proceed
while recording the open question rather than pretending it was settled.

The inverse is the case that matters. If the surviving models imply different
actions, no amount of further argument about likelihood substitutes for the fact
that the decision now turns on which model is right.

Deliberately not a boolean. `PROGRAM.md`'s own warning applies here: shipping this
as a single material-or-not bit rebuilds the black box that confidence scores
were, under a new name. So a result names which models were compared, which
actions they implied, which models disagreed, and what would settle it. A caller
that wants one bit can read `is_material`; a caller that wants to know *why* has
the parts.

The action vocabulary is the Gate's -- proceed, block, escalate, request_evidence
-- per `canon/PLACEMENT.md`, and is not re-invented here. Minority Prophet emits
epistemic verdicts and no authority; this module compares what *would* be done and
decides nothing itself.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Action(StrEnum):
    """The Gate's runtime consequences. This module compares them; it takes none."""

    PROCEED = "proceed"
    BLOCK = "block"
    ESCALATE = "escalate"
    REQUEST_EVIDENCE = "request_evidence"


class Resolution(StrEnum):
    """What a caller should do about the *disagreement*, which is not the same as
    what to do about the decision. Named ACT rather than PROCEED because the
    shared action may itself be `block`, and reusing `proceed` for both senses is
    exactly the collision this corpus exists to catch."""

    ACT_NOTING_THE_OPEN_QUESTION = "act_noting_the_open_question"
    GATHER = "gather"        # more of the same evidence would separate them
    EXPERIMENT = "experiment"  # only a new observation would
    ABSTAIN = "abstain"      # neither is available, and the actions differ


@dataclass(frozen=True)
class Model:
    """One surviving account of the situation, and what it would have us do."""

    name: str
    implies: Action
    #: What observation would tell this model apart from a rival. Empty means
    #: nothing known would, which is what forces ABSTAIN rather than EXPERIMENT.
    discriminating_observation: str = ""


@dataclass(frozen=True)
class Sensitivity:
    """Whether a live disagreement changes what gets done."""

    models: tuple[Model, ...]
    actions: frozenset[Action]
    resolution: Resolution
    #: Populated only when the actions differ: the models on each side.
    split: tuple[tuple[Action, tuple[str, ...]], ...] = ()
    open_question: str = ""

    @property
    def is_material(self) -> bool:
        """One bit, for callers that only need one. The parts above are the reason
        it is not the only thing returned."""
        return len(self.actions) > 1

    def report(self) -> str:
        names = ", ".join(m.name for m in self.models)
        if not self.is_material:
            act = next(iter(self.actions))
            return (f"{len(self.models)} surviving models ({names}) all imply {act}.\n"
                    f"  NOT decision-material. Take that action and record the open\n"
                    f"  question; do not spend effort separating the models:\n"
                    f"    {self.open_question}")
        lines = [f"{len(self.models)} surviving models ({names}) imply different actions.",
                 "  DECISION-MATERIAL. The decision turns on which model is right."]
        for act, who in self.split:
            lines.append(f"    {act:<18} {', '.join(who)}")
        lines.append(f"  resolution: {self.resolution}")
        return "\n".join(lines)


def compare(models: list[Model] | tuple[Model, ...]) -> Sensitivity:
    """Compare surviving models by the action they imply."""
    models = tuple(models)
    if len(models) < 2:
        raise ValueError("decision sensitivity compares surviving models; supply at least two")
    actions = frozenset(m.implies for m in models)

    if len(actions) == 1:
        names = " vs ".join(m.name for m in models)
        return Sensitivity(
            models=models,
            actions=actions,
            resolution=Resolution.ACT_NOTING_THE_OPEN_QUESTION,
            open_question=(f"{names} remain unresolved and were not separated. They "
                           f"imply the same action, so the decision did not require "
                           f"separating them. This is recorded, not closed."),
        )

    split = tuple(
        (a, tuple(m.name for m in models if m.implies is a))
        for a in sorted(actions, key=lambda x: x.value)
    )
    # Only a discriminating observation can settle a difference in implied action.
    # If every model names one, a new observation would do it; if some do but not
    # all, more of the same evidence may; if none does, nothing available will.
    naming = [bool(m.discriminating_observation) for m in models]
    if all(naming):
        res = Resolution.EXPERIMENT
    elif any(naming):
        res = Resolution.GATHER
    else:
        res = Resolution.ABSTAIN
    return Sensitivity(models=models, actions=actions, resolution=res, split=split)


__all__ = ["Action", "Resolution", "Model", "Sensitivity", "compare"]
