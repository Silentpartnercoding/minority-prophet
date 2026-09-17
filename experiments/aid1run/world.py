"""AID-1 world: six families, each built so the attested policy can lose.

The policy under test is `aggregation/attested_independence.py`, written by
someone else. `research/attested-independence/AID-1-DESIGN-DRAFT.md` section 5
names the six families the world must contain. They are built here to the letter
of that section, and where the letter left a choice, the choice was made against
the policy rather than for it. Every such choice is named in
`PREREGISTRATION.md`.

Families, and what each is built to break:

- **nobody_can_attest** — five honest witnesses who went to the world and can
  prove nothing: `REALITY` claimed, `DECLARED` basis, `ANONYMOUS` identity, so
  `admissible_depth` grants them `TEXT`. They are `attestable=False`, so the
  adoption rate never reaches them. Nothing is hidden, so the policy can prevent
  nothing here and every settlement it drops is pure cost. This is the family
  that decides criterion 2.
- **adversary_attests_freely** — three witnesses echoing one fabricator, in
  three strains. `declares_completeness` is the spec's own wording: declared
  `REALITY`, declared complete ancestry, no backing, no holdable identity. The
  policy's completeness clause fires *before* any depth check, so the strain is
  granted full independence against `FABRICATION`. `claims_bonded_identity`
  declares `BONDED` with nothing behind it; `Witness.admissible` calls
  `admissible_depth` directly and never applies `honoured_identity`, so the free
  claim buys `REALITY`. `declares_depth_only` is the strain where the backing
  machinery actually bites, and it is here so criterion 3 is a real test rather
  than a foregone one.
- **hidden_shared_source** — DR3's case. Four witnesses on one hidden source,
  nothing recorded connecting them, plus three genuine independents. Two
  variants: `aware` witnesses know their ancestry record is incomplete and so
  never attest completeness; `unaware` witnesses attest completeness in good
  faith and are wrong. The policy can only prevent anything in `aware`.
- **baseline_already_right** — three witnesses who are simply right and one who
  is simply wrong, nothing hidden, everyone attestable. A policy that discounts
  reflexively is punished; at `alpha = 1.0` a working policy pays nothing.
- **minority_suppression** — three attestable majority witnesses asserting the
  false value against three unattestable witnesses carrying the true one, all
  six genuinely independent. The baseline ties and the claim survives; the
  policy deflates the minority to one and settles against it. The call is made
  with `Use.PERMIT_ACTION`, because that is what a caller settling a decision
  declares, and nothing in the record tells it that the same count also deletes
  a claim.
- **mixed_attestation** — one decision containing an artifact-attested pair on a
  hidden source, a recorded-ancestry pair sharing a marker, an unattestable
  witness, a witness that states no depth at all, and a device-attested witness.

Machinery is reused rather than rebuilt: DRI-3 settlement outcomes
(`settlement_over_units`, the `SETTLED` vocabulary, the reversible/irreversible
classes), `provenance/dependence_robustness.py` for whether a settlement is
silent or flagged by the record, `canon/independent_set.py` through both
independence modules for `N_eff`, and DRI-2 statistics in `scoring.py`.
"""

from __future__ import annotations

import dataclasses
import hashlib
import itertools
import json
import random
from collections.abc import Iterable, Mapping
from typing import Any

from aggregation.attested_independence import Witness
from aggregation.independence_axes import DepthBasis, WitnessDepth, WitnessIdentity
from canon.proximity import ErrorClass
from experiments.dri3.world import IRREVERSIBLE, REVERSIBLE, SETTLED, settlement_over_units
from provenance.decision_relative import DecisionEvidence
from provenance.dependence_robustness import assess_dependence_robustness

UNSETTLED = "unsettled"

FAMILIES = (
    "nobody_can_attest",
    "adversary_attests_freely",
    "hidden_shared_source",
    "baseline_already_right",
    "minority_suppression",
    "mixed_attestation",
)

#: Sub-populations inside a family. A variant is a separate campaign, so the
#: strains never average each other away inside one campaign; the family row
#: still aggregates them, because the frozen criteria are stated per family.
VARIANTS: dict[str, tuple[str, ...]] = {
    "nobody_can_attest": ("unfindable_honest",),
    "adversary_attests_freely": (
        "declares_completeness",
        "declares_depth_only",
        "claims_bonded_identity",
    ),
    "hidden_shared_source": ("unaware", "aware"),
    "baseline_already_right": ("nothing_hidden",),
    "minority_suppression": ("count_decides_survival",),
    "mixed_attestation": ("mixed",),
}

