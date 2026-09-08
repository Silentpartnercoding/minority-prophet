"""`IndependenceBasis` decomposed into the two axes it was conflating.

`IndependenceBasis` ranks four values on one scale:

    UNKNOWN(0) < INFERRED(1) < DECLARED(2) < ATTESTED(3)

Those four values are not four points on one dimension. They are a diagonal
through a two-dimensional space, and collapsing them onto a single rank produces
comparisons that are not real:

* **ATTESTED vs DECLARED** differ only in *who vouched*. Neither says anything
  about whether anyone went and looked.
* **INFERRED vs the rest** differs only in *how far back toward the world* the
  root reached. It says nothing about who vouched.

Ranking those against each other forces an exchange rate between vouching and
looking, and there is no such rate. The visible consequence is an inversion:

> Under `BASIS_RANK`, a **notarised piece of hearsay** (`ATTESTED`, rank 3)
> outranks an **anonymous eyewitness** (`INFERRED`, rank 1) — a signed statement
> from someone who only read a document beats an unsigned report from someone
> who was in the room.

That is backwards, and no single ordering of four values can fix it, because the
error is the single ordering.

**This module is additive.** `IndependenceBasis`, `BASIS_RANK` and `verdict()`
are untouched, and the wire vocabulary shared byte-for-byte with
`invention_engine.models.IndependenceBasis` is preserved exactly. Decomposition
is offered alongside so callers can migrate deliberately.

The replacement for a total rank is a **partial order**: one root dominates
another only when it is at least as good on *both* axes. Incomparable pairs stay
incomparable rather than being forced into a false ranking — the same
no-trading-off rule the gate uses everywhere else.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Iterable, Sequence


class WitnessDepth(IntEnum):
    """How far back toward the world the root actually reached.

    Lower is closer to the world and stronger. `UNSTATED` is not a depth; it
    records that the legacy vocabulary never carried one.
    """

    REALITY = 0       # observed the world
    METHOD = 1        # re-measured by a materially different route
    REPLICATION = 2   # re-measured the same way
    RAW = 3           # recomputed from the raw record
    ANALYSIS = 4      # recomputed from published figures
    TEXT = 5          # read, restated, reasoned over
    UNSTATED = 6      # the source vocabulary did not say


class DepthBasis(IntEnum):
    """How we know the depth. The question `WitnessDepth` alone cannot answer.

    A stated depth is worth what its backing is worth. "I was there" is free,
    so an adversary says it as readily as an honest witness; naming a procedure
    is also free, though at least specific enough that someone could check.
    What raises the cost is the observation having **left something behind**
    that the claimant could not author alone.

    The ladder terminates, which the independence question never did: it bottoms
    out at a signed artifact, a fact about cryptography rather than a claim
    about a person.
    """

    DECLARED = 0          # "I was there." Free, therefore worthless alone.
    PROCEDURAL = 1        # a named, specific procedure -- checkable in principle
    ARTIFACT = 2          # the observation produced a log, capture or receipt
    DEVICE_ATTESTED = 3   # signed by a keyholding device or instrument


#: The deepest rung each basis can support. A claim deeper than its backing is
#: granted only what the backing carries -- overclaiming buys nothing.
#:
#: `DECLARED` bottoms out at `TEXT` deliberately. Claiming to have merely read
#: something is a claim against interest: nobody lies to look weaker, so the
#: weakest rung needs no backing. That is the hearsay exception, borrowed from
#: the same place proximate cause was.
DEPTH_FLOOR: dict[DepthBasis, "WitnessDepth"] = {}

#: What each identity level stakes on the claim, expressed as the backing it is
#: worth on its own.
#:
#: Law furnished this. Sworn eyewitness testimony carries no artifact and no
#: instrument, yet is treated as strong evidence -- because the oath is not an
#: exception to the cost rule but another way of paying it. An artifact is
#: expensive to fabricate; sworn testimony is expensive to be caught on.
#:
#: The teeth are the perjury statute, not the ceremony. Swearing changes nothing
#: by itself; what changes is that a false statement becomes a prosecutable act.
#: So the stake only bites where the claimant can be found and held, which is
#: why courts require the witness identified, present and cross-examinable, and
#: why anonymous testimony is generally inadmissible. That is not an
#: accommodation bolted on here -- the model predicts it: an anonymous oath
#: stakes nothing, because there is nobody to prosecute.
IDENTITY_STAKE: dict["WitnessIdentity", DepthBasis] = {}


class WitnessIdentity(IntEnum):
    """Whether the *observer* can be identified and held to the claim.

    Distinct from the issuer identity the root registry already requires. The
    registry authenticates **who requested the root**; it says nothing about
    **who saw the thing**. An authenticated newspaper minting a root for an
    anonymous source is fully compliant with R1.4 and tells you nothing about
    whether two such roots came from two people.

    That is the open half of U1, recorded in
    `research/knowledge-ledger/experiments/KL-014/CORRECTION-20260813-quota.md`:
    an issuer may supply many distinct `observation_id`s for one real
    observation and stay inside quota. Witness identity is the lever on it,
    because distinctness is only checkable when the observer is.

    Absence is `ANONYMOUS`, not a separate `UNSTATED` -- having no identity on
    record *is* anonymity, so nothing is being guessed.
    """

    ANONYMOUS = 0      # no identity; cannot be reached, questioned, or counted apart
    PSEUDONYMOUS = 1   # stable handle, not resolvable to a person
    NAMED = 2          # identity asserted, unverified
    VERIFIED = 3       # identity bound by signature or institution
    BONDED = 4         # identity plus something at stake if wrong


class Attestation(IntEnum):
    """Who vouched for the CLAIM, and how disinterested they were.

    Not the same as `WitnessIdentity`, which is about the SOURCE. An anonymous
    whistleblower whose account a journalist verified is `ANONYMOUS` identity
    with `INDEPENDENT` attestation -- a real and common combination that one
    axis cannot express without the testament overwriting the anonymity.
    """

    NONE = 0
    SELF = 1          # the source vouches for itself
    INTERNAL = 2      # same organisation or control domain
    INDEPENDENT = 3   # separate party with no stake
    ADVERSARIAL = 4   # a party actively trying to find fault


@dataclass(frozen=True)
class IndependenceAxes:
    """A root's independence on three axes, none implying the others.

    Each does a different job in the machinery:

    * `depth` decides **which classes of error** this root can catch.
    * `attestation` reduces the **R3 margin**, by making undetected dependence
      less likely.
    * `identity` decides whether `N_eff` is **computable at all** -- two
      anonymous witnesses cannot be shown to be two people.
    """

    depth: WitnessDepth
    attestation: Attestation
    identity: WitnessIdentity = WitnessIdentity.ANONYMOUS
    depth_basis: DepthBasis = DepthBasis.DECLARED
    stake_reference: str | None = None
    """Where the exposure lives: a case number, licence, bond or registry id.

    Minority Prophet does not punish anyone. It is the assayer, not the sheriff.
    An oath has teeth because perjury is prosecutable *elsewhere*, so `BONDED`
    records that a claim sits under someone else's consequence regime -- it
    never creates one.

    Which makes this field load-bearing rather than decorative. `BONDED` unlocks
    `REALITY` depth with no artifact, so a self-declared `BONDED` would be the
    cheapest lie in the system and the most valuable. It must therefore point at
    something checkable, and an unreferenced stake is not honoured.
    """

    @property
    def honoured_identity(self) -> "WitnessIdentity":
        """Identity after checking that any claimed exposure points somewhere.

        A stake asserted without a reference is an assertion, not a stake, and
        degrades to `NAMED` -- the strongest position a bare claim of identity
        can reach. Overclaiming buys nothing here either.
        """
        if (self.identity >= WitnessIdentity.VERIFIED
                and not (self.stake_reference or "").strip()):
            return WitnessIdentity.NAMED
        return self.identity

    @property
    def admissible(self) -> WitnessDepth:
        """Depth after applying its backing, whether produced or staked.

        Use this, not `depth`, to decide anything.
        """
        return admissible_depth(self.depth, self.depth_basis,
                                self.honoured_identity)

    def dominates(self, other: "IndependenceAxes") -> bool:
        """Partial order over all three axes. Never a score.

        Nothing is traded against anything: vouching does not buy depth, depth
        does not buy identity. A pair better on one axis and worse on another is
        **incomparable**, and the caller escalates rather than ranking them.
        """
        return (self.admissible <= other.admissible
                and self.attestation >= other.attestation
                and self.identity >= other.identity)

    def comparable_to(self, other: "IndependenceAxes") -> bool:
        return self.dominates(other) or other.dominates(self)


#: What each legacy value actually pins down, keyed by the wire string so this
#: module has no dependency on `root_vote` -- `root_vote` depends on this one.
#: `UNSTATED` marks the axis the legacy vocabulary was silent about: silence
#: recorded as silence, never defaulted (ASSAYER A5).
DECOMPOSITION: dict[str, IndependenceAxes] = {
    "attested": IndependenceAxes(WitnessDepth.UNSTATED, Attestation.INDEPENDENT),
    "declared": IndependenceAxes(WitnessDepth.UNSTATED, Attestation.SELF),
    "inferred": IndependenceAxes(WitnessDepth.TEXT, Attestation.NONE),
    "unknown": IndependenceAxes(WitnessDepth.UNSTATED, Attestation.NONE),
}


def decompose(basis) -> IndependenceAxes:
    """Lossy by necessity: three of the four legacy values carry no depth."""
    return DECOMPOSITION[getattr(basis, "value", basis)]


IDENTITY_STAKE.update({
    WitnessIdentity.ANONYMOUS: DepthBasis.DECLARED,        # nothing at stake
    WitnessIdentity.PSEUDONYMOUS: DepthBasis.DECLARED,     # reputation, unenforceable
    WitnessIdentity.NAMED: DepthBasis.PROCEDURAL,          # findable; reputational cost
    WitnessIdentity.VERIFIED: DepthBasis.ARTIFACT,         # bound; can be held to it
    WitnessIdentity.BONDED: DepthBasis.DEVICE_ATTESTED,    # sworn; real exposure
})

DEPTH_FLOOR.update({
    DepthBasis.DECLARED: WitnessDepth.TEXT,
    DepthBasis.PROCEDURAL: WitnessDepth.RAW,
    DepthBasis.ARTIFACT: WitnessDepth.METHOD,
    DepthBasis.DEVICE_ATTESTED: WitnessDepth.REALITY,
})


def effective_basis(basis: DepthBasis, identity: "WitnessIdentity") -> DepthBasis:
    """The stronger of what was produced and what was staked.

    A witness may back a claim with an artifact, or with their own exposure, or
    with both. The two are alternative payments for the same thing.
    """
    return DepthBasis(max(basis, IDENTITY_STAKE[identity]))


def admissible_depth(claimed: WitnessDepth, basis: DepthBasis,
                     identity: "WitnessIdentity" = None) -> WitnessDepth:
    """The depth actually granted: the shallower of what was claimed and what
    the backing supports.

    Overclaiming is not punished, it is simply ineffective -- a `REALITY` claim
    backed by nothing but assertion from an unfindable source is granted `TEXT`,
    which is what a bare assertion has always been worth. Underclaiming is
    honoured: strong backing on a modest claim does not inflate it.

    Caveat worth stating: a stake is only worth its enforcement. The oath has
    teeth because perjury is prosecutable; a bond in a jurisdiction that never
    prosecutes is theatre, and this model cannot tell the difference. `BONDED`
    is a claim about consequences that somebody else has to make true.
    """
    if identity is not None:
        basis = effective_basis(basis, identity)
    return WitnessDepth(max(claimed, DEPTH_FLOOR[basis]))


def indistinguishable(a: IndependenceAxes, b: IndependenceAxes) -> bool:
    """True when the two roots cannot be **shown** to be different sources.

    Read this carefully: it does not mean they are the same source. Two
    anonymous witnesses to the same event may be one person reporting twice, or
    may be two people. Nothing in the record settles it, and no amount of
    vouching helps -- a testament about a claim says nothing about whether two
    sources are the same source.

    An earlier version of this module collapsed such roots to a count of one.
    That was wrong, and owner review caught it. Collapsing *asserts* identity
    exactly as counting them separately *asserts* distinctness; both invent a
    fact the record does not contain, and A5 forbids positive claims of absence.

    It is also not conservative, only directional. Undercounting is safe when
    `N_eff` is used to permit an action and dangerous when it is used to refuse
    one: an adversary who can strip identity from evidence deflates the count
    and suppresses a true claim. That is the censorship primitive that retired
    greedy counting, reintroduced through a default.

    The honest treatment is `effective_witness_bounds`, which reports the range
    the record actually supports and lets the caller escalate when the answer
    depends on where in that range the truth lies.
    """
    return (a.identity is WitnessIdentity.ANONYMOUS
            and b.identity is WitnessIdentity.ANONYMOUS)


@dataclass(frozen=True)
class WitnessBounds:
    """What the record supports: a range, not a number.

    `lower` assumes every mutually-anonymous root is the same source; `upper`
    assumes they are all different. The truth is somewhere inside, and the
    record does not say where.
    """

    lower: int
    upper: int

    @property
    def determined(self) -> bool:
        """True when identity is sufficient to pin the count exactly."""
        return self.lower == self.upper

    def __post_init__(self) -> None:
        if self.lower > self.upper:
            raise ValueError("lower bound exceeds upper bound")


def meet(a: IndependenceAxes, b: IndependenceAxes) -> IndependenceAxes:
    """Greatest lower bound: the weaker position on every axis at once.

    Two claims on one root may disagree about its independence. Under a total
    order the resolution was `min`; under a partial order the componentwise meet
    is the well-defined equivalent, and it always exists. Conservative by
    construction -- it can only take the worse depth, the worse testament and
    the worse identity.
    """
    return IndependenceAxes(
        WitnessDepth(max(a.depth, b.depth)),
        Attestation(min(a.attestation, b.attestation)),
        WitnessIdentity(min(a.identity, b.identity)),
        DepthBasis(min(a.depth_basis, b.depth_basis)),
    )


def effective_witness_bounds(axes: Sequence[IndependenceAxes]) -> WitnessBounds:
    """Bound `N_eff` from both sides instead of inventing a point estimate.

    Non-anonymous roots are countable: their identifiers can be compared. Every
    anonymous root is a coin the record refuses to turn over -- it might be a
    fresh source or a repeat of one already counted.

    A caller that needs a single number is asking a question the evidence does
    not answer. Feed the bounds to the gate: if the decision is the same at both
    ends, it is determined; if it differs, escalate. That is the same
    three-outcome discipline used everywhere else, applied to counting.
    """
    identified = sum(1 for a in axes if a.identity is not WitnessIdentity.ANONYMOUS)
    anonymous = sum(1 for a in axes if a.identity is WitnessIdentity.ANONYMOUS)
    if anonymous == 0:
        return WitnessBounds(identified, identified)
    return WitnessBounds(identified + 1, identified + anonymous)


def minimal_axes(items: Iterable[IndependenceAxes]) -> tuple[IndependenceAxes, ...]:
    """The **weakest** elements: an antichain, not a single value.

    `weakest_basis` assumes a total order and returns one value. Under a partial
    order there may be several minimal elements that no ordering can rank
    against each other -- an anonymous eyewitness and a notarised hearsay are
    both weakest, in different ways.

    When this returns more than one element, any single "weakest" is a fiction,
    and the honest response is to escalate rather than to pick.
    """
    uniq = list(dict.fromkeys(items))
    return tuple(
        x for i, x in enumerate(uniq)
        if not any(j != i and x.dominates(y) and not y.dominates(x)
                   for j, y in enumerate(uniq))
    )


def weakest_is_well_defined(items: Iterable[IndependenceAxes]) -> bool:
    """False when the evidence set has no single weakest member."""
    return len(minimal_axes(items)) <= 1


def legacy_basis(axes: IndependenceAxes) -> str:
    """Project back onto the wire vocabulary. Lossy in the other direction.

    Depth cannot survive the round trip, because the legacy vocabulary has
    nowhere to put it. Preserved only for interoperability with
    `invention_engine`; new callers should carry both axes.
    """
    if axes.attestation >= Attestation.INDEPENDENT:
        return "attested"
    if axes.attestation >= Attestation.SELF:
        return "declared"
    if axes.depth <= WitnessDepth.TEXT:
        return "inferred"
    return "unknown"


def rank_inversion_witness() -> tuple[IndependenceAxes, IndependenceAxes]:
    """The concrete failure the single rank produces.

    Returns `(notarised_hearsay, anonymous_eyewitness)`. The legacy rank puts
    the first above the second. On the axes they are incomparable, which is the
    truthful answer: one has a better testament, the other actually saw it.
    """
    notarised_hearsay = IndependenceAxes(
        WitnessDepth.TEXT, Attestation.INDEPENDENT,
        WitnessIdentity.ANONYMOUS, DepthBasis.DECLARED)
    # Backed, because an unbacked REALITY claim is granted TEXT and genuinely
    # *is* hearsay -- see `admissible_depth`. The inversion this documents is
    # about a real eyewitness, not an asserted one.
    anonymous_eyewitness = IndependenceAxes(
        WitnessDepth.REALITY, Attestation.NONE,
        WitnessIdentity.ANONYMOUS, DepthBasis.ARTIFACT)
    return notarised_hearsay, anonymous_eyewitness


# ---------------------------------------------------------------------------
# Shared wire vocabulary, v2
#
# v1 was the four values of `IndependenceBasis`, which express 4 of the 30
# points in the (depth x attestation) space -- 13%. Five of six witness depths
# and two of five attestation levels had no encoding at all, so a root that
# reached reality could not be written down.
#
# v2 adds both axes explicitly. It is strictly additive: the four v1 strings are
# unchanged and still parse, a v1 reader ignores the new fields, and a v2 reader
# falls back to decomposing the v1 value when the new fields are absent.
#
# These strings are duplicated byte-for-byte in
# `invention_engine/models.py`. Neither copy may drift; a conformance test in
# each project asserts the exact ordered lists and this version number.
# ---------------------------------------------------------------------------

INDEPENDENCE_VOCABULARY_VERSION = 4

DEPTH_WIRE: dict[WitnessDepth, str] = {
    WitnessDepth.REALITY: "reality",
    WitnessDepth.METHOD: "method",
    WitnessDepth.REPLICATION: "replication",
    WitnessDepth.RAW: "raw",
    WitnessDepth.ANALYSIS: "analysis",
    WitnessDepth.TEXT: "text",
    WitnessDepth.UNSTATED: "unstated",
}

ATTESTATION_WIRE: dict[Attestation, str] = {
    Attestation.NONE: "none",
    Attestation.SELF: "self",
    Attestation.INTERNAL: "internal",
    Attestation.INDEPENDENT: "independent",
    Attestation.ADVERSARIAL: "adversarial",
}

IDENTITY_WIRE: dict[WitnessIdentity, str] = {
    WitnessIdentity.ANONYMOUS: "anonymous",
    WitnessIdentity.PSEUDONYMOUS: "pseudonymous",
    WitnessIdentity.NAMED: "named",
    WitnessIdentity.VERIFIED: "verified",
    WitnessIdentity.BONDED: "bonded",
}

DEPTH_BASIS_WIRE: dict[DepthBasis, str] = {
    DepthBasis.DECLARED: "declared",
    DepthBasis.PROCEDURAL: "procedural",
    DepthBasis.ARTIFACT: "artifact",
    DepthBasis.DEVICE_ATTESTED: "device-attested",
}

_DEPTH_BY_WIRE = {v: k for k, v in DEPTH_WIRE.items()}
_DEPTH_BASIS_BY_WIRE = {v: k for k, v in DEPTH_BASIS_WIRE.items()}
_IDENTITY_BY_WIRE = {v: k for k, v in IDENTITY_WIRE.items()}
_ATTESTATION_BY_WIRE = {v: k for k, v in ATTESTATION_WIRE.items()}


class VocabularyError(ValueError):
    """An unrecognised wire value. Refused, never coerced to a default."""


def to_wire(axes: IndependenceAxes) -> dict[str, str]:
    """Serialise both axes. Emitted alongside `independence_basis`, not instead."""
    return {"witness_depth": DEPTH_WIRE[axes.depth],
            "attestation": ATTESTATION_WIRE[axes.attestation],
            "witness_identity": IDENTITY_WIRE[axes.identity],
            "depth_basis": DEPTH_BASIS_WIRE[axes.depth_basis]}


def from_wire(payload: dict, *, legacy_basis_value: str | None = None) -> IndependenceAxes:
    """Parse both axes, falling back to the v1 value when they are absent.

    A v1 producer sends only `independence_basis`; the result is then whatever
    that value pins down, with `UNSTATED` where it says nothing. Unknown strings
    raise rather than defaulting -- an unrecognised vocabulary is a refusal, not
    a downgrade.
    """
    depth_raw = payload.get("witness_depth")
    attest_raw = payload.get("attestation")
    identity_raw = payload.get("witness_identity")
    basis_raw = payload.get("depth_basis")

    if (depth_raw is None and attest_raw is None and identity_raw is None
            and basis_raw is None):
        basis = legacy_basis_value or payload.get("independence_basis") or "unknown"
        if basis not in DECOMPOSITION:
            raise VocabularyError(f"unrecognised independence_basis {basis!r}")
        return DECOMPOSITION[basis]

    if depth_raw is not None and depth_raw not in _DEPTH_BY_WIRE:
        raise VocabularyError(f"unrecognised witness_depth {depth_raw!r}")
    if attest_raw is not None and attest_raw not in _ATTESTATION_BY_WIRE:
        raise VocabularyError(f"unrecognised attestation {attest_raw!r}")
    if identity_raw is not None and identity_raw not in _IDENTITY_BY_WIRE:
        raise VocabularyError(f"unrecognised witness_identity {identity_raw!r}")
    if basis_raw is not None and basis_raw not in _DEPTH_BASIS_BY_WIRE:
        raise VocabularyError(f"unrecognised depth_basis {basis_raw!r}")

    return IndependenceAxes(
        _DEPTH_BY_WIRE.get(depth_raw, WitnessDepth.UNSTATED),
        _ATTESTATION_BY_WIRE.get(attest_raw, Attestation.NONE),
        _IDENTITY_BY_WIRE.get(identity_raw, WitnessIdentity.ANONYMOUS),
        _DEPTH_BASIS_BY_WIRE.get(basis_raw, DepthBasis.DECLARED),
    )


def vocabulary_coverage() -> tuple[int, int]:
    """`(expressible_under_v1, total_points)`. Was 4 of 30; v2 is all of them."""
    v1 = len({DECOMPOSITION[k] for k in DECOMPOSITION})
    real_depths = [d for d in WitnessDepth if d is not WitnessDepth.UNSTATED]
    return (v1, len(real_depths) * len(Attestation) * len(WitnessIdentity)
            * len(DepthBasis))
