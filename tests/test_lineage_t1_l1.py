"""LIN-000 permanent tests: Theorem 1 and Lemma 1, end-to-end, in the
lineage-bearing schema (research/knowledge-ledger/lineage/REGISTRATION.md).

Live small-scale checks plus validation of the committed confirmatory
result against the registered expectations."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LIN = REPO / "research" / "knowledge-ledger" / "lineage"
sys.path.insert(0, str(LIN))

import lineage  # noqa: E402

RESULT = json.loads((LIN / "results" / "lin000-result.json").read_text())


def test_declared_count_is_derivable_and_matches_the_result():
    assert lineage.declared_exhaustive_count(6) == 50362
    assert RESULT["declaredExhaustiveCount"] == 50362
    assert RESULT["phases"]["exhaustive"]["worlds"] == 50362
    assert RESULT["phases"]["exhaustive"]["countMatchesDeclared"] is True


def test_t1_holds_live_on_the_exhaustive_prefix():
    """Every valid single reparenting of every side-consistent world with
    k <= 4 leaves S0, S1 and the verdict unchanged -- live, not archived."""
    checked = 0
    for world in lineage.exhaustive_worlds(4):
        if not lineage.is_side_consistent(world):
            continue
        base = (lineage.s_sets(world), lineage.verdict(world))
        for rewired in lineage.valid_reparentings(world):
            checked += 1
            assert (lineage.s_sets(rewired), lineage.verdict(rewired)) == base
    assert checked > 0


def test_t1_protection_does_not_extend_past_its_preconditions():
    """A test that only exercises the satisfied case cannot fail: assert the
    negatives exist, live."""
    verdict_changed_on_root_break = False
    changed_on_side_break = False
    for world in lineage.exhaustive_worlds(4):
        if not lineage.is_side_consistent(world):
            continue
        v = lineage.verdict(world)
        for rewired in lineage.root_set_breaking_rewirings(world):
            if lineage.verdict(rewired) != v:
                verdict_changed_on_root_break = True
                break
        s = lineage.s_sets(world)
        for rewired in lineage.side_breaking_rewirings(world):
            if lineage.s_sets(rewired) != s or lineage.verdict(rewired) != v:
                changed_on_side_break = True
                break
        if verdict_changed_on_root_break and changed_on_side_break:
            break
    assert verdict_changed_on_root_break and changed_on_side_break


def test_l1_holds_live_and_fails_where_it_must():
    for world in lineage.exhaustive_worlds(3):
        s0, s1 = lineage.s_sets(world)
        expected = (lineage.asserting_roots(world, 0), lineage.asserting_roots(world, 1))
        if lineage.is_side_consistent(world):
            assert (s0, s1) == expected
    # the pinned minimal witness: one root on both sides of the literal S_a
    witness = RESULT["minimalL1NegativeWitness"]["world"]
    assert not lineage.is_side_consistent(witness)
    s0, s1 = lineage.s_sets(witness)
    assert s0 & s1, "the paper's scope-note phenomenon must appear in the witness"


def test_ablations_are_caught_live():
    caught_shallow = caught_claimcount = False
    for world in lineage.exhaustive_worlds(4):
        if not lineage.is_side_consistent(world):
            continue
        base = lineage.ablation_shallow_s_sets(world)
        if any(lineage.ablation_shallow_s_sets(r) != base for r in lineage.valid_reparentings(world)):
            caught_shallow = True
        if (lineage.ablation_claimcount_s_sets(world)
                != (lineage.asserting_roots(world, 0), lineage.asserting_roots(world, 1))):
            caught_claimcount = True
        if caught_shallow and caught_claimcount:
            break
    assert caught_shallow and caught_claimcount


def test_committed_result_meets_every_registered_expectation():
    assert RESULT["result"] == "passed"
    assert RESULT["invalidationReasons"] == []
    assert RESULT["seedReproducesIdenticalStream"] is True
    for phase in RESULT["phases"].values():
        assert phase["l1PositiveViolations"] == 0
        assert phase["t1PositiveViolations"] == 0
        for must_be_positive in ("t1RootSetBreakChangesVerdictWorlds",
                                  "t1SideBreakChangesWorlds",
                                  "l1NegativeWitnessWorlds",
                                  "lbShallowCaughtWorlds",
                                  "lbClaimcountCaughtWorlds"):
            assert phase[must_be_positive] > 0, must_be_positive
    assert RESULT["phases"]["randomized"]["worlds"] == 100_000
