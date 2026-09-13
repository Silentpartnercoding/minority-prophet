"""The benchmark's headline comparison, as assertions."""

from benchmark.dependence import dependence_aware_vote, resolve_root
from benchmark.evaluate import evaluate
from benchmark.world import generate_worlds


def _reports(n=60, seed=7):
    return {r["method"]: r for r in evaluate(generate_worlds(count=n, seed=seed))}


def test_default_suite_includes_the_dependence_aware_comparator():
    assert "dependence_aware" in _reports()


def test_baselines_score_zero_and_that_is_the_point():
    r = _reports()
    assert r["majority"]["truth_accuracy"] == 0.0
    assert r["weighted"]["truth_accuracy"] == 0.0


def test_dependence_aware_beats_the_baselines_decisively():
    r = _reports()
    assert r["dependence_aware"]["truth_accuracy"] > 0.8


def test_every_copy_resolves_to_one_shared_root():
    world = next(iter(generate_worlds(count=1, seed=7)))
    by_id = {c.claim_id: c for c in world.claims}
    copied = [c for c in world.claims if not c.independent]
    roots = {resolve_root(c, by_id) for c in copied}
    assert len(roots) == 1


def test_independent_observers_keep_distinct_roots():
    world = next(iter(generate_worlds(count=1, seed=7)))
    by_id = {c.claim_id: c for c in world.claims}
    ind = [c for c in world.claims if c.independent]
    assert len({resolve_root(c, by_id) for c in ind}) == len(ind)


def test_it_abstains_rather_than_guessing_on_a_tie():
    world = next(iter(generate_worlds(count=1, seed=7)))
    ind = [c for c in world.claims if c.independent]
    copies = [c for c in world.claims if not c.independent]
    tied = dependence_aware_vote([ind[0], copies[0]])
    assert tied.belief is None
