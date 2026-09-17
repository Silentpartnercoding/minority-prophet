"""KL-005 first gate tests.

Each test names the input that would flip it, so none is single-valued.
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


_m = _load("kl005_metric", "src/metric.py")
_s = _load("kl005_syndication", "src/syndication.py")
Event, Judgement = _m.Event, _m.Judgement
delay_cost, one_sided_score, two_sided_score = _m.delay_cost, _m.one_sided_score, _m.two_sided_score
independent_origins, resolve_root = _s.independent_origins, _s.resolve_root

FX = json.loads((HERE / "fixtures/syndication.json").read_text())
REPORTS = FX["reports"]
EVENTS = [Event(e["eventId"], e["isTrue"], e["independentlyReportableAt"]) for e in FX["events"]]


def _js(name):
    return [Judgement(e, d) for e, d in FX["systems"][name]["judgements"].items()]


def test_five_wire_reports_collapse_to_one_origin():
    """Flips if any wire copy declared derivedFrom: None."""
    rids = [r for r, v in REPORTS.items() if v["event"] == "E1-true-wire"]
    assert len(rids) == 5
    assert len(independent_origins(rids, REPORTS)) == 1


def test_circular_citation_yields_no_original():
    """Fail-closed. Flips if resolve_root picked an arbitrary cycle member."""
    rids = [r for r, v in REPORTS.items() if v["event"] == "E2-false-cycle"]
    assert all(resolve_root(r, REPORTS) is None for r in rids)
    assert independent_origins(rids, REPORTS) == set()


def test_genuine_independence_survives_collapse():
    """The control: the rule must not flatten real independence."""
    rids = [r for r, v in REPORTS.items() if v["event"] == "E3-true-three"]
    assert len(independent_origins(rids, REPORTS)) == 3


def test_seven_syndicated_reports_are_still_one_source():
    rids = [r for r, v in REPORTS.items() if v["event"] == "E4-false-single"]
    assert len(rids) == 7
    assert len(independent_origins(rids, REPORTS)) == 1


def test_one_sided_metric_is_won_by_saying_nothing():
    """The defect, demonstrated. This test SHOULD pass -- it records that the
    naive metric is broken. It flips only if silence stops scoring perfectly."""
    assert one_sided_score(EVENTS, _js("silent")) == 0.0
    assert one_sided_score(EVENTS, _js("silent")) <= one_sided_score(EVENTS, _js("root_aware"))


def test_two_sided_metric_makes_silence_lose():
    """The repair. Flips if delay_cost stopped charging for never-confirmed
    true events."""
    silent = two_sided_score(EVENTS, _js("silent"))
    aware = two_sided_score(EVENTS, _js("root_aware"))
    counting = two_sided_score(EVENTS, _js("count_reports"))
    assert aware < silent
    assert aware < counting
    # Was: `silent == max(...) or counting > silent`. That disjunction passed
    # whichever of its halves held, so it could not distinguish silence being
    # worst from silence merely losing -- and REPRODUCE.md asserted the former
    # while the numbers showed the latter. The full ordering is stated instead,
    # so the prose and the measurement cannot drift apart again.
    assert aware < silent < counting


def test_silence_pays_the_full_horizon():
    """Flips if a never-confirmed true event were charged less than 1.0."""
    assert delay_cost(EVENTS, _js("silent")) == 1.0


def test_counting_reports_is_fooled_by_syndication():
    """The naive baseline must actually fail, or the comparison is vacuous."""
    assert one_sided_score(EVENTS, _js("count_reports")) == 1.0


def test_result_file_reproduces():
    import subprocess
    recorded = json.loads((HERE / "probe/first-gate.json").read_text())
    subprocess.run([sys.executable, str(HERE / "run_first_gate.py")], capture_output=True, cwd=HERE)
    assert json.loads((HERE / "probe/first-gate.json").read_text()) == recorded
    assert recorded["oneSidedWinner"] == "silent"
    assert recorded["twoSidedWinner"] == "root_aware"
