"""Decision-relative independence over an unchanged evidence record.

This module is an ADAPTER, not part of the proved Minority Prophet kernel.
The kernel counts supplied roots. This adapter makes the previously implicit
choice of *which* supplied root identity is relevant to a decision explicit.

It does not discover causal structure, choose policy, grant authority, or erase
deeper lineage. A caller supplies a decision context and a root identifier for
each available cut (for example ``machine``, ``controller`` or
``evidence_origin``). Missing roots remain unattributed and therefore fail
closed under the existing root-vote policy when they could alter the outcome.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

from aggregation.root_vote import RootVerdict, Verdict, verdict

CUT_SELECTION_BASES = frozenset(
    {"preregistered", "rules-engine", "model-selected", "human-reviewed", "declared", "unknown"}
)


class DecisionContextError(ValueError):
    """The declared decision context cannot be evaluated as written."""


@dataclass(frozen=True)
class DecisionEvidence:
    """One observation with identity at zero or more lineage cuts.

    ``roots`` contains caller-supplied, auditable identities. Distinct strings
    are not proof of causal independence. ``basis`` records how each identity
    was established using the existing Minority Prophet vocabulary.
    """

    observation_id: str
    proposition_id: str
    value: bool
    roots: Mapping[str, str | None]
    basis: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.observation_id or not self.proposition_id:
            raise ValueError("observation_id and proposition_id are required")
        clean_roots = {
            str(cut).strip(): (str(root).strip() if root is not None else None)
            for cut, root in self.roots.items()
        }
        if any(not cut for cut in clean_roots):
            raise ValueError("root cut names must be non-empty")
        if any(root == "" for root in clean_roots.values()):
            raise ValueError("root identifiers must be non-empty when present")
        clean_basis = {str(cut).strip(): str(value).strip() for cut, value in self.basis.items()}
        object.__setattr__(self, "roots", MappingProxyType(clean_roots))
        object.__setattr__(self, "basis", MappingProxyType(clean_basis))


@dataclass(frozen=True)
class DecisionContext:
    """The policy facts required to select a proximal independence root.

    The context is declared by the caller; this module never infers that a cut
    is appropriate from the evidence it will be used to count.
    """

    decision_id: str
    proposition_id: str
    failure_domain: str
    independence_cut: str
    minimum_winning_roots: int
    consequence: str = "unspecified"
    reversibility: str = "unspecified"
    cut_selection_basis: str = "declared"
    candidate_cuts: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        required = {
            "decision_id": self.decision_id,
            "proposition_id": self.proposition_id,
            "failure_domain": self.failure_domain,
            "independence_cut": self.independence_cut,
            "cut_selection_basis": self.cut_selection_basis,
        }
        missing = [name for name, value in required.items() if not value.strip()]
        if missing:
            raise ValueError("decision context requires " + ", ".join(missing))
        if self.minimum_winning_roots < 1:
            raise ValueError("minimum_winning_roots must be at least 1")
        if self.cut_selection_basis not in CUT_SELECTION_BASES:
            raise ValueError("unsupported cut_selection_basis")
        candidates = tuple(dict.fromkeys((self.independence_cut, *self.candidate_cuts)))
        if any(not cut.strip() for cut in candidates):
            raise ValueError("candidate cuts must be non-empty")
        object.__setattr__(self, "candidate_cuts", candidates)


@dataclass(frozen=True)
class CutAssessment:
    """Root-vote output and settlement status at one explicit cut."""

    independence_cut: str
    root_verdict: RootVerdict
    winning_root_count: int
    settlement: str
    sufficient: bool


@dataclass(frozen=True)
class DecisionAssessment:
    """Selected result plus sensitivity to declared alternative cuts."""

    context: DecisionContext
    selected: CutAssessment
    alternatives: Mapping[str, CutAssessment]
    material_alternative_cuts: tuple[str, ...]
    count_sensitive_cuts: tuple[str, ...]

    @property
    def cut_is_material(self) -> bool:
        """Whether at least one declared alternative changes settlement."""
        return bool(self.material_alternative_cuts)


@dataclass(frozen=True)
class _CutClaim:
    value: bool
    root_id: str | None
    independence_basis: str | None


def _at_cut(
    evidence: tuple[DecisionEvidence, ...],
    cut: str,
    minimum_winning_roots: int,
) -> CutAssessment:
    claims = tuple(
        _CutClaim(
            value=item.value,
            root_id=item.roots.get(cut),
            independence_basis=item.basis.get(cut),
        )
        for item in evidence
    )
    root_result = verdict(claims, unattributed_policy="abstain_if_decisive")
    if root_result.verdict is Verdict.TRUE:
        winning_count = len(root_result.support_true)
    elif root_result.verdict is Verdict.FALSE:
        winning_count = len(root_result.support_false)
    else:
        winning_count = 0
    sufficient = (
        root_result.verdict is not Verdict.ABSTAIN and winning_count >= minimum_winning_roots
    )
    settlement = f"settled_{root_result.verdict.value}" if sufficient else "unsettled"
    return CutAssessment(
        independence_cut=cut,
        root_verdict=root_result,
        winning_root_count=winning_count,
        settlement=settlement,
        sufficient=sufficient,
    )


def assess_decision(
    evidence: Iterable[DecisionEvidence], context: DecisionContext
) -> DecisionAssessment:
    """Evaluate one evidence set through one declared decision context.

    Materiality is operational and narrow: an alternative cut is material when
    it changes the settlement among ``settled_true``, ``settled_false`` and
    ``unsettled``. A count change that does not cross the declared sufficiency
    standard is reported separately as count-sensitive, not verdict-material.
    """

    records = tuple(evidence)
    if not records:
        raise DecisionContextError("at least one evidence record is required")
    mismatched = sorted(
        item.observation_id for item in records if item.proposition_id != context.proposition_id
    )
    if mismatched:
        raise DecisionContextError(
            "decision proposition does not match evidence: " + ", ".join(mismatched)
        )
    duplicate_ids = sorted(
        observation_id
        for observation_id, count in Counter(item.observation_id for item in records).items()
        if count > 1
    )
    if duplicate_ids:
        raise DecisionContextError("duplicate observations: " + ", ".join(duplicate_ids))

    assessments = {
        cut: _at_cut(records, cut, context.minimum_winning_roots) for cut in context.candidate_cuts
    }
    selected = assessments[context.independence_cut]
    alternatives = MappingProxyType(
        {cut: result for cut, result in assessments.items() if cut != context.independence_cut}
    )
    material = tuple(
        cut for cut, result in alternatives.items() if result.settlement != selected.settlement
    )
    count_sensitive = tuple(
        cut
        for cut, result in alternatives.items()
        if result.settlement == selected.settlement
        and (
            len(result.root_verdict.support_true),
            len(result.root_verdict.support_false),
            result.root_verdict.unattributed,
        )
        != (
            len(selected.root_verdict.support_true),
            len(selected.root_verdict.support_false),
            selected.root_verdict.unattributed,
        )
    )
    return DecisionAssessment(
        context=context,
        selected=selected,
        alternatives=alternatives,
        material_alternative_cuts=material,
        count_sensitive_cuts=count_sensitive,
    )
