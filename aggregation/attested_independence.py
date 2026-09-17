"""Independence granted by backing, never by the record's silence.

`canon/proximity.py` decides a pair independent the moment the record shows no
shared ancestry:

    if not (a.ancestry & b.ancestry):
        return True

That is a positive claim of absence, which `ASSAYER.md` A5 forbids, and it is
exactly the case the decision-relative independence series could not solve by
observation: two witnesses drawing on one hidden source, with nothing recorded
connecting them, are granted full independence against **every** class of error
— including fabrication, which is the error a hidden shared source produces.

Ledger DR3 (`no_record_rule_is_immune`) proves no rule reading the record can
tell that case from two genuine independents. It does not license picking the
favourable reading and asserting it. Under the same proof the honest move is to
fail closed, and that is all this module does. **It detects nothing.** Detection
there is proved impossible.

The rule, for two witnesses and one class of error:

1. A shared idiosyncratic marker is decisive. The trout still outranks the
   paperwork.
2. A witness with no admissible depth is independent of nothing. It has made no
   claim about how far it went, and silence stays silence rather than defaulting
   to the bottom rung.
3. Where ancestry is shared, the ladder's divergence test is unchanged.
4. Where no ancestry is recorded, the absence counts only if **both** witnesses
   attested that their ancestry record is complete. Otherwise the pair must
   clear the same divergence test as in (3).

Depth is `admissible_depth`, not the depth claimed: declaring depth is free, so
an adversary declares it, and a policy keyed to bare declarations would reward
precisely the witness it needs to discount. A `REALITY` claim backed by nothing,
from a source nobody can find, is granted `TEXT` — what a bare assertion has
always been worth.

Doctrine, scope and the two policies not implemented here:
`canon/ATTESTED-INDEPENDENCE.md`. Cost, unmeasured:
`research/decision-relative-independence/DRI-12-DESIGN-DRAFT.md`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable

from aggregation.independence_axes import (
    DepthBasis,
    WitnessDepth,
    WitnessIdentity,
    admissible_depth,
)
from canon.independent_set import DEFAULT_BUDGET, maximum_independent_set_size
from canon.proximity import ErrorClass, Rung, Source


class Use(Enum):
    """Which direction the count is used in. Required, never inferred.

    `aggregation/independence_axes.py` already records why this matters:
    undercounting is safe when `N_eff` permits an action and dangerous when it
    refuses one, because an adversary who strips attestation from evidence
    deflates the count and suppresses a true claim. This policy only ever
    deflates, so it is sound in one direction and an attack in the other.
    """

    PERMIT_ACTION = "permit-action"
    """Deciding whether to settle and act. Fewer witnesses means less action."""

    DECIDE_SURVIVAL = "decide-survival"
    """Deciding whether a contrary or minority claim survives. Forbidden here."""


class ScopeViolation(RuntimeError):
    """Raised rather than answering a question this policy must not answer."""


class UnstatedDepth(ValueError):
    """A witness with no admissible depth cannot be placed on the ladder."""


@dataclass(frozen=True)
class Witness:
    """A source, its claimed depth, and what that claim is actually backed by.

    `ancestry_complete` is the field the record does not otherwise carry: an
    assertion that the ancestry shown for this witness is all the ancestry there
    is. Default `False`, because no existing record makes that claim and
    defaulting it to `True` would reinstate the defect this module exists to fix.
    """

    name: str
    claimed: WitnessDepth = WitnessDepth.UNSTATED
    depth_basis: DepthBasis = DepthBasis.DECLARED
    identity: WitnessIdentity = WitnessIdentity.ANONYMOUS
    ancestry: frozenset[str] = field(default_factory=frozenset)
    markers: frozenset[str] = field(default_factory=frozenset)
    ancestry_complete: bool = False

    @property
    def admissible(self) -> WitnessDepth:
        """The depth actually granted: the shallower of claim and backing."""
        return admissible_depth(self.claimed, self.depth_basis, self.identity)

    @property
    def has_depth(self) -> bool:
        """False when nothing was claimed, or the claim reduces to nothing."""
        return self.admissible is not WitnessDepth.UNSTATED

    @property
    def rung(self) -> Rung:
        """Position on the proximity ladder, refused when there is none."""
        if not self.has_depth:
            raise UnstatedDepth(f"{self.name} has no admissible depth")
        return Rung(int(self.admissible))

    def as_source(self) -> Source:
        """The `canon.proximity` view of this witness, at its admissible depth.

        Note the depth: handing the *claimed* depth to the ladder is how a free
        declaration buys independence.
        """
        return Source(self.name, self.rung, self.ancestry, self.markers)


def divergence(a: Witness, b: Witness) -> Rung:
    """The shallowest rung at which the two paths separate, on admissible depth.

    The worse of the two, as in `canon.proximity.divergence`: one party going
    deep does not make the pair independent.
    """
    return Rung(max(a.rung, b.rung))


def independent_for(a: Witness, b: Witness, error: ErrorClass) -> bool:
    """Are these two independent with respect to this class of error?

    Never more permissive than `canon.proximity.independent_for` on the same
    pair. It differs only by refusing to convert silence into independence.
    """
    if a.markers & b.markers:
        return False
    if not (a.has_depth and b.has_depth):
        return False
    if not (a.ancestry & b.ancestry) and a.ancestry_complete and b.ancestry_complete:
        return True
    return divergence(a, b) <= error


def effective_witnesses_for(
    witnesses: Iterable[Witness],
    error: ErrorClass,
    *,
    use: Use,
    budget: int = DEFAULT_BUDGET,
) -> int:
    """`N_eff` against one class of error, under the attestation policy.

    `use` is required. A caller that cannot say whether the count permits an
    action or decides a claim's survival does not get to use this policy.
    """
    if use is not Use.PERMIT_ACTION:
        raise ScopeViolation(
            "the attestation policy only ever deflates the count; using it to "
            "decide whether a claim survives lets an adversary delete evidence "
            "by stripping its attestation. Use effective_witness_bounds."
        )
    items = list(witnesses)
    return maximum_independent_set_size(
        items, lambda x, y: not independent_for(x, y, error), budget=budget
    )


def independence_profile(
    witnesses: Iterable[Witness], *, use: Use = Use.PERMIT_ACTION
) -> dict[str, int]:
    """`N_eff` against every error class. There is still no error-free count."""
    items = list(witnesses)
    return {e.name: effective_witnesses_for(items, e, use=use) for e in ErrorClass}


def unattested_exposure(witnesses: Iterable[Witness]) -> dict[str, int]:
    """What a report must publish when this policy is **not** applied.

    Policy C in `canon/ATTESTED-INDEPENDENCE.md`: if the unattested witnesses
    are going to be counted anyway, the blindness is priced rather than hidden.
    Counts, not a rate — a rate over a handful of witnesses reads as precision
    the sample cannot support.
    """
    items = list(witnesses)
    return {
        "witnesses": len(items),
        "no_admissible_depth": sum(1 for w in items if not w.has_depth),
        "ancestry_not_attested": sum(1 for w in items if not w.ancestry_complete),
        "overclaimed_depth": sum(
            1 for w in items if w.claimed is not WitnessDepth.UNSTATED
            and w.admissible > w.claimed
        ),
    }
