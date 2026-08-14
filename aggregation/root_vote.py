"""The aggregator the theorems are actually about, plus its guard rails.

`aggregation/semantic.evidence_root_vote` is NOT this function and must not be
described as the aggregator of formal/PROOFS.md. It is retained byte-identical
because `results/los-inspired-v0.1.manifest.json` binds its sha256 as canonical
evidence for EXPERIMENT-001; changing it would falsify a canonical record. Use
this module for new work. See formal/CLAIM-SCOPE.md.

Correspondence with the compiled proofs in formal/lean/:

    verdict(...).verdict        F
    verdict(...).margin         margin            (signed, true minus false)
    verdict(...).flip_budget    |margin|          (R3's first-class output)
    verdict(...).immunity_applicable  SideConsistent precondition of Theorem 1

Three behaviours here differ deliberately from `evidence_root_vote`, each
fixing a defect recorded in formal/COUNTEREXAMPLES.md:

CE-11  Duplicate root IDs carrying different assertions were resolved
       first-writer-wins, making the result depend on input ORDER in exactly
       the case where R2 is violated. Here a conflicting root is detected and
       the result fails closed.
CE-12  Claims with no root were discarded silently. Here they are counted,
       reported, and -- under the default policy -- force abstention when they
       could change the answer.
CE-02  The margin is reported in the unit the theorems use, together with the
       cost of the two distinct attack shapes, which differ by a factor of two.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Literal, Protocol


class IndependenceBasis(str, Enum):
    """How a root's independence was established.

    Vocabulary aligned byte-for-byte with `invention_engine.models.IndependenceBasis`
    so the two projects interoperate without translation. Ordered weakest to
    strongest by `RANK` below.

    Minority Prophet had no such concept before 2026-08-13: a root was a root,
    and `flip_budget` counted an attested observation and an anonymous assertion
    identically. The cross-project conformance experiment MP-IG-CONFORMANCE-001
    made that visible -- Invention Graph fed roots in as DECLARED and UNKNOWN,
    and nothing about that survived into the verdict.

    Nothing in formal/lean/ is wrong about this. T4 and T5 count roots, and they
    are correct to. But they say nothing about how hard each root is to forge,
    and an adversary who need only DECLARE faces a smaller budget than one who
    must defeat ATTESTATION. A single flip_budget over mixed roots therefore
    overstates the cost of attack.
    """

    ATTESTED = "attested"
    DECLARED = "declared"
    INFERRED = "inferred"
    UNKNOWN = "unknown"


BASIS_RANK: dict[IndependenceBasis, int] = {
    IndependenceBasis.UNKNOWN: 0,
    IndependenceBasis.INFERRED: 1,
    IndependenceBasis.DECLARED: 2,
    IndependenceBasis.ATTESTED: 3,
}


class Verdict(str, Enum):
    TRUE = "true"
    FALSE = "false"
    ABSTAIN = "abstain"


class RootedClaim(Protocol):
    value: bool
    root_id: str | None
    # Optional. Absent means UNKNOWN -- the conservative reading, since a claim
    # that does not say how its independence was established has not established
    # it. Existing callers keep working and are simply reported as unknown.
    independence_basis: str | None


UnattributedPolicy = Literal["abstain_if_decisive", "ignore", "treat_as_root"]


@dataclass(frozen=True)
class RootVerdict:
    verdict: Verdict
    support_true: frozenset[str]
    support_false: frozenset[str]
    margin: int
    """Signed: |S_true| - |S_false|. This is the theorems' `margin`."""
    flip_budget: int
    """|margin|. Units of NET PER-SIDE ROOT CHANGE (p0 - p1), not incidents."""
    conversions_to_reverse: int
    """Cheapest number of side CONVERSIONS that reverses this verdict.

    A conversion moves one root from the winning side to the losing side and is
    worth TWO units of `flip_budget`, so this is roughly half of it. Reporting
    only `flip_budget` overstates the attacker's cost by ~2x (CE-03).
    """
    abstention_reachable_by_conversion: bool
    """False at odd margin: conversions preserve the margin's parity, so they
    cannot produce a tie and must overshoot into full reversal. Proved as
    `no_abstention_of_odd_margin`."""
    unattributed: int
    conflicting_roots: frozenset[str]
    basis_counts: dict[str, int]
    """Roots per independence basis, over the roots that decided this verdict."""
    weakest_basis: str
    """The weakest basis among counted roots. The margin is only as trustworthy
    as this, whatever `flip_budget` says."""
    attested_margin: int
    """Signed margin counting ATTESTED roots ONLY.

    This is the margin that survives an adversary who can forge declarations but
    not attestations. When it disagrees in sign with `margin`, the decisive
    evidence is unattested and `flip_budget` is not a security budget -- it is a
    headcount. Reporting both is the point; reporting only `margin` is what this
    field exists to stop."""
    immunity_applicable: bool
    """False means Theorem 1 says NOTHING about this input. It is not a claim
    that the verdict is wrong -- it is the absence of a guarantee."""
    notes: tuple[str, ...] = field(default_factory=tuple)


