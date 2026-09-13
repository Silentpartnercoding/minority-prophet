"""A brake that can stop a conclusion it believes is correct.

Every other stop in this programme fires on not knowing enough. This one fires on
the opposite: the conclusion may well be right, and acting on it or revealing it
would change the system enough that acting becomes harmful. Uncertainty is
explicitly not a reason here; a brake that only ever says "not sure" is the brake
we already have.

That requires the system to model its own causal footprint, and it requires three
stances to be kept apart, because they are routinely collapsed:

    PREDICTION                 saying what will happen, changing nothing
    INTERVENTION               doing something, which changes what happens
    POST_INTERVENTION_FORECAST saying what will happen *given that we acted*

The third is where reflexive failure lives. A forecast made after an intervention
is a forecast about a world the forecaster has already altered, and treating it as
an ordinary prediction is how a system ends up confirming its own effects.

`PROGRAM.md`'s warning is honoured the same way the susceptibility probe honours
it: firing on something being "materially unsafe" without decomposing what
material means would be a new black box under a new name. So a firing names its
reason, the stance it applies to, who bears the cost, and what would make it
release. There is no severity score.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Stance(StrEnum):
    """What the system is doing when it says the thing."""

    PREDICTION = "prediction"
    INTERVENTION = "intervention"
    POST_INTERVENTION_FORECAST = "post_intervention_forecast"


class Reflexive(StrEnum):
    """Why acting or revealing is harmful. None of these is uncertainty."""

    #: Revealing it changes the behaviour it describes, so it stops being true.
    SELF_INVALIDATING = "self_invalidating"
    #: Revealing it brings about what it predicts, and the bringing about is the harm.
    SELF_FULFILLING = "self_fulfilling"
    #: Measuring it disturbs the thing measured; the reading is of our own hand.
    OBSERVATION_IS_INTERVENTION = "observation_is_intervention"
    #: Acting has effects outside the failure domain the governor declared.
    FOOTPRINT_EXCEEDS_MANDATE = "footprint_exceeds_mandate"
    #: The forecast is about a world this system already altered, and is being
    #: read as though it were an independent prediction.
    FORECAST_CONFIRMS_OUR_OWN_EFFECT = "forecast_confirms_our_own_effect"


@dataclass(frozen=True)
class Footprint:
    """What this system's own action does to the thing it is reasoning about."""

    stance: Stance
    #: Named parties who experience the effect. Empty means the system asserts it
    #: has no footprint, which is a claim and is recorded as one.
    bears_the_cost: tuple[str, ...] = ()
    #: Whether the subject can observe the system's output and respond to it.
    subject_can_observe_us: bool = False
    #: Whether taking the reading itself disturbs the thing being read. Distinct
    #: from the subject reacting to our *output*: here the act of measuring is the
    #: intervention, so withholding the conclusion does not help.
    measuring_disturbs_the_subject: bool = False
    #: Whether the declared failure domain contains every party above.
    within_declared_domain: bool = True


@dataclass(frozen=True)
class Firing:
    """The brake engaged. Carries its reason, never a score."""

    reason: Reflexive
    stance: Stance
    belief: float
    bears_the_cost: tuple[str, ...]
    releases_when: str

    def report(self) -> str:
        return (f"BRAKE: {self.reason}\n"
                f"  the conclusion is held at {self.belief:.2f} and is NOT being "
                f"disputed; this is not an uncertainty stop\n"
                f"  stance: {self.stance}\n"
                f"  cost borne by: {', '.join(self.bears_the_cost) or 'unnamed'}\n"
                f"  releases when: {self.releases_when}")


#: Below this the ordinary uncertainty machinery owns the decision, and a
#: reflexive brake would be indistinguishable from it.
CONFIDENT = 0.70


def check(belief: float, footprint: Footprint) -> Firing | None:
    """Fire only on a conclusion the system holds confidently.

    Returns None below `CONFIDENT` by design: the point of this brake is that it
    is not an uncertainty stop, so it must be silent exactly where an uncertainty
    stop would speak. Deferring there is a boundary, not an oversight.
    """
    if not 0.0 <= belief <= 1.0:
        raise ValueError(f"belief must be in [0, 1], got {belief}")
    if belief < CONFIDENT:
        return None

    def fire(reason: Reflexive, releases: str) -> Firing:
        return Firing(reason=reason, stance=footprint.stance, belief=belief,
                      bears_the_cost=footprint.bears_the_cost, releases_when=releases)

    if not footprint.within_declared_domain:
        return fire(Reflexive.FOOTPRINT_EXCEEDS_MANDATE,
                    "the governor widens the declared failure domain to contain "
                    "every party named above, or the action is narrowed to fit it")

    if footprint.stance is Stance.POST_INTERVENTION_FORECAST:
        return fire(Reflexive.FORECAST_CONFIRMS_OUR_OWN_EFFECT,
                    "the forecast is restated as conditional on our intervention, "
                    "or a control that we did not touch is supplied")

    if footprint.measuring_disturbs_the_subject:
        return fire(Reflexive.OBSERVATION_IS_INTERVENTION,
                    "a measurement path is found that does not touch the subject, "
                    "or the reading is reported as a reading of our own hand")

    if footprint.subject_can_observe_us:
        if footprint.stance is Stance.PREDICTION:
            return fire(Reflexive.SELF_INVALIDATING,
                        "the prediction is withheld from the subject, or reissued "
                        "as a claim about the subject's behaviour when informed")
        return fire(Reflexive.SELF_FULFILLING,
                    "the intervention is separated from the announcement, so the "
                    "effect can be attributed to one of them")

    return None


__all__ = ["Stance", "Reflexive", "Footprint", "Firing", "check", "CONFIDENT"]