HIDDEN_FAMILY = "hidden_shared_source"
FREELY_ATTESTING_FAMILY = "adversary_attests_freely"
MINORITY_FAMILY = "minority_suppression"

#: What an act of attestation buys. An artifact reaches `METHOD` and no further;
#: only a device attestation or a bonded identity reaches `REALITY`
#: (`aggregation/independence_axes.py`, DEPTH_FLOOR and IDENTITY_STAKE).
ATTESTATION_KINDS: dict[str, tuple[DepthBasis, WitnessIdentity]] = {
    "artifact": (DepthBasis.ARTIFACT, WitnessIdentity.VERIFIED),
    "device": (DepthBasis.DEVICE_ATTESTED, WitnessIdentity.BONDED),
}

#: The legacy `independence_basis` wire value DRI-3 stamps on every cut. It is
#: the vocabulary of `aggregation/root_vote.py` and is unrelated to the policy's
#: sense of "attested"; it is kept identical to DRI-3 so the reference
#: settlement is DRI-3's, unchanged.
LEGACY_BASIS = "attested"


def _seed(*parts: object) -> int:
    return int.from_bytes(hashlib.sha256("|".join(map(str, parts)).encode()).digest(), "big")


@dataclasses.dataclass(frozen=True)
class WitnessSpec:
    """A witness before the adoption draw decides what it can prove."""

    wid: str
    unit: str
    """True causal unit. Witnesses sharing one are one source, whatever the
    record says."""
    role: str
    """honest | liar | echo | independent."""
    accuracy: float
    claimed: WitnessDepth
    attestable: bool
    """False for a witness the adoption rate can never reach."""
    attestation: str
    ancestry: tuple[str, ...]
    """Recorded ancestry beyond the witness's own token."""
    markers: tuple[str, ...]
    complete_when_attested: bool
    """Whether attesting also produces a completeness claim. False for a witness
    that knows its ancestry record is incomplete."""
    complete_override: bool | None = None
    identity_override: WitnessIdentity | None = None


@dataclasses.dataclass(frozen=True)
class Decision:
    decision_id: str
    index: int
    truth: bool
    threshold: int
    decision_class: str
    values: tuple[tuple[str, bool], ...]
    evidence: tuple[DecisionEvidence, ...]
    reference: str
    """Settlement over the true causal units. DRI-3's `settlement_over_units`."""
    naive: str
    """Settlement with every witness counted as its own source."""
    critical: bool
    """The true dependence is what decides this one: reference != naive."""
    robust_settlement: str | None
    """What the recorded ancestry alone robustly settles, or None. A settlement
    the record does not corroborate is flagged; one it does is silent."""
    contrary_value: bool | None
    """The value the minority carries, where a minority claim is at stake."""


@dataclasses.dataclass(frozen=True)
class Campaign:
    campaign_id: str
    family: str
    variant: str
    alpha: float
    specs: tuple[WitnessSpec, ...]
    witnesses: tuple[Witness, ...]
    attested: tuple[tuple[str, bool], ...]
    unit_of: tuple[tuple[str, str], ...]
    ancestry_cuts: tuple[str, ...]
    mixed_attestation: bool
    decisions: tuple[Decision, ...]


def _spec(
    wid: str,
    unit: str,
    role: str,
    *,
    accuracy: float = 1.0,
    claimed: WitnessDepth = WitnessDepth.REALITY,
    attestable: bool = True,
    attestation: str = "artifact",
    ancestry: tuple[str, ...] = (),
    markers: tuple[str, ...] = (),
    complete_when_attested: bool = True,
    complete_override: bool | None = None,
    identity_override: WitnessIdentity | None = None,
) -> WitnessSpec:
    return WitnessSpec(
        wid=wid,
        unit=unit,
        role=role,
        accuracy=accuracy,
        claimed=claimed,
        attestable=attestable,
        attestation=attestation,
        ancestry=ancestry,
        markers=markers,
        complete_when_attested=complete_when_attested,
        complete_override=complete_override,
        identity_override=identity_override,
    )


