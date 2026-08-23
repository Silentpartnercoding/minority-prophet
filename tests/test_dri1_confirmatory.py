from pathlib import Path

from experiments.dri1.run_confirmatory import (
    CONFIG_SHA256,
    PREREGISTRATION_SHA256,
    _outcomes,
    generate_world,
    iter_worlds,
    load_frozen_config,
)


ROOT = Path(__file__).parents[1]
CONFIG = ROOT / "experiments" / "dri1" / "EXECUTION-CONFIG.json"
PREREGISTRATION = ROOT / "experiments" / "dri1" / "PREREGISTRATION.md"


def _config():
    return load_frozen_config(CONFIG, PREREGISTRATION)


def test_preregistered_inputs_are_content_bound():
    config = _config()
    assert CONFIG_SHA256 == "42078e86815cd5b806e1a44f23aaff4b002f94af7193b5c422adf0c948bb7d1b"
    assert PREREGISTRATION_SHA256 == (
        "6f47faa5aaa3d856e7d9e990b40b086288a9d05507a2b7ec053f85ef720248ce"
    )
    assert config["status"] == "preregistered-unexecuted"


def test_generator_materializes_the_frozen_factorial():
    worlds = list(iter_worlds(_config()))
    assert len(worlds) == 8192
    assert len({world.world_id for world in worlds}) == 8192
    assert {world.relevant_cut for world in worlds} == {
        "machine",
        "controller",
        "evidence_origin",
        "upstream_component",
    }


def test_repeated_observation_is_distinct_at_fine_cut_and_shared_at_relevant_cut():
    config = _config()
    for replicate in range(config["replicates_per_cell"]):
        world = generate_world(
            config,
            failure_domain="copied_source",
            accuracy=0.65,
            amplification=15,
            decision_class="high_irreversible",
            replicate=replicate,
        )
        by_origin = {}
        for item in world.evidence:
            by_origin.setdefault(item.roots["evidence_origin"], []).append(item)
        copied = next((items for items in by_origin.values() if len(items) > 1), None)
        if copied:
            assert len({item.roots["agent"] for item in copied}) == len(copied)
            assert len({item.roots["evidence_origin"] for item in copied}) == 1
            return
    raise AssertionError("frozen generator produced no copied source in searched worlds")


def test_sampled_worlds_are_deterministic_and_rules_equal_oracle():
    config = _config()
    first = list(iter_worlds(config))[:128]
    second = list(iter_worlds(config))[:128]
    assert first == second
    cuts = tuple(config["candidate_cuts"])
    for world in first:
        oracle, _ = _outcomes(world, world.relevant_cut, world.threshold, cuts)
        selected_cut = config["cut_policy"][world.failure_domain]
        rules, _ = _outcomes(world, selected_cut, world.threshold, cuts)
        assert selected_cut == world.relevant_cut
        assert rules[selected_cut].settlement == oracle[world.relevant_cut].settlement
