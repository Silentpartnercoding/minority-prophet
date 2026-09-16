"""Integrity tests for the DRI-9 protocol.

Development salt only. Construction invariants; no arm comparisons.
"""

import json
from itertools import combinations
from pathlib import Path

from experiments.dri3.world import CUTS, IRREVERSIBLE, REVERSIBLE
from experiments.dri9.arms import ARMS, METHOD, run_campaign
from experiments.dri9.rule import (
    BELIEF_CUT,
    RULE_CUTS,
    Belief,
    believe,
    is_pivotal,
    lookup_grouping,
    outcome_if_believed,
)
from experiments.dri9.scoring import evaluate, evaluate_criterion
from experiments.dri9.world import FAMILIES, GROUP_SIZE, cell_key, cells, generate_campaign

ROOT = Path(__file__).parents[1]
CONFIG = json.loads((ROOT / "experiments" / "dri9" / "EXECUTION-CONFIG.json").read_text())
DEV = CONFIG["development_salt"]
HIDDEN_FAMILIES = ("shared_upstream_pair", "shared_upstream_trio")


def campaigns(family, count=4, pickup=0.9, jitter=0.1):
    return [generate_campaign(CONFIG, DEV, family, rep, pickup, jitter) for rep in range(count)]


def test_config_is_frozen_scoped_and_sized():
    assert CONFIG["status"] == "preregistered-unexecuted"
    assert tuple(CONFIG["families"]) == FAMILIES
    assert CONFIG["decision_scope"] == "reversible"
    assert CONFIG["success_criterion"]["scope"] == "reversible"
    assert CONFIG["campaigns_per_family"] * CONFIG["decisions_per_campaign"] == 6000
    assert CONFIG["success_criterion"]["method_under_test"] == METHOD
    assert "timing" not in CONFIG["ladder_signals"]


def test_the_hidden_component_is_recorded_nowhere_and_never_looked_up():
    for family in HIDDEN_FAMILIES:
        for campaign in campaigns(family):
            focus = set(campaign.focus_group)
            assert len(focus) == GROUP_SIZE[family]
            for decision in campaign.decisions:
                source_of = dict(decision.source_of)
                for cut in CUTS + ("content",):
                    groups = {}
                    for item in decision.evidence:
                        groups.setdefault(item.roots[cut], set()).add(source_of[item.observation_id])
                    assert not any(len(members & focus) > 1 for members in groups.values()), cut
                reported = dict(lookup_grouping(decision))
                observation = {source: obs for obs, source in decision.source_of}
                for left, right in combinations(sorted(focus), 2):
                    assert reported[observation[left]] != reported[observation[right]]


def test_believing_rewrites_every_cut_for_the_group_and_nothing_else():
    campaign = campaigns("shared_upstream_pair", 1)[0]
    decision = campaign.decisions[0]
    belief = Belief()
    belief.merge(*campaign.focus_group[:2])
    source_of = dict(decision.source_of)
    before = {i.observation_id: dict(i.roots) for i in decision.evidence}
    after = {i.observation_id: dict(i.roots) for i in believe(decision, belief)}
    believed_ids = set(campaign.focus_group[:2])
    believed_observations = [o for o, s in source_of.items() if s in believed_ids]
    for observation, roots in after.items():
        if source_of[observation] in believed_ids:
            assert all(roots[cut] != before[observation][cut] for cut in CUTS)
        else:
            assert all(roots[cut] == before[observation][cut] for cut in CUTS)
        assert BELIEF_CUT in roots
    # Identities are namespaced per cut, so the property is that the believed
    # sources agree with each other AT each cut, not that one string spans all
    # five. They must also stop agreeing with anyone they did not merge with.
    for cut in CUTS:
        shared = {after[o][cut] for o in believed_observations}
        assert len(shared) == 1, cut
        others = {after[o][cut] for o in after if source_of[o] not in believed_ids}
        assert shared.isdisjoint(others), cut
    assert len({after[o][BELIEF_CUT] for o in believed_observations}) == 1


def test_is_pivotal_checks_every_subset_not_a_sliding_window():
    """The trio's (first, third) pair was skipped by the original slice walk."""
    campaign = campaigns("shared_upstream_trio", 1)[0]
    group = campaign.focus_group
    assert len(group) == 3
    for decision in campaign.decisions:
        base = outcome_if_believed(decision, Belief())
        any_subset = any(
            outcome_if_believed(decision, Belief(), [(subset[0], other) for other in subset[1:]]) != base
            for size in (2, 3)
            for subset in combinations(group, size)
        )
        assert is_pivotal(decision, group) == any_subset