def layout(config: Mapping[str, Any], family: str, variant: str) -> tuple[WitnessSpec, ...]:
    """The witness population of one campaign. No randomness: the shape of a
    family is a construction, not a draw."""
    if family == "nobody_can_attest":
        # Honest, deep, and unprovable. `attestable=False` so no adoption rate
        # reaches them; `admissible_depth(REALITY, DECLARED, ANONYMOUS)` is TEXT.
        return tuple(
            _spec(f"u{i}", f"unit:u{i}", "independent",
                  accuracy=config["unfindable_accuracy"], attestable=False)
            for i in range(config["unfindable_witnesses"])
        )

    if family == "adversary_attests_freely":
        if variant == "declares_completeness":
            override, identity = True, None
        elif variant == "declares_depth_only":
            override, identity = False, None
        elif variant == "claims_bonded_identity":
            override, identity = False, WitnessIdentity.BONDED
        else:
            raise ValueError(f"unknown variant {variant}")
        adversaries = [
            _spec(f"a{i}", "hidden:fabricator", "liar", attestable=False,
                  complete_override=override, identity_override=identity)
            for i in range(config["adversary_group_size"])
        ]
        honest = [
            _spec(f"h{i}", f"unit:h{i}", "independent", accuracy=config["honest_accuracy"])
            for i in range(config["adversary_honest_witnesses"])
        ]
        return tuple(adversaries + honest)

    if family == HIDDEN_FAMILY:
        aware = variant == "aware"
        group = [
            _spec(f"g{i}", "hidden:source", "echo", complete_when_attested=not aware)
            for i in range(config["hidden_group_size"])
        ]
        rest = [
            _spec(f"i{i}", f"unit:i{i}", "independent", accuracy=config["independent_accuracy"])
            for i in range(config["hidden_independents"])
        ]
        return tuple(group + rest)

    if family == "baseline_already_right":
        right = [
            _spec(f"t{i}", f"unit:t{i}", "honest")
            for i in range(config["already_right_witnesses"])
        ]
        return tuple(right + [_spec("d0", "unit:d0", "liar")])

    if family == MINORITY_FAMILY:
        majority = [
            _spec(f"m{i}", f"unit:m{i}", "liar") for i in range(config["majority_size"])
        ]
        # Carrying the true claim and unable to attest: the case the policy's
        # own scope says must not be decided by a count.
        minority = [
            _spec(f"c{i}", f"unit:c{i}", "honest", attestable=False)
            for i in range(config["minority_size"])
        ]
        return tuple(majority + minority)

    if family == "mixed_attestation":
        return (
            _spec("x0", "hidden:mixed", "echo"),
            _spec("x1", "hidden:mixed", "echo"),
            _spec("x2", "recorded:pair", "echo", ancestry=("doc:shared",),
                  markers=("mark:shared",)),
            _spec("x3", "recorded:pair", "echo", ancestry=("doc:shared",),
                  markers=("mark:shared",)),
            _spec("x4", "unit:x4", "independent", accuracy=config["independent_accuracy"],
                  attestable=False),
            _spec("x5", "unit:x5", "independent", accuracy=config["independent_accuracy"],
                  attestable=False, claimed=WitnessDepth.UNSTATED),
            _spec("x6", "unit:x6", "independent", accuracy=config["honest_accuracy"],
                  attestation="device"),
        )

    raise ValueError(f"unknown family {family}")


def build_witness(spec: WitnessSpec, attested: bool) -> Witness:
    """The policy's own view of a witness, once adoption has or has not reached it."""
    if attested:
        basis, identity = ATTESTATION_KINDS[spec.attestation]
        complete = spec.complete_when_attested
    else:
        basis, identity = DepthBasis.DECLARED, WitnessIdentity.ANONYMOUS
        complete = False
    if spec.identity_override is not None:
        identity = spec.identity_override
    if spec.complete_override is not None:
        complete = spec.complete_override
    return Witness(
        name=spec.wid,
        claimed=spec.claimed,
        depth_basis=basis,
        identity=identity,
        ancestry=frozenset((f"anc:{spec.wid}",) + spec.ancestry),
        markers=frozenset(spec.markers),
        ancestry_complete=complete,
    )


