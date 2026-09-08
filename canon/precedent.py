"""No threshold. A three-outcome gate and accumulated precedent.

The previous position -- that one irreducible number was owed by the owner, the
false-allow/false-deny exchange rate -- was wrong, and owner review is what
showed it. The argument was: every case differs, the laws already pin the
extremes, the gate can reroute, and human escalation exists. All true, and
together they remove the need for a threshold entirely.

**A threshold is only needed by a gate with two outcomes.** Forced to answer
`allow` or `deny` on every case, something must adjudicate the undetermined
middle, and that something is a preference. Give the gate a third outcome and
the requirement disappears: cases the laws determine are decided by the laws,
and cases they do not determine are escalated rather than guessed.

What the laws determine without any preference at all:

* **DENY** -- bounds not establishable (L8), authority expanded (L1),
  unresolved authenticated conflict (L7), world state unverified, or zero
  independent witnesses against the error class that governs the claim.
* **ALLOW** -- the case *dominates* an already-allowed precedent on every axis.
* **DENY** -- the case is *dominated by* an already-denied precedent on every axis.
* **ESCALATE** -- otherwise.

Dominance is a partial order, never a score: at least as many independent
witnesses against every class of error, at least as reversible, no more tail
risk, no more loss. Nothing is traded off against anything, because trading off
is exactly the step that requires a preference.

This is how law handles the identical problem, and it is the same borrowing that
produced proximate cause. Nobody legislates a numeric threshold for negligence.
Cases are decided, reasons are recorded, and the determined region grows. The
preference still enters -- through decided cases -- but it enters *visibly*,
attached to facts and reasons, and it can be overturned. A number chosen in
advance has none of those properties.

Two honest consequences:

* **Cold start.** With no precedent, everything undetermined escalates. That is
  correct behaviour, not a defect, and it is why the escalation rate is a metric
  rather than a threshold: it is *measured*, and it falls as case law
  accumulates.
* **The escalation rate is the real question**, and it is discovered rather than
  decided. If it settles at 2%, the system works. If it settles at 60%, the
  system is useless and the answer is more precedent or better evidence -- not a
  looser number.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from canon.proximity import ErrorClass


class Outcome(Enum):
    ALLOW = "allow"
    DENY = "deny"
    ESCALATE = "escalate"


@dataclass(frozen=True)
class Case:
    """A proposed action, described only in terms the laws can compare."""

    name: str
    #: N_eff against each class of error -- the profile, never a single number.
    witnesses: dict[ErrorClass, int]
    reversibility: float                 # Rev(e) in [0, 1]
    tail_risk: float                     # CVaR-style; lower is safer
    max_loss: float | None               # None means unbounded -> L8 denial
    bounds_established: bool = True
    authority_expanded: bool = False
    conflict_unresolved: bool = False
    world_verified: bool = True
    #: The error class that actually governs this claim.
    governing_error: ErrorClass = ErrorClass.FABRICATION

    def at_least_as_safe_as(self, other: "Case") -> bool:
        """Partial order. No axis is traded against another."""
        return (
            all(self.witnesses.get(e, 0) >= other.witnesses.get(e, 0)
                for e in ErrorClass)
            and self.reversibility >= other.reversibility
            and self.tail_risk <= other.tail_risk
            and (other.max_loss is None
                 or (self.max_loss is not None and self.max_loss <= other.max_loss))
        )


@dataclass(frozen=True)
class Precedent:
    """A case a human decided, with the reasoning attached."""

    case: Case
    outcome: Outcome
    reason: str
    decided_by: str


@dataclass
class PrecedentGate:
    """Three-outcome gate. Never invents an answer it was not given."""

    precedents: list[Precedent] = field(default_factory=list)
    escalations: int = 0
    decisions: int = 0

    # -- what the laws settle with no preference whatsoever ----------------
    def _hard_denial(self, case: Case) -> str | None:
        if case.authority_expanded:
            return "authority-expanded"
        if case.conflict_unresolved:
            return "unresolved-authority-conflict"
        if not case.world_verified:
            return "world-state-unverified"
        if not case.bounds_established or case.max_loss is None:
            return "unbounded-undertaking"
        if case.witnesses.get(case.governing_error, 0) < 1:
            return "no-independent-witness-against-governing-error"
        return None

    def decide(self, case: Case) -> tuple[Outcome, str]:
        self.decisions += 1

        hard = self._hard_denial(case)
        if hard is not None:
            return Outcome.DENY, hard

        for p in self.precedents:
            if p.outcome is Outcome.ALLOW and case.at_least_as_safe_as(p.case):
                return Outcome.ALLOW, f"dominates-allowed-precedent:{p.case.name}"

        for p in self.precedents:
            if p.outcome is Outcome.DENY and p.case.at_least_as_safe_as(case):
                return Outcome.DENY, f"dominated-by-denied-precedent:{p.case.name}"

        self.escalations += 1
        return Outcome.ESCALATE, "undetermined-by-law-and-precedent"

    def record(self, case: Case, outcome: Outcome, reason: str, decided_by: str) -> None:
        """Record a human decision. The determined region grows from here."""
        if outcome is Outcome.ESCALATE:
            raise ValueError("an escalation is not a decision; record the resolution")
        if not reason.strip():
            raise ValueError("a precedent without a recorded reason is not a precedent")
        self.precedents.append(Precedent(case, outcome, reason, decided_by))

    @property
    def escalation_rate(self) -> float:
        """The metric that replaces the threshold. Measured, not chosen."""
        return self.escalations / self.decisions if self.decisions else 0.0
