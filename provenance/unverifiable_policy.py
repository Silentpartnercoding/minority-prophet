"""Make an unverifiable answer cost something, without making it a guilty one.

The attack, named in claim-warrant.schema.json and answered by no code until now:

    A prophet can make claims unverifiable at no cost.

Both obvious responses are wrong. Treating `unverifiable` as `rejected` means a
paywall makes you guilty and a flaky network makes you a liar. Treating it as
`verified` is the original defect. The schema is right that the two must stay
distinct -- so the cost cannot be applied to the CLAIM.

It is applied to the SETTLEMENT instead. A conclusion resting mostly on evidence
nobody could check is not a false conclusion; it is one nobody is entitled to act
on yet. So the claim keeps its three-valued verdict and the DECISION abstains.
Nothing is condemned, and nothing settles on fog.

CORRECTION. An earlier version claimed abstention "cannot cause a wrong effect".
That holds only when the status quo is safe. Defer on "should I execute this
transfer?" and nothing moves; defer on "is there a vulnerability?" and the hole
stays open. For the second kind, deferring IS the harmful act.

Worse here than in the counterexample case, because fog can outvote a finding
that WAS checked: one confirmed rejection among seven unreachable roots crosses
the ceiling and abstains, sitting on a confirmed finding because its neighbours
were unreachable.

The fix is narrower than it first looked, and the narrowing is the point. Two
kinds of withholding are not the same:

    withholding a CLEAN verdict        "I cannot certify there is nothing here."
                                       Always safe. No finding is being sat on,
                                       because by definition there is no finding.

    withholding ACTION ON A FINDING    "Something was found, but I will wait."
                                       Dangerous whenever the status quo is
                                       exposure.

Only the second needs a guard, and it needs a hard one rather than a dial: a
confirmed rejection is never withheld by fog. If something was actually found,
the fog around it does not un-find it.

The first needs no guard at all. Refusing to certify clean when most of the
evidence is unreachable is exactly right, in every domain, and that refusal is
the whole defence against a prophet who cites only unreachable sources.

An earlier draft of this module also gated the ceiling behind a
`deferring_is_safe` declaration. That was overcorrection: it reopened the attack,
because an undeclared decision could then buy a clean bill of health from pure
fog. The declaration is kept on the policy for callers that want it, and it no
longer suppresses the clean-certification defence.

Two dials, both declared rather than fitted:

    max_unverifiable_share   how much unchecked evidence a settlement may rest on
    min_checked_roots        how many roots must have actually been answered

`min_checked_roots` exists because a share is meaningless at tiny denominators:
one root of one, unverifiable, is a share of 1.0 and also a sample of one.
"""

from __future__ import annotations

from dataclasses import dataclass

SETTLE = "settle"
ABSTAIN_UNVERIFIABLE = "abstain_unverifiable"
ABSTAIN_UNDERPOWERED = "abstain_underpowered"


@dataclass(frozen=True)
class UnverifiablePolicy:
    """Declared before a population is seen, per the repository's own habit.

    The two numbers are defaults chosen for this module rather than measured.
    They govern one thing only: whether a CLEAN verdict may be issued over fog.
    They can never withhold action on a confirmed finding, so being wrong about
    them costs a certification, never a remedy.
    """
    max_unverifiable_share: float = 0.5
    min_checked_roots: int = 2

    def __post_init__(self):
        if not 0.0 <= self.max_unverifiable_share <= 1.0:
            raise ValueError("max_unverifiable_share must be a share between 0 and 1")
        if self.min_checked_roots < 1:
            raise ValueError("min_checked_roots must be at least 1")


def apply_policy(outcomes: dict, policy: UnverifiablePolicy | None = None) -> dict:
    """Decide whether a settlement may proceed on this evidence.

    `outcomes` is the counter shape produced by `warrant_recheck.recheck_report`:
    verified / rejected / unverifiable / not_rechecked.

    Returns the decision, the numbers behind it, and -- when it abstains -- what
    would have to change. An abstention that does not say what would lift it is
    just a refusal.
    """
    policy = policy or UnverifiablePolicy()
    verified = int(outcomes.get("verified", 0))
    rejected = int(outcomes.get("rejected", 0))
    unverifiable = int(outcomes.get("unverifiable", 0))

    answered = verified + rejected
    considered = answered + unverifiable
    share = (unverifiable / considered) if considered else None

    # The one guard that is needed. Something was actually found: fog around a
    # confirmed rejection does not un-find it, and withholding here would mean
    # sitting on a real finding because its neighbours were unreachable. Below
    # this line nothing was found, so every remaining outcome withholds a CLEAN
    # verdict only -- which is safe in every domain.
    if rejected > 0:
        out = _decision(SETTLE, share, answered, unverifiable, policy, None)
        out["note"] = ("a rejection was confirmed; fog around it cannot withhold it. "
                       "Fog still blocks a CLEAN settlement, which is the attack this guards.")
        return out

    if considered == 0:
        return _decision(ABSTAIN_UNDERPOWERED, share, answered, unverifiable, policy,
                         "no root carried a reference that could be re-checked at all")
    if answered < policy.min_checked_roots:
        return _decision(ABSTAIN_UNDERPOWERED, share, answered, unverifiable, policy,
                         f"only {answered} root(s) were actually answered; a share over so few "
                         "is not a measurement")
    if share > policy.max_unverifiable_share:
        return _decision(ABSTAIN_UNVERIFIABLE, share, answered, unverifiable, policy,
                         f"{unverifiable} of {considered} roots could not be checked, above the "
                         f"declared ceiling of {policy.max_unverifiable_share:.0%}")
    return _decision(SETTLE, share, answered, unverifiable, policy, None)


def _decision(decision, share, answered, unverifiable, policy, why):
    out = {
        "decision": decision,
        "unverifiableShare": round(share, 3) if share is not None else None,
        "rootsAnswered": answered,
        "rootsUnverifiable": unverifiable,
        "policy": {"maxUnverifiableShare": policy.max_unverifiable_share,
                   "minCheckedRoots": policy.min_checked_roots},
        "condemnsAnything": False,
    }
    if decision != SETTLE:
        out["reason"] = why
        needed = max(0, policy.min_checked_roots - answered)
        out["wouldLiftIf"] = (
            f"{needed} more root(s) are answered" if needed else
            "enough of the unverifiable roots become answerable — configure a resolver "
            "that can reach them, or cite references that can be reached"
        )
    return out


def annotate(report: dict, policy: UnverifiablePolicy | None = None) -> dict:
    """Attach the decision to a recheck report without altering its counts."""
    return {**report, "settlement": apply_policy(report.get("outcomes", {}), policy)}