def test_the_ladder_scores_only_its_declared_signals():
    """Timing must not supply a vote to the method under test."""
    import experiments.dri9.arms as arms

    source = Path(arms.__file__).read_text()
    assert 'config["ladder_signals"]' in source
    assert "timing" in source  # still available as an arm, just not declared
    loose = dict(CONFIG, ladder_signals=["bait", "timing", "coerror"], ladder_score_to_merge=2)
    differed = False
    for campaign in campaigns("shared_upstream_pair", 8, jitter=0.1):
        _, declared = run_campaign(METHOD, campaign, CONFIG, DEV)
        _, contaminated = run_campaign(METHOD, campaign, loose, DEV)
        declared_pairs = {tuple(sorted(pair)) for pair in declared.pairs()}
        contaminated_pairs = {tuple(sorted(pair)) for pair in contaminated.pairs()}
        assert declared_pairs <= contaminated_pairs
        differed |= declared_pairs != contaminated_pairs
    assert differed, "excluding timing must change what the ladder believes"


def test_only_ablation_spends_and_never_above_budget():
    for family in FAMILIES:
        for campaign in campaigns(family, 2):
            for arm in ARMS:
                outcomes, _ = run_campaign(arm, campaign, CONFIG, DEV)
                spent = sum(o.interventions for o in outcomes)
                assert spent <= CONFIG["ablation_budget"]
                if arm != "ablation":
                    assert spent == 0


def test_everything_is_deterministic():
    for family in FAMILIES:
        for pickup, jitter in cells(CONFIG):
            campaign = generate_campaign(CONFIG, DEV, family, 1, pickup, jitter)
            assert campaign == generate_campaign(CONFIG, DEV, family, 1, pickup, jitter)
            for arm in ARMS:
                first, left = run_campaign(arm, campaign, CONFIG, DEV)
                again, right = run_campaign(arm, campaign, CONFIG, DEV)
                assert [vars(o) for o in first] == [vars(o) for o in again]
                assert sorted(map(sorted, left.groups)) == sorted(map(sorted, right.groups))


def test_decision_classes_alternate_and_both_appear():
    campaign = campaigns("shared_upstream_pair", 1)[0]
    classes = [d.decision_class for d in campaign.decisions]
    assert set(classes) == {IRREVERSIBLE, REVERSIBLE}
    assert classes[0] == IRREVERSIBLE and classes[1] == REVERSIBLE


def test_criterion_logic_on_constructed_rows():
    def row(critical, prevented, arm_only, correct=1000, method_correct=1000, spent=0, true_m=5, false_m=0):
        comparison = {
            "silent": max(critical - prevented, 0), "criticalSilent": max(critical - prevented, 0),
            "criticalPrevented": prevented, "tieredOnlySilent": prevented, "armOnlySilent": arm_only,
            "p": 2 * 0.5 ** prevented if arm_only == 0 else 1.0,
        }
        return {
            "arms": {
                "tiered_rule": {f"{REVERSIBLE}:correct_settlement": correct},
                METHOD: {f"{REVERSIBLE}:correct_settlement": method_correct,
                         f"{REVERSIBLE}:interventions": spent,
                         "trueMerges": true_m, "falseMerges": false_m},
            },
            "reversibleTieredSilent": critical,
            "criticalTieredSilent": critical,
            "comparisons": {arm: dict(comparison) for arm in
                            ("fragile_refusal", "bait", "reflection", "ablation", METHOD)},
        }

    def semantic(good):
        return {"families": {f: {cell_key(p, j): good for p, j in cells(CONFIG)} for f in CONFIG["families"]}}

    assert evaluate_criterion(semantic(row(40, 30, 0)), CONFIG, True)["supported"]
    # prevented too small a share of the critical set
    assert not evaluate_criterion(semantic(row(40, 5, 0)), CONFIG, True)["supported"]
    # loses too many correct settlements
    assert not evaluate_criterion(semantic(row(40, 30, 0, method_correct=800)), CONFIG, True)["supported"]
    # spends more than the ceiling per prevented error
    assert not evaluate_criterion(semantic(row(40, 30, 0, spent=100000)), CONFIG, True)["supported"]
    # believes more wrongly than rightly
    assert not evaluate_criterion(semantic(row(40, 30, 0, true_m=1, false_m=9)), CONFIG, True)["supported"]
    assert not evaluate_criterion(semantic(row(40, 30, 0)), CONFIG, False)["supported"]
    quiet = evaluate_criterion(semantic(row(3, 0, 0)), CONFIG, True)
    assert quiet["supported"] and quiet["underpoweredComparisons"]


def test_evaluation_runs_and_is_deterministic_on_development_campaigns():
    first = evaluate(CONFIG, DEV, 1)
    assert first == evaluate(CONFIG, DEV, 1)
    assert first["campaigns"] == len(FAMILIES) * len(cells(CONFIG))
    assert set(first["families"]) == set(FAMILIES)
    assert "reversible" in first["scope"]


def test_runner_pins_hold_and_refuse_changed_inputs(tmp_path):
    import shutil

    import pytest

    from experiments.dri9.run_confirmatory import PINNED, load_config, verify_pins

    verify_pins()
    assert load_config()["status"] == "preregistered-unexecuted"
    for name in PINNED:
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / name, tmp_path / name)
    reused = tmp_path / "experiments/dri9/rule.py"
    reused.write_text(reused.read_text() + "\n# changed\n")
    with pytest.raises(ValueError, match="dri9/rule.py"):
        verify_pins(tmp_path)
