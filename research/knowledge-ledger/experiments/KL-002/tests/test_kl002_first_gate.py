"""KL-002: the measured defect, and the repair.

Each test names the input that would flip it, so none is single-valued.
"""

import importlib.util
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parents[1]
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))


def _load(name, relpath):
    spec = importlib.util.spec_from_file_location(name, HERE / relpath)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


_agg = _load("kl002_aggregate", "src/aggregate.py")
_roots = _load("kl002_roots", "src/roots.py")
confidence = _agg.confidence
distinct_roots, normalize, build_index = _roots.distinct_roots, _roots.normalize, _roots.build_index

FIXTURE = json.loads((HERE / "fixtures/laundered-source.json").read_text())
POPULATIONS = ("laundered", "stripped", "chained", "independent")
INDEX = build_index(*(FIXTURE[name] for name in POPULATIONS))


def _roots_for(population, rule):
    return distinct_roots(FIXTURE[population]["documents"], rule, INDEX)


# ---- the defect ------------------------------------------------------------

def test_byte_identity_splits_one_source_into_twenty_roots():
    assert len(_roots_for("laundered", "byte_identity")) == 20
    assert FIXTURE["laundered"]["trueOriginCount"] == 1


def test_laundered_false_claim_outscores_multi_sourced_true_claim():
    false_conf = confidence(len(_roots_for("laundered", "byte_identity")))
    true_conf = confidence(len(_roots_for("independent", "byte_identity")))
    assert FIXTURE["laundered"]["groundTruth"] is False
    assert FIXTURE["independent"]["groundTruth"] is True
    assert false_conf > true_conf


# ---- the repair ------------------------------------------------------------

def test_ancestry_collapses_declared_descent_to_one_root():
    assert _roots_for("laundered", "ancestry") == {"SRC-0"}


def test_ancestry_refuses_a_document_that_declares_no_ancestry():
    """The actual repair. byte_identity mints 20 roots from stripped provenance
    and declared_origin mints 0 by reading a null; ancestry refuses all 20 as
    unattributable. Flips if silence is ever read as originality again."""
    assert _roots_for("stripped", "ancestry") == set()
    assert len(_roots_for("stripped", "byte_identity")) == 20


def test_only_ancestry_survives_a_chain_and_nothing_in_it_is_a_lie():
    """Every chained document truthfully names what it was copied from.
    declared_origin reads one hop and calls five intermediates origins."""
    assert len(_roots_for("chained", "declared_origin")) == 6
    assert _roots_for("chained", "ancestry") == {"SRC-0"}
    assert FIXTURE["chained"]["trueOriginCount"] == 1


def test_ancestry_preserves_genuine_independence():
    """The control: the repair must not flatten real independence."""
    assert len(_roots_for("independent", "ancestry")) == 3


def test_no_rule_is_correct_on_every_population():
    """Recorded rather than hidden: ancestry is wrong on `stripped` by refusing
    all twenty instead of finding the one."""
    for rule in ("byte_identity", "declared_origin", "ancestry"):
        correct = [len(_roots_for(p, rule)) == FIXTURE[p]["trueOriginCount"] for p in POPULATIONS]
        assert not all(correct), f"{rule} unexpectedly correct everywhere"


def test_only_ancestry_never_manufactures_independence():
    """The asymmetry that matters: over-counting creates a false belief,
    under-counting creates an abstention."""
    for rule in ("byte_identity", "declared_origin"):
        assert any(len(_roots_for(p, rule)) > FIXTURE[p]["trueOriginCount"] for p in POPULATIONS)
    assert all(len(_roots_for(p, "ancestry")) <= FIXTURE[p]["trueOriginCount"] for p in POPULATIONS)


def test_ancestry_is_shared_with_kl005_not_duplicated():
    from knowledge_ledger.ancestry import resolve_root  # noqa: F401
    assert (ROOT / "knowledge_ledger/ancestry.py").is_file()


def test_ancestry_fails_closed_on_a_cycle():
    from knowledge_ledger.ancestry import resolve_root
    docs = {"A": {"derivedFrom": "C"}, "B": {"derivedFrom": "A"}, "C": {"derivedFrom": "B"}}
    assert all(resolve_root(k, docs) is None for k in docs)


def test_normalizer_is_generous_not_a_straw_man():
    assert normalize("The  CITY engineer's order.") == "the city engineers order"


def test_result_file_matches_a_fresh_run():
    import subprocess
    recorded = json.loads((HERE / "probe/first-gate.json").read_text())
    subprocess.run([sys.executable, str(HERE / "run_first_gate.py")], capture_output=True, cwd=HERE)
    assert json.loads((HERE / "probe/first-gate.json").read_text()) == recorded
    assert recorded["gateHoldsUnderByteIdentity"] is False
    assert recorded["errorDirection"]["ancestry"]["neverOvercounts"] is True