def _unit_fault_rate(config: Mapping[str, Any], unit: str) -> float:
    return float(config["unit_fault_rates"].get(unit, 0.0))


def _values(
    specs: tuple[WitnessSpec, ...], truth: bool, rng: random.Random, config: Mapping[str, Any]
) -> dict[str, bool]:
    units = sorted({s.unit for s in specs if s.role == "echo"})
    faulty = {unit: rng.random() < _unit_fault_rate(config, unit) for unit in units}
    out: dict[str, bool] = {}
    for spec in specs:
        if spec.role == "honest":
            out[spec.wid] = truth
        elif spec.role == "liar":
            out[spec.wid] = not truth
        elif spec.role == "echo":
            out[spec.wid] = (not truth) if faulty[spec.unit] else truth
        else:
            out[spec.wid] = truth if rng.random() < spec.accuracy else not truth
    return out


def _evidence(
    decision_id: str,
    witnesses: tuple[Witness, ...],
    values: Mapping[str, bool],
    cut_of: Mapping[str, str],
) -> tuple[DecisionEvidence, ...]:
    """One observation per witness, carrying its recorded ancestry and nothing else.

    Every witness carries its own lineage token, so no observation is
    unattributed. What the record does not carry is any token connecting two
    witnesses that share a hidden source -- which is the whole of DR3's case.
    """
    return tuple(
        DecisionEvidence(
            observation_id=f"{decision_id}|{w.name}",
            proposition_id=decision_id,
            value=values[w.name],
            roots={cut_of[token]: token for token in sorted(w.ancestry)},
            basis={cut_of[token]: LEGACY_BASIS for token in sorted(w.ancestry)},
        )
        for w in witnesses
    )


def _decision(
    config: Mapping[str, Any],
    campaign_id: str,
    index: int,
    family: str,
    specs: tuple[WitnessSpec, ...],
    witnesses: tuple[Witness, ...],
    cut_of: Mapping[str, str],
    ancestry_cuts: tuple[str, ...],
    rng: random.Random,
) -> Decision:
    decision_class = IRREVERSIBLE if index % 2 == 0 else REVERSIBLE
    threshold = config["decision_classes"][decision_class]
    truth = bool(rng.getrandbits(1))
    values = _values(specs, truth, rng, config)
    decision_id = f"{campaign_id}|d{index:02d}"
    evidence = _evidence(decision_id, witnesses, values, cut_of)
    unit_of = {s.wid: s.unit for s in specs}
    reference_units = tuple((f"{decision_id}|{s.wid}", unit_of[s.wid]) for s in specs)
    naive_units = tuple((f"{decision_id}|{s.wid}", s.wid) for s in specs)
    reference = settlement_over_units(evidence, reference_units, threshold)
    naive = settlement_over_units(evidence, naive_units, threshold)
    robustness = assess_dependence_robustness(evidence, threshold, ancestry_cuts)
    return Decision(
        decision_id=decision_id,
        index=index,
        truth=truth,
        threshold=threshold,
        decision_class=decision_class,
        values=tuple(sorted(values.items())),
        evidence=evidence,
        reference=reference,
        naive=naive,
        critical=reference != naive,
        robust_settlement=robustness.settlement if robustness.robust else None,
        contrary_value=truth if family == MINORITY_FAMILY else None,
    )


def generate_campaign(
    config: Mapping[str, Any], salt: str, family: str, variant: str, replicate: int, alpha: float
) -> Campaign:
    """One population of witnesses answering a sequence of decisions.

    The error class is not an input here. Which errors a pair is independent
    *for* is an arm-time question, so the same generated world is scored against
    every error class and the comparison is paired by construction.
    """
    rng = random.Random(_seed(salt, family, variant, replicate, alpha))
    campaign_id = f"{family}|{variant}|{replicate:05d}|a{alpha}"
    specs = layout(config, family, variant)
    attested = {
        spec.wid: bool(spec.attestable and rng.random() < alpha) for spec in specs
    }
    witnesses = tuple(build_witness(spec, attested[spec.wid]) for spec in specs)
    tokens = sorted({token for w in witnesses for token in w.ancestry})
    cut_of = {token: f"anc{index:02d}" for index, token in enumerate(tokens)}
    ancestry_cuts = tuple(cut_of[token] for token in tokens)
    reached = [attested[spec.wid] for spec in specs]
    decisions = tuple(
        _decision(config, campaign_id, index, family, specs, witnesses, cut_of,
                  ancestry_cuts, rng)
        for index in range(config["decisions_per_campaign"])
    )
    return Campaign(
        campaign_id=campaign_id,
        family=family,
        variant=variant,
        alpha=alpha,
        specs=specs,
        witnesses=witnesses,
        attested=tuple(sorted(attested.items())),
        unit_of=tuple((s.wid, s.unit) for s in specs),
        ancestry_cuts=ancestry_cuts,
        mixed_attestation=any(reached) and not all(reached),
        decisions=decisions,
    )