def _basis_of(claim: RootedClaim) -> IndependenceBasis:
    """A claim that does not say how its independence was established has not
    established it. Absent, unrecognised and explicitly-unknown all read as
    UNKNOWN, which is the conservative direction."""
    raw = getattr(claim, "independence_basis", None)
    if raw is None:
        return IndependenceBasis.UNKNOWN
    try:
        return IndependenceBasis(str(raw))
    except ValueError:
        return IndependenceBasis.UNKNOWN


def _sides(
    claims: Iterable[RootedClaim], *, promote_unattributed: bool
) -> tuple[dict[str, set[bool]], int, dict[str, IndependenceBasis], dict[str, bool]]:
    """Map root id -> set of assertions made on it, plus unattributed count.

    Collecting a SET of assertions per root, rather than keeping the first one
    seen, is what makes the result order-independent (CE-11).
    """
    by_root: dict[str, set[bool]] = {}
    basis: dict[str, IndependenceBasis] = {}
    values: dict[str, bool] = {}
    unattributed = 0
    for claim in claims:
        root_id = getattr(claim, "root_id", None)
        if root_id is None:
            unattributed += 1
            if not promote_unattributed:
                continue
            root_id = f"__unattributed_{unattributed}"
        by_root.setdefault(root_id, set()).add(bool(claim.value))
        values[root_id] = bool(claim.value)
        # Two claims on one root may disagree about its basis. Take the WEAKER:
        # a root is only as independently established as its weakest supporting
        # account of it.
        seen = _basis_of(claim)
        if root_id not in basis or BASIS_RANK[seen] < BASIS_RANK[basis[root_id]]:
            basis[root_id] = seen
    return by_root, unattributed, basis, values


