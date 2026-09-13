"""What a zero weight means, decided explicitly instead of by accident.

`audit/falsify.py::weight_boundary_probe` records the defect: a zero-weight root
is counted at full strength by the cardinality aggregator and at zero by
`weighted_vote`, so one corpus yields two verdicts depending on which reads it.
`formal/EXTENSION-SOCKETS.md` section 2 states that the two must be reconciled
before any weighted theorem is stated. This is that reconciliation.

It does not pick a winner, because neither reading is wrong. They answer
different questions:

    COUNTS_AS_A_ROOT   presence is what matters. A source that observed the
                       world and assigned itself no confidence still observed
                       the world, and the margin theorems count observations.
    EXCLUDED           mass is what matters. A source contributing zero mass
                       contributes nothing, and summing it changes no total.

The real defect is underneath both. `ClaimLike` types confidence and competence
as `float`, so **a weight that was never supplied and a weight deliberately set
to zero are the same value**. That is exactly the ambiguity `U2` found for absent
provenance one level up, and it is resolved the same way: name the policy, make
it a parameter, and default to fail-closed.

    REFUSE             the default. If the corpus contains a zero weight and the
                       two readings disagree about the verdict, refuse rather
                       than silently adopt one.

`REFUSE` is not timidity. It is `canon/decision_sensitivity.py` applied here: a
disagreement only matters where it changes the answer. Where both readings give
the same verdict the ambiguity is real, unresolved, and not decision-material,
and the caller proceeds while the open question is recorded.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable, Protocol


class WeightedClaim(Protocol):
    value: bool
    confidence: float
    competence: float


class ZeroWeightPolicy(StrEnum):
    """How a zero weight is read. Never inferred; always supplied or defaulted."""

    REFUSE = "refuse"                        # fail closed on a decisive disagreement
    COUNTS_AS_A_ROOT = "counts_as_a_root"    # the cardinality reading
    EXCLUDED = "excluded"                    # the mass reading


class ZeroWeightAmbiguity(ValueError):
    """The corpus contains a zero weight and the two readings disagree."""


@dataclass(frozen=True)
class Reading:
    """What each policy would conclude, and whether the choice matters."""

    zero_weight_claims: int
    as_roots: tuple[int, int]      #: (true, false) under the cardinality reading
    as_mass: tuple[float, float]   #: (true, false) under the mass reading

    @property
    def has_zero_weights(self) -> bool:
        return self.zero_weight_claims > 0

    @staticmethod
    def _side(t: float, f: float) -> str:
        return "true" if t > f else ("false" if f > t else "abstain")

    @property
    def verdict_as_roots(self) -> str:
        return self._side(*self.as_roots)

    @property
    def verdict_as_mass(self) -> str:
        return self._side(*self.as_mass)

    @property
    def decision_material(self) -> bool:
        """The only question worth asking. If both readings agree, the ambiguity
        is real and unresolved and does not need resolving to act."""
        return self.verdict_as_roots != self.verdict_as_mass

    def report(self) -> str:
        if not self.has_zero_weights:
            return "no zero weights present; the policy does not engage"
        head = (f"{self.zero_weight_claims} zero-weight claim(s)\n"
                f"  as roots: {self.as_roots} -> {self.verdict_as_roots}\n"
                f"  as mass:  {self.as_mass} -> {self.verdict_as_mass}")
        if self.decision_material:
            return head + ("\n  DECISION-MATERIAL: the two readings disagree, so the "
                           "verdict depends on a convention the corpus does not state.")
        return head + ("\n  not decision-material: both readings agree, so the "
                       "ambiguity is recorded and the verdict stands either way.")


def _weight(claim: WeightedClaim) -> float:
    return max(0.0, min(1.0, claim.confidence)) * max(0.0, min(1.0, claim.competence))


def read(claims: Iterable[WeightedClaim]) -> Reading:
    """Compute both readings. Decides nothing."""
    claims = list(claims)
    zero = sum(1 for c in claims if _weight(c) == 0.0)
    rt = sum(1 for c in claims if c.value)
    rf = len(claims) - rt
    mt = sum(_weight(c) for c in claims if c.value)
    mf = sum(_weight(c) for c in claims if not c.value)
    return Reading(zero_weight_claims=zero, as_roots=(rt, rf), as_mass=(mt, mf))


def resolve(claims: Iterable[WeightedClaim], *,
            policy: ZeroWeightPolicy = ZeroWeightPolicy.REFUSE) -> str:
    """Return one verdict under a named policy, or refuse.

    Refusing is the default and it fires only where the choice changes the
    answer. A corpus with zero weights whose readings agree resolves normally.
    """
    r = read(claims)
    if not r.has_zero_weights:
        return r.verdict_as_roots
    if policy is ZeroWeightPolicy.COUNTS_AS_A_ROOT:
        return r.verdict_as_roots
    if policy is ZeroWeightPolicy.EXCLUDED:
        return r.verdict_as_mass
    if r.decision_material:
        raise ZeroWeightAmbiguity(
            "zero weights present and the two readings disagree "
            f"({r.verdict_as_roots} as roots, {r.verdict_as_mass} as mass). "
            "A zero weight that was never supplied and one deliberately set to "
            "zero are the same float, so the corpus does not state which is "
            "meant. Supply an explicit ZeroWeightPolicy."
        )
    return r.verdict_as_roots


__all__ = ["ZeroWeightPolicy", "ZeroWeightAmbiguity", "Reading", "read", "resolve"]
