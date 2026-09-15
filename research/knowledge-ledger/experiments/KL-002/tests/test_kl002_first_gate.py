"""KL-002 first gate tests.

These assert the gate's ACTUAL outcome, including that it fails under byte
identity. A test asserting only that the code runs would be single-valued and
would tell us nothing (see the repository's recurring single-valued-check
finding), so each test below names an input that would flip it.
"""

import importlib.util
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parents[1]


def _load(name, relpath):
    """Load by path under a unique name.

    Every KL experiment keeps its code in `src/`, so importing by package name
    makes whichever experiment pytest collects first shadow the others. That is
    an import collision, not a test failure, and it silently hid this suite.
    """
    spec = importlib.util.spec_from_file_location(name, HERE / relpath)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


_agg = _load("kl002_aggregate", "src/aggregate.py")
_roots = _load("kl002_roots", "src/roots.py")
confidence = _agg.confidence
distinct_roots, normalize = _roots.distinct_roots, _roots.normalize

FIXTURE = json.loads((HERE / "fixtures/laundered-source.json").read_text())


def test_byte_identity_splits_one_source_into_twenty_roots():
    """Flips if any two paraphrases normalize identically."""
    docs = FIXTURE["laundered"]["documents"]
    assert len(distinct_roots(docs, "byte_identity")) == 20
    assert FIXTURE["laundered"]["trueOriginCount"] == 1


def test_declared_origin_keeps_them_as_one_root():
    """Flips if any paraphrase declares an origin other than SRC-0."""
    docs = FIXTURE["laundered"]["documents"]
    assert len(distinct_roots(docs, "declared_origin")) == 1


def test_the_two_rules_disagree_and_that_is_the_point():
    """A single-valued check would pass both rules. This one must not."""
    docs = FIXTURE["laundered"]["documents"]
    assert distinct_roots(docs, "byte_identity") != distinct_roots(docs, "declared_origin")


def test_rules_agree_on_genuinely_independent_documents():
    """The control. Flips if declared_origin collapsed real independence too --
    which would make the rule useless in the opposite direction."""
    docs = FIXTURE["independent"]["documents"]
    assert len(distinct_roots(docs, "byte_identity")) == 3
    assert len(distinct_roots(docs, "declared_origin")) == 3


def test_laundered_false_claim_outscores_multi_sourced_true_claim():
    """The harm, stated as an inequality rather than a rate."""
    false_conf = confidence(len(distinct_roots(FIXTURE["laundered"]["documents"], "byte_identity")))
    true_conf = confidence(len(distinct_roots(FIXTURE["independent"]["documents"], "byte_identity")))
    assert FIXTURE["laundered"]["groundTruth"] is False
    assert FIXTURE["independent"]["groundTruth"] is True
    assert false_conf > true_conf


def test_normalizer_is_generous_not_a_straw_man():
    """A stricter normalizer can only increase the root count, never reduce it."""
    assert normalize("The  CITY engineer's order.") == "the city engineers order"


def test_confidence_is_monotone_and_declared():
    """Guards against a later tuned p silently changing the gate's meaning."""
    assert confidence(1, 0.7) == 0.7
    assert confidence(2, 0.7) > confidence(1, 0.7)
    assert confidence(0, 0.7) == 0.0


def test_result_file_matches_a_fresh_run():
    """The committed result must be reproducible, not a stale artifact."""
    import subprocess
    recorded = json.loads((HERE / "probe/first-gate.json").read_text())
    subprocess.run([sys.executable, str(HERE / "run_first_gate.py")],
                   capture_output=True, cwd=HERE)
    assert json.loads((HERE / "probe/first-gate.json").read_text()) == recorded
    assert recorded["gateHolds"] is False
