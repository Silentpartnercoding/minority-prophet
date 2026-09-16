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

The asymmetry that makes this safe: abstention withholds action, it does not
grant it. A policy that could only ever escalate is a policy that cannot cause a
wrong effect -- which is the same reason Minority Prophet holds no authority in
the first place.

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
    """Declared before a population is seen, per the repository's own habit."""
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