def verdict(
    claims: Iterable[RootedClaim],
    *,
    unattributed_policy: UnattributedPolicy = "abstain_if_decisive",
) -> RootVerdict:
    """Count distinct evidence roots per side and compare.

    `unattributed_policy` decides what a claim with no recorded root means. The
    repository previously contained BOTH of the rejected answers, in different
    modules, with no decision recorded (ledger U2):

      "abstain_if_decisive"  (default, fail closed) -- unattributed claims are
          not roots, but if there are enough of them to change the outcome the
          result abstains and says so. Choosing this default is a policy
          decision, not a theorem.
      "ignore"        -- drop them, as `semantic.evidence_root_vote` does.
          Understates risk: an undetected copy has zero influence here.
      "treat_as_root" -- each becomes its own root, as formal/PROOFS.md's model
          implies. Overstates support: an undetected copy has full influence.
    """
    by_root, unattributed, basis, values = _sides(
        claims, promote_unattributed=unattributed_policy == "treat_as_root"
    )

    conflicting = frozenset(r for r, vals in by_root.items() if len(vals) > 1)
    support_true = frozenset(r for r, vals in by_root.items() if vals == {True})
    support_false = frozenset(r for r, vals in by_root.items() if vals == {False})

    counted = support_true | support_false
    basis_counts: dict[str, int] = {}
    for root in counted:
        key = basis.get(root, IndependenceBasis.UNKNOWN).value
        basis_counts[key] = basis_counts.get(key, 0) + 1
    weakest = min(
        (basis.get(r, IndependenceBasis.UNKNOWN) for r in counted),
        key=lambda b: BASIS_RANK[b],
        default=IndependenceBasis.UNKNOWN,
    ).value
    attested = [r for r in counted
                if basis.get(r, IndependenceBasis.UNKNOWN) is IndependenceBasis.ATTESTED]
    attested_margin = (sum(1 for r in attested if values.get(r))
                       - sum(1 for r in attested if not values.get(r)))

    notes: list[str] = []
    s1, s0 = len(support_true), len(support_false)

    if unattributed_policy == "treat_as_root":
        notes.append(
            f"{unattributed} unattributed claim(s) counted as independent roots "
            "(treat_as_root); this is the most permissive reading"
        )
    elif unattributed_policy == "ignore" and unattributed:
        notes.append(f"{unattributed} unattributed claim(s) discarded (ignore)")

    margin = s1 - s0
    flip_budget = abs(margin)

    if conflicting:
        notes.append(
            f"{len(conflicting)} root(s) carry conflicting assertions: "
            + ", ".join(sorted(conflicting))
            + " -- R2 (side separation) is violated; failing closed"
        )
        return RootVerdict(
            verdict=Verdict.ABSTAIN,
            support_true=support_true,
            support_false=support_false,
            margin=margin,
            flip_budget=flip_budget,
            conversions_to_reverse=flip_budget // 2 + 1,
            abstention_reachable_by_conversion=flip_budget % 2 == 0,
            unattributed=unattributed,
            conflicting_roots=conflicting,
            basis_counts=basis_counts,
            weakest_basis=weakest,
            attested_margin=attested_margin,
            immunity_applicable=False,
            notes=tuple(notes),
        )

    if margin != 0 and attested_margin == 0:
        notes.append(
            f"margin {margin} rests on no attested root (weakest basis: {weakest}); "
            "flip_budget is a headcount here, not a security budget"
        )
    elif margin != 0 and (attested_margin > 0) != (margin > 0):
        notes.append(
            f"margin {margin} and attested_margin {attested_margin} disagree in sign: "
            "the decisive evidence is unattested"
        )

    decided = Verdict.TRUE if margin > 0 else (Verdict.FALSE if margin < 0 else Verdict.ABSTAIN)

    if (
        unattributed_policy == "abstain_if_decisive"
        and unattributed >= flip_budget
        and decided is not Verdict.ABSTAIN
    ):
        notes.append(
            f"{unattributed} unattributed claim(s) >= flip budget {flip_budget}: "
            "they could change this verdict, so it is withheld (abstain_if_decisive)"
        )
        decided = Verdict.ABSTAIN

    return RootVerdict(
        verdict=decided,
        support_true=support_true,
        support_false=support_false,
        margin=margin,
        flip_budget=flip_budget,
        conversions_to_reverse=flip_budget // 2 + 1,
        abstention_reachable_by_conversion=flip_budget % 2 == 0,
        unattributed=unattributed,
        conflicting_roots=conflicting,
        basis_counts=basis_counts,
        weakest_basis=weakest,
        attested_margin=attested_margin,
        immunity_applicable=True,
        notes=tuple(notes),
    )


def tolerated_root_errors(result: RootVerdict) -> int:
    """How many UNITS of root-set change this verdict provably survives.

    Compiled as `root_error_tolerance`. The hypothesis that assertions do not
    change is essential and is not checkable from this result alone.

    This is NOT a number of operational incidents. One deleted claim record
    orphans every child at once, and one compromised signing key mints
    unboundedly many roots (CE-04, CE-05). Converting units into incidents
    requires a roots-per-identity bound, which is R1.4 in
    PROVENANCE-REQUIREMENTS.md and is not enforced by this library.
    """
    return max(result.flip_budget - 1, 0)
