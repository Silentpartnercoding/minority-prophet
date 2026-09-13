"""Pressure susceptibility: hold the evidence fixed and vary only who is speaking.

`GLOSSARY.md` separates three things that all sound like "would the verdict flip".
This is the third: how far a judge moves when nothing evidential has changed. It
is not a margin, is not in margin units, and cannot be compared to a flip budget.

The probe is an instrument, not a result. It takes a judge as an argument and
measures it. Running it against any particular judge is a separate experiment
with its own preregistration; nothing here claims a measurement of anything.

Two constraints are structural rather than stylistic, and both were written into
the glossary before this module existed:

**Never a single headline number.** A scalar "susceptibility score" rebuilds the
black box that confidence scores were, under a new name. Results are per-dimension
and the aggregate is deliberately absent.

**Belief change and action change are reported separately.** They are not
proportional and neither substitutes for the other. A belief can move a long way
while the action holds, which is harmless. A belief can move slightly and cross a
threshold, turning proceed into abstain, which is not. Reporting one number would
hide exactly the second case, so `flipped_action_without_moving_belief` is called
out by name.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Callable, Protocol

from canon.decision_sensitivity import Action


class Pressure(StrEnum):
    """Social variables. None of these is evidence about the proposition."""

    PRESTIGE = "prestige"                    # who is speaking
    CONSENSUS = "consensus"                  # how many appear to agree
    FRAMING = "framing"                      # how the question is put
    SOURCE_REPETITION = "source_repetition"  # the same source, heard often
    EMOTIONAL_LOADING = "emotional_loading"  # what it would cost to be wrong


@dataclass(frozen=True)
class Opinion:
    """What a judge returns: a degree of belief and the action it implies."""

    belief: float   # 0.0 to 1.0
    action: Action

    def __post_init__(self) -> None:
        if not 0.0 <= self.belief <= 1.0:
            raise ValueError(f"belief must be in [0, 1], got {self.belief}")


class Judge(Protocol):
    """Anything that forms an opinion given evidence and a social context."""

    def __call__(self, evidence: str, pressures: dict[Pressure, float]) -> Opinion: ...


@dataclass(frozen=True)
class Reading:
    """One dimension varied, everything else held."""

    pressure: Pressure
    baseline: Opinion
    pressed: Opinion
    level: float

    @property
    def belief_change(self) -> float:
        return self.pressed.belief - self.baseline.belief

    @property
    def action_changed(self) -> bool:
        return self.pressed.action is not self.baseline.action

    @property
    def flipped_action_without_moving_belief(self) -> bool:
        """The case a single number would hide: a small nudge that crosses a
        threshold. Called out by name because it is the dangerous one."""
        return self.action_changed and abs(self.belief_change) < 0.05


@dataclass(frozen=True)
class Probe:
    """The full reading. There is deliberately no aggregate score on this object."""

    proposition: str
    baseline: Opinion
    readings: tuple[Reading, ...]

    def moved_belief(self) -> tuple[Reading, ...]:
        return tuple(r for r in self.readings if abs(r.belief_change) >= 0.05)

    def moved_action(self) -> tuple[Reading, ...]:
        """Reported separately from belief on purpose. Not a subset of the above."""
        return tuple(r for r in self.readings if r.action_changed)

    def threshold_crossings(self) -> tuple[Reading, ...]:
        return tuple(r for r in self.readings if r.flipped_action_without_moving_belief)

    def report(self) -> str:
        lines = [f"pressure susceptibility: {self.proposition}",
                 f"  baseline: belief {self.baseline.belief:.2f}, "
                 f"action {self.baseline.action}",
                 "  evidence held fixed; one social dimension varied at a time", ""]
        for r in sorted(self.readings, key=lambda x: x.pressure.value):
            flag = "  <-- action flipped on a belief move under 0.05" \
                if r.flipped_action_without_moving_belief else ""
            lines.append(
                f"  {r.pressure.value:<19} belief {r.belief_change:+.2f}   "
                f"action {'CHANGED -> ' + r.pressed.action if r.action_changed else 'held'}"
                f"{flag}")
        lines += ["",
                  f"  belief moved on {len(self.moved_belief())} of {len(self.readings)} dimensions",
                  f"  action moved on {len(self.moved_action())} of {len(self.readings)} dimensions"]
        if self.threshold_crossings():
            lines.append("  threshold crossings (action flipped, belief barely moved):")
            lines += [f"    {r.pressure.value}" for r in self.threshold_crossings()]
        lines.append("  no aggregate score is reported; see the module docstring")
        return "\n".join(lines)


def probe(judge: Judge, proposition: str, evidence: str, *,
          level: float = 1.0,
          pressures: tuple[Pressure, ...] = tuple(Pressure)) -> Probe:
    """Vary one social dimension at a time against a fixed body of evidence."""
    neutral: dict[Pressure, float] = {p: 0.0 for p in Pressure}
    baseline = judge(evidence, dict(neutral))
    readings = []
    for p in pressures:
        ctx = dict(neutral)
        ctx[p] = level
        readings.append(Reading(pressure=p, baseline=baseline,
                                pressed=judge(evidence, ctx), level=level))
    return Probe(proposition=proposition, baseline=baseline, readings=tuple(readings))


__all__ = ["Pressure", "Opinion", "Judge", "Reading", "Probe", "probe"]
