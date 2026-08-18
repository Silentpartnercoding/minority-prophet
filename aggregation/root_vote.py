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

ClaimShape = Literal["symmetric", "universal", "existential"]
"""Which question the roots are being counted to answer.

`symmetric` -- "which side has more independent evidence?" Both sides can win by
    accumulating roots. This is every synthetic world in the programme and every
    proposition the compiled theorems are about.
`universal` -- "does EVERY member of a scope satisfy P?" One counterexample root
    settles it against, whatever the confirming count. Counting is the wrong
    operation and this function REFUSES it (CE-14).
`existential` -- "does ANY member of a scope satisfy P?" The mirror: one verified
    root settles it FOR, and roots reporting an unsuccessful search are absence
    of evidence, not evidence of absence. They cannot out-vote a find. Counting
    is wrong in the opposite direction and is REFUSED for the same reason.

This is a DECLARATION BY THE CALLER, not a detection. Nothing in a claim
iterable reveals which question it answers, so a caller who mislabels a
universal claim as symmetric gets the wrong answer and this fence does not
catch it. The fence converts a silent wrong answer into a loud one for callers
who say what they are asking; it is not a classifier.
"""


class AsymmetricClaimError(ValueError):
    """Raised when an asymmetric claim is passed to the counting aggregator.

    CE-14: handed 999 confirmations and one ATTESTED counterexample, this
    function returns `true` with margin 998 and `immunity_applicable=True`. The
    counting is correct; counting is simply not how an asymmetric claim is
    decided. For the universal direction,
    `knowledge_ledger.evaluate_transaction_v2` answers correctly today as an
    `absence` claim. For the existential direction its `presence` branch also
    counts -- see CE-14's mirror note, which is an open semantic question
    rather than a settled defect.
    """


