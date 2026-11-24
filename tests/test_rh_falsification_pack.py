"""Runs the RH falsification pack's own unittest suite inside the repository suite."""

from __future__ import annotations

import pathlib
import unittest

PACK = pathlib.Path(__file__).resolve().parents[1] / "experiments" / "rh_falsification"


def test_rh_falsification_pack_suite_passes():
    suite = unittest.defaultTestLoader.discover(
        start_dir=str(PACK / "tests"), pattern="test_*.py", top_level_dir=str(PACK / "tests")
    )
    result = unittest.TextTestRunner(verbosity=0).run(suite)
    assert result.testsRun > 0
    assert result.wasSuccessful(), [str(f[0]) for f in result.failures + result.errors]


def test_scorer_is_gone():
    assert not (PACK / "src" / "scorer_stub.py").exists()
