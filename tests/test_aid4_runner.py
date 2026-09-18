"""The AID-4 runner's pins, and the gate the world's author built.

Separate from `tests/test_aid4_protocol.py`, which belongs to the world's
author. This file tests the runner, which is the operator's part.

**Nothing here reads git history.** An earlier runner in this series verified
pins against blobs at a freeze commit; it passed locally and failed CI, where
the Python job checks out at the default depth and has no tree for that commit.
Every check below works from the working tree alone, and the one that needs a
mismatch builds its own fixture.
"""

import hashlib
import json
import pathlib
import re

import pytest

from experiments.aid4run import run_confirmatory
from experiments.aid4run.run_confirmatory import (
    ARTIFACT_UNDER_TEST,
    PINNED,
    load_config,
    verify_pins,
)
from experiments.aid4run.scoring import ConfirmatorySaltRefused, evaluate

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO_PACKAGES = ("experiments.", "aggregation.", "canon.", "provenance.")
WORLD_MODULES = (
    "experiments/aid4run/world.py",
    "experiments/aid4run/arms.py",
    "experiments/aid4run/scoring.py",
)


def test_pins_hold_at_freeze_time():
    verify_pins()


def test_the_policy_itself_is_pinned():
    """A runner that pins the world but not the policy can measure a policy
    that is not the one the record names."""
    assert ARTIFACT_UNDER_TEST == "aggregation/attested_independence.py"
    assert ARTIFACT_UNDER_TEST in PINNED


def test_every_input_named_by_the_protocol_is_pinned():
    """Section 9 names ten. Derived from the imports as a cross-check, so an
    unpinned dependency cannot change under a frozen protocol unnoticed."""
    assert len(PINNED) == 10
    imported = set()
    for relative in WORLD_MODULES:
        for line in (ROOT / relative).read_text(encoding="utf-8").splitlines():
            match = (re.match(r"\s*from ([\w.]+) import", line)
                     or re.match(r"\s*import ([\w.]+)", line))
            if match and match.group(1).startswith(REPO_PACKAGES):
                candidate = match.group(1).replace(".", "/") + ".py"
                if (ROOT / candidate).is_file():
                    imported.add(candidate)
    assert imported, "no repository imports found; the derivation is broken"
    assert imported <= set(PINNED), sorted(imported - set(PINNED))


def test_pinned_digests_are_well_formed_and_match_their_files():
    for name, digest in PINNED.items():
        assert re.fullmatch(r"[0-9a-f]{64}", digest), name
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name


def test_config_loads_only_in_its_preregistered_state():
    config = load_config()
    assert config["status"] == "preregistered-unexecuted"
    rule = config["success_criterion"]
    assert rule["primary_b"] == "margin"
    assert rule["primary_c"] == "priced"
    assert rule["baseline"] == "ladder"
    assert config["confirmatory_salt"] != config["development_salt"]


def test_the_confirmatory_salt_is_refused_without_the_explicit_flag():
    """The world author's gate: evaluating the confirmatory salt is a deliberate
    act, not something a default can trip over. The runner is the only caller
    that sets it, and the record shows who turned the key."""
    config = load_config()
    with pytest.raises(ConfirmatorySaltRefused):
        evaluate(config, config["confirmatory_salt"], 1)


def _sets_confirmatory_flag(path: pathlib.Path) -> bool:
    """True when the file actually *calls* something with `confirmatory=True`.

    Checked through the AST rather than by substring: `scoring.py` documents the
    gate in its docstring and names it in an error message, and prose about a
    flag is not the same as setting one. An earlier version of this test failed
    on exactly that confusion.
    """
    import ast

    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        for keyword in node.keywords:
            if (keyword.arg == "confirmatory"
                    and isinstance(keyword.value, ast.Constant)
                    and keyword.value.value is True):
                return True
    return False


def test_the_runner_is_the_only_place_that_sets_the_flag():
    assert _sets_confirmatory_flag(ROOT / "experiments/aid4run/run_confirmatory.py")
    for module in WORLD_MODULES:
        assert not _sets_confirmatory_flag(ROOT / module), module


def test_the_refusal_mechanism_bites(tmp_path, monkeypatch):
    """A pin is worth exactly what its refusal is worth.

    Exercised against a synthetic pin map, so the test needs neither git history
    nor bytes that may later be repaired.
    """
    target = tmp_path / "experiments" / "aid4run" / "world.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"original\n")
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    monkeypatch.setattr(run_confirmatory, "PINNED",
                        {"experiments/aid4run/world.py": digest})

    verify_pins(tmp_path)

    target.write_bytes(b"changed\n")
    with pytest.raises(ValueError, match="aid4run/world.py"):
        verify_pins(tmp_path)


def test_a_changed_policy_would_refuse_too(tmp_path, monkeypatch):
    """The case that matters most: editing the artifact under test."""
    target = tmp_path / ARTIFACT_UNDER_TEST
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"policy\n")
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    monkeypatch.setattr(run_confirmatory, "PINNED", {ARTIFACT_UNDER_TEST: digest})

    verify_pins(tmp_path)

    target.write_bytes(b"policy changed again\n")
    with pytest.raises(ValueError, match="attested_independence.py"):
        verify_pins(tmp_path)


def test_the_config_names_every_family_the_protocol_describes():
    config = json.loads(
        (ROOT / "experiments/aid4run/EXECUTION-CONFIG.json").read_text())
    for family in ("hidden_source", "backed_hidden_source", "honest_unattestable",
                   "wide_margin_unattested", "silent_but_correct",
                   "minority_suppression", "minority_wins", "mixed_populations"):
        assert family in config["families"], family
    assert len(config["families"]) == 8