UniversalClaimError = AsymmetricClaimError
"""Retained name. The universal direction was found first; the fence covers
both directions and the error is one type."""


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
    claim_shape: ClaimShape = "symmetric",
) -> RootVerdict:
    """Count distinct evidence roots per side and compare.

    `claim_shape` declares which question is being asked. `universal` raises
    `UniversalClaimError`: one counterexample settles such a claim regardless of
    the confirming count, so no margin over root counts answers it (CE-14). The
    default is `symmetric` because that is what every existing caller asks and
    what the compiled theorems cover -- it is not a claim that an undeclared
    proposition has been checked.

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
    if claim_shape == "universal":
        raise AsymmetricClaimError(
            "a universal claim is settled by one counterexample root, not by a "
            "margin over root counts; this function counts and would report the "
            "confirming side (CE-14). Use "
            "knowledge_ledger.transaction_v2.evaluate_transaction_v2 with "
            "claim.type='absence', or aggregation.root_vote.asymmetric_verdict, "
            "which implements the compiled rule (AC1-AC5)."
        )
    if claim_shape == "existential":
        raise AsymmetricClaimError(
            "an existential claim is settled by one verified root, not by a "
            "margin over root counts; roots reporting an unsuccessful search "
            "are absence of evidence and cannot out-vote a find (CE-14 mirror "
            "note). Use aggregation.root_vote.asymmetric_verdict, which "
            "implements the compiled rule (AC1-AC5); evaluate_transaction_v2's "
            "'presence' branch counts and does not decide this shape."
        )

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


# ---------------------------------------------------------------------------
# Asymmetric claims (CE-14). The rule implemented here is COMPILED, not
# proposed: `formal/lean/MinorityProphetCore/Asymmetric.lean`, ledger AC1-AC5.
#
# It is a SEPARATE FUNCTION rather than a mode of `verdict`, mirroring the Lean,
# where `universalF` and `existentialF` are separate definitions from `F` and
# not special cases of it. `verdict` keeps refusing these shapes, because it is
# proved that counting does not answer them.
# ---------------------------------------------------------------------------


class AsymmetricOutcome(str, Enum):
    """Outcomes for claims whose falsifier or verifier is singular.

    REFUTED / NOT_REFUTED     -- universal claims ("every member satisfies P")
    ESTABLISHED / NOT_ESTABLISHED -- existential claims ("some member does")
    INDETERMINATE             -- a precondition of the compiled rule failed.
        NO THEOREM COVERS THIS OUTCOME. The Lean assumes side-consistency and
        an attributed root set; this is what the implementation does when those
        hypotheses do not hold, and it fails closed rather than guessing.
    """

    REFUTED = "refuted"
    NOT_REFUTED = "not_refuted"
    ESTABLISHED = "established"
    NOT_ESTABLISHED = "not_established"
    INDETERMINATE = "indeterminate"


@dataclass(frozen=True)
class AsymmetricVerdict:
    """The result of a rule that reads ONE side and ignores the other.

    There is deliberately no `margin`, no `flip_budget` and no
    `conversions_to_reverse`. AC2 proves the outcome does not read the other
    side at all, so a margin over both sides is not an input to this decision
    and reporting one would invite exactly the misreading CE-14 records.
    """

    outcome: AsymmetricOutcome
    claim_shape: ClaimShape
    decisive_roots: frozenset[str]
    """The roots that carry the outcome. AC1: one is enough."""
    ignored_root_count: int
    """Roots on the other side. Reported so the indifference is VISIBLE rather
    than merely true; this number had no influence on `outcome` (AC2)."""
    roots_to_reverse: int
    """Roots that must be removed or added to change `outcome`. For a positive
    outcome, every decisive root must go; for a negative one, a single new root
    suffices. This replaces `flip_budget`, which is not defined here."""
    unattributed: int
    conflicting_roots: frozenset[str]
    weakest_basis: str
    """Weakest independence basis among the DECISIVE roots. A refutation resting
    on one UNKNOWN root is one assertion, not a proof."""
    notes: tuple[str, ...] = field(default_factory=tuple)


_DECISIVE_SIDE: dict[str, bool] = {"universal": False, "existential": True}
"""Which assertion carries the outcome. For a universal claim it is the
counterexample (False); for an existential claim it is the find (True)."""


def asymmetric_verdict(
    claims: Iterable[RootedClaim],
    *,
    claim_shape: ClaimShape,
) -> AsymmetricVerdict:
    """Decide a universal or existential claim from its decisive side alone.

    Implements `universalF` / `existentialF` (AC1-AC5). One decisive root
    settles the claim regardless of how many roots assert the other side.

    `NOT_REFUTED` IS NOT "PROVED". This function has no search-coverage input,
    so it cannot distinguish "the scope was searched and nothing was found" from
    "nothing was found yet". Only `knowledge_ledger` can, because only it
    carries a search ledger. Read alone, `NOT_REFUTED` means exactly "no
    counterexample root is present here". The same applies to
    `NOT_ESTABLISHED`.
    """
    if claim_shape == "symmetric":
        raise ValueError(
            "symmetric claims are decided by counting roots per side; use "
            "aggregation.root_vote.verdict"
        )
    if claim_shape not in _DECISIVE_SIDE:
        raise ValueError(f"unknown claim_shape: {claim_shape!r}")

    decisive_value = _DECISIVE_SIDE[claim_shape]
    by_root, unattributed, basis, values = _sides(claims, promote_unattributed=False)

    conflicting = frozenset(r for r, vals in by_root.items() if len(vals) > 1)
    decisive = frozenset(r for r, vals in by_root.items() if vals == {decisive_value})
    ignored = frozenset(r for r, vals in by_root.items() if vals == {not decisive_value})

    notes: list[str] = []
    positive = AsymmetricOutcome.REFUTED if claim_shape == "universal" \
        else AsymmetricOutcome.ESTABLISHED
    negative = AsymmetricOutcome.NOT_REFUTED if claim_shape == "universal" \
        else AsymmetricOutcome.NOT_ESTABLISHED

    def _weakest(roots: frozenset[str]) -> str:
        return min((basis.get(r, IndependenceBasis.UNKNOWN) for r in roots),
                   key=lambda b: BASIS_RANK[b],
                   default=IndependenceBasis.UNKNOWN).value

    if conflicting:
        # R2 (side separation) fails, which is a hypothesis of the compiled
        # rule. Outside the theorem; fail closed.
        notes.append(
            f"{len(conflicting)} root(s) carry conflicting assertions: "
            + ", ".join(sorted(conflicting))
            + " -- R2 (side separation) is violated, which the compiled rule "
            "assumes; failing closed"
        )
        return AsymmetricVerdict(
            outcome=AsymmetricOutcome.INDETERMINATE,
            claim_shape=claim_shape,
            decisive_roots=decisive,
            ignored_root_count=len(ignored),
            roots_to_reverse=0,
            unattributed=unattributed,
            conflicting_roots=conflicting,
            weakest_basis=_weakest(decisive),
            notes=tuple(notes),
        )

    if decisive:
        # AC1: one decisive root settles it, whatever the other side holds.
        # Unattributed claims cannot undo this -- nothing un-refutes a claim.
        if ignored:
            notes.append(
                f"{len(ignored)} root(s) assert the other side and did not "
                "influence this outcome (AC2: the verdict does not read them)"
            )
        weakest = _weakest(decisive)
        if weakest != IndependenceBasis.ATTESTED.value:
            notes.append(
                f"decisive evidence rests on a {weakest} root; a singular "
                "falsifier is only as strong as its weakest decisive root"
            )
        return AsymmetricVerdict(
            outcome=positive,
            claim_shape=claim_shape,
            decisive_roots=decisive,
            ignored_root_count=len(ignored),
            roots_to_reverse=len(decisive),
            unattributed=unattributed,
            conflicting_roots=conflicting,
            weakest_basis=weakest,
            notes=tuple(notes),
        )

    # No decisive root. Here unattributed claims DO matter: one of them could be
    # the decisive root, and a single one is enough to flip the outcome.
    if unattributed:
        notes.append(
            f"{unattributed} unattributed claim(s) present and no decisive root "
            "found; a single unattributed claim on the decisive side would "
            "settle this claim, so the outcome is withheld"
        )
        return AsymmetricVerdict(
            outcome=AsymmetricOutcome.INDETERMINATE,
            claim_shape=claim_shape,
            decisive_roots=decisive,
            ignored_root_count=len(ignored),
            roots_to_reverse=1,
            unattributed=unattributed,
            conflicting_roots=conflicting,
            weakest_basis=_weakest(decisive),
            notes=tuple(notes),
        )

    notes.append(
        "no decisive root is present. This is NOT a proof of the claim: this "
        "function has no search-coverage input and cannot distinguish a "
        "searched scope from an unsearched one. Use knowledge_ledger for that."
    )
    return AsymmetricVerdict(
        outcome=negative,
        claim_shape=claim_shape,
        decisive_roots=decisive,
        ignored_root_count=len(ignored),
        roots_to_reverse=1,
        unattributed=unattributed,
        conflicting_roots=conflicting,
        weakest_basis=_weakest(decisive),
        notes=tuple(notes),
    )
