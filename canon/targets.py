"""Two corrections from owner review, both structural.

**1. A rung is not a property of a procedure. It is a property of a
(procedure, proposition) pair.**

The four "contested" assignments were not close calls. They were one missing
parameter. Retrieving an original contract is *going to the world* if the claim
is "the contract says X" — the document is the world for that claim. It is a
mere record if the claim is "the payment was made". Querying a second model is
direct observation if the claim is about model behaviour, and hearsay if the
claim is about reality. Same act, different depth, decided by what is being
measured.

**2. Witnessing and attesting are different axes, and the ladder had only one.**

Peer review is not a witness. It is a *testament*. It adds no observation of the
world, yet it is plainly more than one more person re-reading the text — an
independent party took an action and put their name to it. Forcing that onto the
witness ladder loses the information; giving it its own axis keeps it.

The two axes compose without mixing:

* **Witness depth** sets `N_eff` — how many independent observations exist.
* **Attestation** never adds a witness. It lowers the *margin* required on top
  of `N_eff`, because margin exists to absorb undetected dependence (R3), and an
  independent party putting their name to the chain is exactly what makes
  undetected laundering less likely.

So peer review cannot manufacture evidence, and does not count for nothing. That
is the correct shape, and it is the shape the owner described.
"""

from __future__ import annotations

from enum import Enum, IntEnum

from canon.proximity import Rung


class Target(Enum):
    """What the proposition is *about*. Fixes the rung of every procedure."""

    WORLD = "world"                    # physical or social fact
    DOCUMENT = "document"              # what a specific artifact says
    MODEL_BEHAVIOR = "model-behavior"  # what a model outputs
    PROCESS = "process"                # whether a procedure was followed


class Attestation(IntEnum):
    """Who vouched, and how disinterested they were. Never adds a witness."""

    NONE = 0
    SELF = 1          # the author vouches for their own work
    INTERNAL = 2      # same organisation or control domain
    INDEPENDENT = 3   # separate party with no stake in the outcome
    ADVERSARIAL = 4   # a party actively trying to find fault


#: (procedure, target) -> rung. Absence means the procedure is undefined for
#: that target and must be refused, not guessed.
RUNG_BY_TARGET: dict[tuple[str, Target], Rung] = {
    # Retrieving an original artifact: the document IS the world for a claim
    # about the document, and only a raw record for a claim about events.
    ("retrieved-original-document", Target.DOCUMENT): Rung.REALITY,
    ("retrieved-original-document", Target.WORLD): Rung.RAW,
    ("retrieved-original-document", Target.PROCESS): Rung.RAW,

    # Querying a model: direct observation of model behaviour; hearsay about
    # anything else, and correlated hearsay at that.
    ("second-model-reviewing-first-model", Target.MODEL_BEHAVIOR): Rung.REALITY,
    ("second-model-reviewing-first-model", Target.WORLD): Rung.TEXT,
    ("second-model-reviewing-first-model", Target.DOCUMENT): Rung.TEXT,
    ("model-reasoning-over-given-context", Target.MODEL_BEHAVIOR): Rung.REALITY,
    ("model-reasoning-over-given-context", Target.WORLD): Rung.TEXT,

    # Peer review observes the manuscript and the process, never the world.
    ("peer-review", Target.WORLD): Rung.TEXT,
    ("peer-review", Target.DOCUMENT): Rung.RAW,
    ("peer-review", Target.PROCESS): Rung.METHOD,

    # A second lab running the same protocol is a real measurement of the world
    # and a strong statement about the protocol's reproducibility.
    ("different-lab-same-protocol", Target.WORLD): Rung.REPLICATION,
    ("different-lab-same-protocol", Target.PROCESS): Rung.REALITY,
}

#: Attestation strength. Independent of witness depth, by construction.
ATTESTATION: dict[str, Attestation] = {
    "original-experiment": Attestation.SELF,
    "peer-review": Attestation.INDEPENDENT,
    "different-lab-same-protocol": Attestation.INDEPENDENT,
    "retrieved-original-document": Attestation.NONE,
    "citation": Attestation.NONE,
    "reliance-on-prior-auditor-report": Attestation.INTERNAL,
    "third-party-confirmation": Attestation.INDEPENDENT,
    "model-reasoning-over-given-context": Attestation.SELF,
    "second-model-reviewing-first-model": Attestation.INTERNAL,
    "adversarial-red-team-review": Attestation.ADVERSARIAL,
}


class TargetUndefined(KeyError):
    """The procedure has no defined depth for this proposition. Refuse."""


def rung_for(procedure: str, target: Target) -> Rung:
    """Depth of a procedure *for a given proposition*.

    Falls back to the target-independent table in ``canon.rungs`` when the
    procedure's depth genuinely does not vary with the target — an experiment
    observes the world whatever you are asking about.
    """
    key = (procedure, target)
    if key in RUNG_BY_TARGET:
        return RUNG_BY_TARGET[key]
    from canon.rungs import BY_NAME
    if procedure in BY_NAME:
        return BY_NAME[procedure].rung
    raise TargetUndefined(
        f"{procedure!r} has no assigned depth for target {target.value!r}; "
        "assign it and publish before drawing a sample (ASSAYER A3)."
    )


def attestation_of(procedure: str) -> Attestation:
    """Attestation strength. Returns NONE for anything unlisted — absence of a
    testament is not a testament."""
    return ATTESTATION.get(procedure, Attestation.NONE)


def required_margin(base_margin: int, attestations: list[Attestation]) -> int:
    """Margin required on top of `N_eff`, reduced by independent attestation.

    Attestation **never** increases `N_eff`; it reduces the buffer R3 holds
    against *undetected* dependence, because an independent party naming itself
    on the chain makes silent laundering less likely.

    Self-attestation reduces nothing — that is the bootstrap. Only attestation
    from outside the control domain counts, and it saturates: a testament
    lowers the floor, it never removes it.
    """
    if base_margin <= 1:
        return base_margin
    best = max(attestations, default=Attestation.NONE)
    if best <= Attestation.SELF:
        return base_margin
    reduction = {Attestation.INTERNAL: 0,
                 Attestation.INDEPENDENT: 1,
                 Attestation.ADVERSARIAL: 2}[best]
    return max(1, base_margin - reduction)