def error_classes(config: Mapping[str, Any]) -> tuple[ErrorClass, ...]:
    return tuple(ErrorClass[name] for name in config["error_classes"])


def cells(config: Mapping[str, Any]) -> tuple[tuple[float, ErrorClass], ...]:
    return tuple(
        (alpha, error)
        for alpha in config["adoption_rates"]
        for error in error_classes(config)
    )


def cell_key(alpha: float, error: ErrorClass) -> str:
    return f"alpha={alpha}|error={error.name}"


def iter_cell_campaigns(
    config: Mapping[str, Any], salt: str, campaigns_per_variant: int | None = None
) -> Iterable[tuple[str, ErrorClass, Campaign]]:
    count = (
        config["campaigns_per_variant"] if campaigns_per_variant is None else campaigns_per_variant
    )
    for family in config["families"]:
        for variant in VARIANTS[family]:
            for replicate in range(count):
                for alpha in config["adoption_rates"]:
                    campaign = generate_campaign(config, salt, family, variant, replicate, alpha)
                    for error in error_classes(config):
                        yield cell_key(alpha, error), error, campaign


def hidden_group_is_unrecorded(campaign: Campaign) -> bool:
    """No pair sharing a true unit shares anything the record carries.

    The construction claim behind DR3's case: at every ancestry cut and on every
    marker, two witnesses of one hidden source look exactly like two strangers.
    """
    unit_of = dict(campaign.unit_of)
    by_name = {w.name: w for w in campaign.witnesses}
    for left, right in itertools.combinations(sorted(by_name), 2):
        if not unit_of[left].startswith("hidden:"):
            continue
        if unit_of[left] != unit_of[right]:
            continue
        if by_name[left].ancestry & by_name[right].ancestry:
            return False
        if by_name[left].markers & by_name[right].markers:
            return False
    return True


def campaign_hash_row(cell: str, error: ErrorClass, campaign: Campaign) -> bytes:
    row = {
        "cell": cell,
        "error": error.name,
        "campaignId": campaign.campaign_id,
        "family": campaign.family,
        "variant": campaign.variant,
        "alpha": campaign.alpha,
        "attested": [list(pair) for pair in campaign.attested],
        "units": [list(pair) for pair in campaign.unit_of],
        "witnesses": [
            {
                "name": w.name,
                "claimed": w.claimed.name,
                "basis": w.depth_basis.name,
                "identity": w.identity.name,
                "admissible": w.admissible.name,
                "ancestry": sorted(w.ancestry),
                "markers": sorted(w.markers),
                "complete": w.ancestry_complete,
            }
            for w in campaign.witnesses
        ],
        "decisions": [
            {
                "id": d.decision_id,
                "truth": d.truth,
                "class": d.decision_class,
                "reference": d.reference,
                "naive": d.naive,
                "critical": d.critical,
                "robust": d.robust_settlement,
                "values": [list(pair) for pair in d.values],
            }
            for d in campaign.decisions
        ],
    }
    return (json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n").encode()


__all__ = [
    "Campaign",
    "Decision",
    "FAMILIES",
    "FREELY_ATTESTING_FAMILY",
    "HIDDEN_FAMILY",
    "MINORITY_FAMILY",
    "SETTLED",
    "UNSETTLED",
    "VARIANTS",
    "WitnessSpec",
    "build_witness",
    "campaign_hash_row",
    "cell_key",
    "cells",
    "error_classes",
    "generate_campaign",
    "hidden_group_is_unrecorded",
    "iter_cell_campaigns",
    "layout",
]
