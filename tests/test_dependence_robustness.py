"""Robustness over recorded possible dependence, checked against brute force.

The brute-force oracle enumerates every partition of the observations whose
blocks are connected through shared identities, and settles each one with the
same root-vote kernel ``provenance.decision_relative`` uses. The module must
report exactly the settlements that enumeration reaches.
"""

import random

import pytest

from provenance.decision_relative import (
    DecisionContext,
    DecisionContextError,
    DecisionEvidence,
    assess_decision,
)
from provenance.dependence_robustness import (
    SETTLED_TRUE,
    UNSETTLED,
    assess_dependence_robustness,
)


def _evidence(rows):
    """rows: (value, {cut: identity or None})"""
    return tuple(
        DecisionEvidence(
            observation_id=f"o{index}",
            proposition_id="p",
            value=value,
            roots=roots,
            basis={cut: "attested" for cut in roots},
        )
        for index, (value, roots) in enumerate(rows)
    )


def _settle_partition(records, blocks, threshold):
    block_of = {index: number for number, block in enumerate(blocks) for index in block}
    regrouped = tuple(
        DecisionEvidence(
            observation_id=item.observation_id,
            proposition_id="p",
            value=item.value,
            roots={"block": f"b{block_of[index]}"},
            basis={"block": "attested"},
        )
        for index, item in enumerate(records)
    )
    context = DecisionContext(
        decision_id="p",
        proposition_id="p",
        failure_domain="undisclosed",
        independence_cut="block",
        minimum_winning_roots=threshold,
        cut_selection_basis="unknown",
        candidate_cuts=("block",),
    )
    return assess_decision(regrouped, context).selected.settlement


def _partitions(items):
    if not items:
        yield []
        return
    first, rest = items[0], items[1:]
    for partition in _partitions(rest):
        for position in range(len(partition)):
            yield partition[:position] + [[first] + partition[position]] + partition[position + 1:]
        yield [[first]] + partition


def _connected(block, adjacent):
    seen, frontier = {block[0]}, [block[0]]
    while frontier:
        current = frontier.pop()
        for other in block:
            if other not in seen and other in adjacent[current]:
                seen.add(other)
                frontier.append(other)
    return len(seen) == len(block)


def _brute_force(records, cuts, threshold):
    adjacent = {i: set() for i in range(len(records))}
    for i, a in enumerate(records):
        for j, b in enumerate(records):
            if i != j and any(
                a.roots.get(cut) is not None and a.roots.get(cut) == b.roots.get(cut) for cut in cuts
            ):
                adjacent[i].add(j)
    return {
        _settle_partition(records, partition, threshold)
        for partition in _partitions(list(range(len(records))))
        if all(_connected(block, adjacent) for block in partition)
    }


def test_matches_brute_force_on_random_records():
    rng = random.Random(20260915)
    for _ in range(600):
        cuts = ("a", "b", "c")[: rng.randint(1, 3)]
        rows = []
        for _ in range(rng.randint(1, 6)):
            roots = {cut: rng.choice([None, "x", "y", "z", "w"]) for cut in cuts}
            if all(value is None for value in roots.values()):
                roots[cuts[0]] = rng.choice(["x", "y", "z", "w"])
            rows.append((rng.random() < 0.5, roots))
        threshold = rng.randint(1, 3)
        records = _evidence(rows)
        result = assess_dependence_robustness(records, threshold, cuts)
        expected = _brute_force(records, cuts, threshold)
        assert result.reachable_settlements == expected, (rows, threshold)
        assert result.robust == (len(expected) == 1)


def test_every_single_cut_reading_is_reachable():
    rng = random.Random(7)
    for _ in range(300):
        cuts = ("a", "b", "c")
        rows = [
            (rng.random() < 0.5, {cut: rng.choice(["x", "y", "z", "w"]) for cut in cuts})
            for _ in range(rng.randint(1, 7))
        ]
        threshold = rng.randint(1, 3)
        records = _evidence(rows)
        result = assess_dependence_robustness(records, threshold, cuts)
        for cut in cuts:
            context = DecisionContext(
                decision_id="p",
                proposition_id="p",
                failure_domain="undisclosed",
                independence_cut=cut,
                minimum_winning_roots=threshold,
                cut_selection_basis="unknown",
                candidate_cuts=(cut,),
            )
            assert assess_decision(records, context).selected.settlement in result.reachable_settlements


def test_stacked_dependence_that_every_cut_agrees_on_is_not_robust():
    """The DRI-2 false-settlement shape: reports 0 and 1 share an upstream
    component, 2 and 3 are independent but the upstream cut also merges them,
    and 4 is separate. True units: {0,1} true, 2 false, 3 false, 4 true, a 2-2 tie."""
    rows = [
        (True, {"agent": "a0", "controller": "c0", "upstream": "g0"}),
        (True, {"agent": "a1", "controller": "c1", "upstream": "g0"}),
        (False, {"agent": "a2", "controller": "c2", "upstream": "g1"}),
        (False, {"agent": "a3", "controller": "c3", "upstream": "g1"}),
        (True, {"agent": "a4", "controller": "c4", "upstream": "g2"}),
    ]
    records = _evidence(rows)
    cuts = ("agent", "controller", "upstream")
    for cut in cuts:
        context = DecisionContext("p", "p", "undisclosed", cut, 2, cut_selection_basis="unknown", candidate_cuts=cuts)
        assert assess_decision(records, context).selected.settlement == SETTLED_TRUE
    result = assess_dependence_robustness(records, 2, cuts)
    assert not result.robust and result.settlement is None
    assert UNSETTLED in result.reachable_settlements
    assert result.true_roots == (2, 3) and result.false_roots == (1, 2)


def test_genuinely_independent_evidence_is_robust():
    rows = [(value, {"agent": f"a{i}", "origin": f"o{i}"}) for i, value in enumerate([True, True, True, False])]
    result = assess_dependence_robustness(_evidence(rows), 2)
    assert result.robust and result.settlement == SETTLED_TRUE
    assert result.true_roots == (3, 3) and result.false_roots == (1, 1)


def test_a_shared_identity_across_sides_can_only_fail_closed():
    rows = [(True, {"origin": "o1"}), (True, {"origin": "o2"}), (False, {"origin": "o1"})]
    result = assess_dependence_robustness(_evidence(rows), 1)
    assert result.mixed_root_possible
    assert UNSETTLED in result.reachable_settlements and not result.robust


def test_unattributed_evidence_is_never_robust():
    rows = [(True, {"agent": "a1"}), (True, {"agent": "a2"}), (True, {"agent": None})]
    result = assess_dependence_robustness(_evidence(rows), 1)
    assert result.unattributed == 1 and not result.robust and result.settlement is None


def test_rejects_empty_evidence_and_bad_threshold():
    with pytest.raises(DecisionContextError):
        assess_dependence_robustness((), 1)
    with pytest.raises(ValueError):
        assess_dependence_robustness(_evidence([(True, {"agent": "a"})]), 0)
