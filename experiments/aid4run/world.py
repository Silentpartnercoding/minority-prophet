"""AID-4 world. Eight families, each built so a named criterion can lose.

The draft named two policies and two criterion sets before this world existed.
This file is the world, and it is written to make both policies losable.

**Adoption.** `alpha` is the probability that a witness which *can* attest
actually presents its credentials for a decision. A witness that presents them
appears with the backing it really has (a device attestation, a verified
identity) and ticks `ancestry_complete`. A witness that does not present them
appears as what the record then holds: a bare declaration from an anonymous
source, with the completeness box unticked. Witnesses who cannot attest never
present credentials at any rate. Adversarial copies that hold a device key
present them at every rate.

That is a stronger adoption model than AID-3's, which moved only the
completeness tick. It is chosen so that `alpha` moves all three policies rather
than only the rejected one, and it has a consequence flagged here rather than
discovered later: **at alpha = 0 every witness in the world is anonymous**, so
policy B's floor is 1 on every side and B settles nothing above threshold 2.
That is a property of B under this adoption model, not an artifact introduced to
defeat it, and it is disclosed in `PREREGISTRATION.md` section 10 before any
salt is read.

**Nothing connects the copies in the record.** No family records ancestry or
idiosyncratic markers. That is DR3's case, and it makes `refuse_all_unrecorded`
abstain on every decision in the world — which is what a cost *ceiling* is for.

Families, and the criterion each is built to break:

- **hidden_source** — DR3. Two copies of one hidden parent plus three honest
  attestable witnesses, ordinary noisy voting. The copies can attest at the same
  rate as anyone else, so at `alpha = 1` they are attested and B's floor stops
  collapsing them. Aimed at B's criterion 1 at high adoption, and at C's
  criterion 1: adoption is orthogonal to whether the hidden dependence bites, so
  exposure should not separate the classes.
- **backed_hidden_source** — AID-2's finding, made a family. Three copies of one
  hidden parent, each holding a device key and a verified identity, attesting at
  every rate. A device attestation earns depth; it says nothing about shared
  origin. B counts them as three, so its floor never fires. Aimed at B's
  criterion 1 at *every* rate, and at C, whose exposure figure reads zero on
  exactly the settlements that are false.
- **honest_unattestable** — witnesses who went to the world and left nothing.
  Thin margin, three against two, baseline always right. B's floor collapses the
  winning side to 1 and B abstains on every decision. Aimed at criterion 5 and
  at C's criterion 2, where exposure is constant and discriminates nothing.
- **wide_margin_unattested** — the construction no previous world supplied.
  Four against one, with unattested witnesses present on the winning side and
  enough attested ones that B's floor still clears the threshold. B can settle
  here rather than merely refuse. Aimed at criterion 5 from the other side: if B
  cannot pass here it is refusal with extra steps.
- **silent_but_correct** — the other construction no previous world supplied.
  Settlements that rest on silence and are nonetheless correct, in two shapes:
  one where the hidden dependence sits on the *losing* side and therefore does
  not make the settlement wrong, and one where the winning side is entirely
  unattested and entirely right. Aimed at C: without these, high exposure and
  falsity coincide and discrimination is trivial.
- **minority_suppression** — carried forward from AID-3 unchanged in substance.
  Two unattestable witnesses hold the true claim, two backed attesters hold the
  false one, the ladder ties and abstains. This killed policy A. B faces it
  unchanged.
- **minority_wins** — the asymmetry that AID-3 could not exhibit. The minority
  is *the winning side* and it is the side carrying the unattested witnesses:
  three unattestable witnesses hold the true claim and beat two backed
  attesters, so the baseline settles for them and is right. Collapsing the
  winning side is not symmetric when the minority is the winning side. B
  abstains and the vindication is lost, while the frozen criterion 4 — which
  asks only whether the claim was settled *against* — records no loss.
- **mixed_populations** — hidden copies, attestable witnesses, unattestable
  witnesses and one honest restater in one decision, noisy voting. The family
  where both outcome classes arise from the same layout, so C's discrimination
  is measured without any cross-family confound.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import random
from collections.abc import Iterable, Mapping
from typing import Any

from aggregation.attested_independence import Witness
from aggregation.independence_axes import DepthBasis, WitnessDepth, WitnessIdentity
from canon.proximity import ErrorClass

FAMILIES = (
    "hidden_source",
    "backed_hidden_source",
    "honest_unattestable",
    "wide_margin_unattested",
    "silent_but_correct",
    "minority_suppression",
    "minority_wins",
    "mixed_populations",
)

#: Families whose votes come from source accuracy and a component fault, as in
#: AID-3. They produce both outcome classes from one layout.
NOISY_FAMILIES = ("hidden_source", "backed_hidden_source", "mixed_populations")

#: Families whose decision structure is forced, because the structure *is* the
#: construction being tested.
FORCED_FAMILIES = (
    "honest_unattestable",
    "wide_margin_unattested",
    "silent_but_correct",
    "minority_suppression",
    "minority_wins",
)

SETTLED_TRUE = "settled_true"
SETTLED_FALSE = "settled_false"
ABSTAIN = "abstain"
SETTLED = (SETTLED_TRUE, SETTLED_FALSE)
REVERSIBLE = "low_reversible"

ROLE_ATTESTABLE = "attestable"
ROLE_UNATTESTABLE = "unattestable"
ROLE_HIDDEN = "hidden"
ROLE_BACKED_HIDDEN = "backed_hidden"
ROLE_RESTATER = "restater"

#: Roles that hold the true claim in the two minority families.
MINORITY_ROLES = (ROLE_UNATTESTABLE,)


def _seed(*parts: object) -> int:
    return int.from_bytes(hashlib.sha256("|".join(map(str, parts)).encode()).digest(), "big")


@dataclasses.dataclass(frozen=True)
class Source:
    """A source, its true causal unit, and what it can show for itself.

    `stance` is fixed for forced families — `True` votes with the truth, `False`
    against it — and `None` where votes come from accuracy and fault instead.
    """

    source_id: str
    accuracy: float
    component: str | None
    can_attest: bool
    always_attest: bool
    claimed: WitnessDepth
    depth_basis: DepthBasis
    identity: WitnessIdentity
    ancestry: frozenset[str]
    markers: frozenset[str]
    role: str
    stance: bool | None = None


@dataclasses.dataclass(frozen=True)
class RealizedWitness:
    source_id: str
    vote: bool
    unit: str
    adopted: bool
    witness: Witness
    role: str


@dataclasses.dataclass(frozen=True)
class Decision:
    decision_id: str
    truth: bool
    threshold: int
    decision_class: str
    witnesses: tuple[RealizedWitness, ...]
    reference: str
    mixed: bool


@dataclasses.dataclass(frozen=True)
class Campaign:
    campaign_id: str
    family: str
    sources: tuple[Source, ...]
    focus_group: tuple[str, ...]
    decisions: tuple[Decision, ...]


def _attestable(source_id: str, accuracy: float, *, stance: bool | None = None) -> Source:
    """Honest, and able to show a device attestation and a verified identity."""
    return Source(
        source_id,
        accuracy,
        None,
        True,
        False,
        WitnessDepth.REALITY,
        DepthBasis.DEVICE_ATTESTED,
        WitnessIdentity.VERIFIED,
        frozenset(),
        frozenset(),
        ROLE_ATTESTABLE,
        stance,
    )


def _unattestable(source_id: str, accuracy: float, *, stance: bool | None = None) -> Source:
    """Honest, went to the world, left nothing behind and cannot be found.

    Not a defect and not an adversary. This witness is right as often as any
    other and can never produce backing at any adoption rate.
    """
    return Source(
        source_id,
        accuracy,
        None,
        False,
        False,
        WitnessDepth.REALITY,
        DepthBasis.DECLARED,
        WitnessIdentity.ANONYMOUS,
        frozenset(),
        frozenset(),
        ROLE_UNATTESTABLE,
        stance,
    )


def _hidden_copy(
    source_id: str, accuracy: float, component: str, *, stance: bool | None = None
) -> Source:
    """A copy of one hidden parent that attests at the same rate as anybody else.

    AID-1's construction, carried forward: a hidden pair that can fill in the
    same form as two honest attesters is the same object as two honest
    attesters, and nothing in the record distinguishes them. So these copies
    hold real credentials — each one can show that *it* reached the world and
    who *it* is — and present them at rate `alpha`, exactly like the honest
    witnesses beside them. What no credential speaks to is the parent they
    share, because nothing recorded connects them.

    This is what puts policy B's prevention on an adoption curve: while the
    copies are silent, B's floor collapses them and prevents the settlement;
    once they attest, B counts them apart and hands back the independence it
    was withholding. `_backed_hidden_copy` is the same defect with the dial
    removed.
    """
    return Source(
        source_id,
        accuracy,
        component,
        True,
        False,
        WitnessDepth.REALITY,
        DepthBasis.DEVICE_ATTESTED,
        WitnessIdentity.VERIFIED,
        frozenset(),
        frozenset(),
        ROLE_HIDDEN,
        stance,
    )


def _backed_hidden_copy(source_id: str, accuracy: float, component: str) -> Source:
    """A copy of one hidden parent that holds a device key and a verified name.

    AID-2 recorded this and no world has carried it: a device attestation earns
    depth and says nothing whatever about shared origin. Nothing in the record
    connects these copies, and each one can prove exactly how far *it* went.
    """
    return Source(
        source_id,
        accuracy,
        component,
        True,
        True,
        WitnessDepth.REALITY,
        DepthBasis.DEVICE_ATTESTED,
        WitnessIdentity.VERIFIED,
        frozenset(),
        frozenset(),
        ROLE_BACKED_HIDDEN,
    )


def _restater(source_id: str, accuracy: float) -> Source:
    """Claims only to have read and restated, and is honest about it.

    Present so the shipped exposure figure's axes do not collapse onto one
    number: this witness is `ancestry_not_attested` and is *not*
    `overclaimed_depth`, because its claim and its backing agree.
    """
    return Source(
        source_id,
        accuracy,
        None,
        False,
        False,
        WitnessDepth.TEXT,
        DepthBasis.DECLARED,
        WitnessIdentity.ANONYMOUS,
        frozenset(),
        frozenset(),
        ROLE_RESTATER,
    )


def _layout(
    config: Mapping[str, Any], family: str, rng: random.Random
) -> tuple[tuple[Source, ...], tuple[str, ...]]:
    accuracies = tuple(config["source_accuracies"])
    high = max(accuracies)
    mid = accuracies[len(accuracies) // 2]

    if family == "hidden_source":
        group = tuple(_hidden_copy(f"g{i}", rng.choice(accuracies), "hidden:u") for i in range(2))
        rest = tuple(_attestable(f"i{i}", rng.choice(accuracies)) for i in range(3))
        return group + rest, tuple(s.source_id for s in group)

    if family == "backed_hidden_source":
        group = tuple(
            _backed_hidden_copy(f"b{i}", rng.choice(accuracies), "hidden:v") for i in range(3)
        )
        rest = tuple(_attestable(f"i{i}", rng.choice(accuracies)) for i in range(2))
        return group + rest, tuple(s.source_id for s in group)

    if family == "honest_unattestable":
        # Three against two, everybody silent. The baseline is always right and
        # B's floor collapses the winning side to one.
        with_truth = tuple(_unattestable(f"u{i}", high, stance=True) for i in range(3))
        against = tuple(_unattestable(f"v{i}", mid, stance=False) for i in range(2))
        return with_truth + against, ()

    if family == "wide_margin_unattested":
        # Four against one. Three of the four can attest, so B's floor is 4 at
        # full adoption and the decision is settlable rather than merely refused.
        backed = tuple(_attestable(f"a{i}", high, stance=True) for i in range(3))
        silent = (_unattestable("n0", high, stance=True),)
        against = (_attestable("a3", mid, stance=False),)
        return backed + silent + against, ()

    if family == "silent_but_correct":
        # Two shapes, chosen per campaign. Both settle correctly and both rest
        # on silence; only one contains a hidden source, and it is on the side
        # that loses.
        if rng.random() < config["silent_correct_hidden_share"]:
            winners = (
                _attestable("a0", high, stance=True),
                _attestable("a1", high, stance=True),
                _unattestable("n0", high, stance=True),
            )
            losers = tuple(
                _hidden_copy(f"g{i}", mid, "hidden:w", stance=False) for i in range(2)
            )
            return winners + losers, tuple(s.source_id for s in losers)
        winners = tuple(_unattestable(f"n{i}", high, stance=True) for i in range(3))
        losers = tuple(_attestable(f"a{i}", mid, stance=False) for i in range(2))
        return winners + losers, ()

    if family == "minority_suppression":
        # AID-3's construction, unchanged in substance: a forced tie the ladder
        # abstains on, with backing on the false side only.
        majority = tuple(_attestable(f"m{i}", mid, stance=False) for i in range(2))
        minority = tuple(_unattestable(f"n{i}", high, stance=True) for i in range(2))
        return majority + minority, tuple(s.source_id for s in minority)

    if family == "minority_wins":
        # The minority holds the true claim, carries every unattested witness,
        # and wins on the baseline. Collapsing the winning side is what costs it.
        minority = tuple(_unattestable(f"n{i}", high, stance=True) for i in range(3))
        majority = tuple(_attestable(f"m{i}", mid, stance=False) for i in range(2))
        return minority + majority, tuple(s.source_id for s in minority)

    if family == "mixed_populations":
        hidden = tuple(_hidden_copy(f"g{i}", rng.choice(accuracies), "hidden:u") for i in range(2))
        backed = tuple(_attestable(f"a{i}", rng.choice(accuracies)) for i in range(2))
        silent = tuple(_unattestable(f"u{i}", rng.choice(accuracies)) for i in range(2))
        restater = (_restater("r0", mid),)
        return hidden + backed + silent + restater, tuple(s.source_id for s in hidden)

    raise ValueError(f"unknown family {family}")


def _adopts(source: Source, alpha: float, rng: random.Random) -> bool:
    if source.always_attest:
        return True
    if not source.can_attest:
        return False
    return rng.random() < alpha


def _realize(source: Source, vote: bool, adopted: bool) -> RealizedWitness:
    """A source as the record holds it for this decision.

    Presenting credentials is what `alpha` governs. A witness that does not
    present them is not accused of anything — the record simply holds a bare
    declaration from someone it cannot tell apart from anyone else.
    """
    if adopted:
        witness = Witness(
            name=source.source_id,
            claimed=source.claimed,
            depth_basis=source.depth_basis,
            identity=source.identity,
            ancestry=source.ancestry,
            markers=source.markers,
            ancestry_complete=True,
        )
    else:
        witness = Witness(
            name=source.source_id,
            claimed=source.claimed,
            depth_basis=DepthBasis.DECLARED,
            identity=WitnessIdentity.ANONYMOUS,
            ancestry=source.ancestry,
            markers=source.markers,
            ancestry_complete=False,
        )
    return RealizedWitness(
        source_id=source.source_id,
        vote=vote,
        unit=source.component or source.source_id,
        adopted=adopted,
        witness=witness,
        role=source.role,
    )


def _ordinary_votes(
    sources: tuple[Source, ...], truth: bool, rng: random.Random, config: Mapping[str, Any]
) -> dict[str, bool]:
    faulty = {
        component: rng.random() < config["component_fault_rate"]
        for component in sorted({s.component for s in sources if s.component})
    }
    votes: dict[str, bool] = {}
    for source in sources:
        if source.component and faulty[source.component]:
            votes[source.source_id] = not truth
        else:
            votes[source.source_id] = truth if rng.random() < source.accuracy else not truth
    return votes


def _forced_votes(sources: tuple[Source, ...], truth: bool) -> dict[str, bool]:
    return {s.source_id: (truth if s.stance else not truth) for s in sources}


def _count_units(realized: tuple[RealizedWitness, ...], side: bool) -> int:
    return len({item.unit for item in realized if item.vote is side})


def reference_settlement(realized: tuple[RealizedWitness, ...], threshold: int) -> str:
    """Settlement over true causal units. A hidden pair is one unit."""
    n_true = _count_units(realized, True)
    n_false = _count_units(realized, False)
    if n_true >= threshold and n_true > n_false:
        return SETTLED_TRUE
    if n_false >= threshold and n_false > n_true:
        return SETTLED_FALSE
    return ABSTAIN


def is_mixed(realized: tuple[RealizedWitness, ...]) -> bool:
    adopted = {item.adopted for item in realized}
    return True in adopted and False in adopted


def _decision(
    config: Mapping[str, Any],
    campaign: str,
    index: int,
    sources: tuple[Source, ...],
    family: str,
    alpha: float,
    rng: random.Random,
) -> Decision:
    truth = (
        True
        if family in ("minority_suppression", "minority_wins")
        else bool(rng.getrandbits(1))
    )
    if family in NOISY_FAMILIES:
        votes = _ordinary_votes(sources, truth, rng, config)
    else:
        votes = _forced_votes(sources, truth)
    realized = tuple(
        _realize(source, votes[source.source_id], _adopts(source, alpha, rng)) for source in sources
    )
    threshold = config["threshold"]
    return Decision(
        decision_id=f"{campaign}|d{index:02d}",
        truth=truth,
        threshold=threshold,
        decision_class=REVERSIBLE,
        witnesses=realized,
        reference=reference_settlement(realized, threshold),
        mixed=is_mixed(realized),
    )


def generate_campaign(
    config: Mapping[str, Any], salt: str, family: str, replicate: int, alpha: float
) -> Campaign:
    rng = random.Random(_seed(salt, family, replicate, alpha))
    campaign_id = f"{family}|a{alpha}|{replicate:05d}"
    sources, focus = _layout(config, family, rng)
    decisions = tuple(
        _decision(config, campaign_id, index, sources, family, alpha, rng)
        for index in range(config["decisions_per_campaign"])
    )
    return Campaign(
        campaign_id=campaign_id,
        family=family,
        sources=sources,
        focus_group=focus,
        decisions=decisions,
    )


def cells(config: Mapping[str, Any]) -> tuple[float, ...]:
    return tuple(config["adoption_rates"])


def cell_key(alpha: float) -> str:
    return f"alpha={alpha}"


def error_class(config: Mapping[str, Any]) -> ErrorClass:
    return ErrorClass[config["error_class"]]


def iter_cell_campaigns(
    config: Mapping[str, Any], salt: str, campaigns_per_family: int | None = None
) -> Iterable[tuple[str, Campaign]]:
    count = config["campaigns_per_family"] if campaigns_per_family is None else campaigns_per_family
    for family in config["families"]:
        for replicate in range(count):
            for alpha in cells(config):
                yield cell_key(alpha), generate_campaign(config, salt, family, replicate, alpha)


def campaign_hash_row(cell: str, campaign: Campaign) -> bytes:
    row = {
        "cell": cell,
        "campaignId": campaign.campaign_id,
        "focus": list(campaign.focus_group),
        "sources": [
            [
                s.source_id,
                s.accuracy,
                s.component,
                s.can_attest,
                s.always_attest,
                s.claimed.name,
                s.depth_basis.name,
                s.identity.name,
                s.role,
                s.stance,
            ]
            for s in campaign.sources
        ],
        "decisions": [
            {
                "id": d.decision_id,
                "truth": d.truth,
                "reference": d.reference,
                "mixed": d.mixed,
                "witnesses": [
                    {
                        "id": w.source_id,
                        "vote": w.vote,
                        "unit": w.unit,
                        "adopted": w.adopted,
                        "complete": w.witness.ancestry_complete,
                        "identity": w.witness.identity.name,
                        "admissible": w.witness.admissible.name,
                        "role": w.role,
                    }
                    for w in d.witnesses
                ],
            }
            for d in campaign.decisions
        ],
    }
    return (json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n").encode()
