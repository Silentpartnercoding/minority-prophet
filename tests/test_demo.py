"""The public runner must fail on regressions, not merely print a receipt."""
import subprocess
import sys
from pathlib import Path

from scripts import demo


def test_demo_passes_and_identifies_its_source(capsys):
    assert demo.main() == 0
    output = capsys.readouterr().out
    assert "commit=" in output and "UTC=" in output
    assert "PASS: 3 citations resolve to 1 declared root" in output
    assert "PASS: bounded immunity checks and negative controls (6 checks)" in output


def test_citation_root_regression_fails(monkeypatch, capsys):
    citations = list(demo.CITATION["CITATIONS"])
    label, _, basis = citations[-1]
    citations[-1] = (label, "different-root", basis)
    monkeypatch.setitem(demo.CITATION, "CITATIONS", citations)
    assert demo.main() == 1
    assert "FAIL: citation fixture" in capsys.readouterr().out


def test_empty_immunity_population_fails(monkeypatch, capsys):
    lineage = demo.CHECKS["test_t1_holds_live_on_the_exhaustive_prefix"].__globals__["lineage"]
    monkeypatch.setattr(lineage, "valid_reparentings", lambda world: iter(()))
    assert demo.main() == 1
    assert "FAIL: test_t1_holds_live_on_the_exhaustive_prefix" in capsys.readouterr().out


def test_lost_negative_control_fails(monkeypatch, capsys):
    lineage = demo.CHECKS["test_t1_protection_does_not_extend_past_its_preconditions"].__globals__["lineage"]
    monkeypatch.setattr(lineage, "root_set_breaking_rewirings", lambda world: iter(()))
    assert demo.main() == 1
    assert "FAIL: test_t1_protection_does_not_extend_past_its_preconditions" in capsys.readouterr().out


def test_optimized_python_cannot_silently_disable_checks():
    result = subprocess.run(
        [sys.executable, "-O", str(Path(demo.__file__))],
        capture_output=True, text=True,
    )
    assert result.returncode == 1
    assert "FAIL: Python optimization disables assertions" in result.stdout
