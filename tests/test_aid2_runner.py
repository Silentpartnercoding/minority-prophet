"""The AID-2 runner's pins, which are what make the record mean anything.

Separate from `tests/test_aid2_protocol.py`, which belongs to the world's
author. This file tests the runner, which is the operator's part.

**Nothing here reads git history.** An earlier version of the AID-1 equivalent
did, and it passed locally and failed in CI, where the Python job checks out at
the default depth and has no tree for the commit being read. Every check below
works from the working tree alone, and the one that needs a mismatch builds its
own fixture rather than reaching for bytes that might have moved.
"""

import hashlib
import json
import pathlib
import re

import pytest

from experiments.aid2run import run_confirmatory
from experiments.aid2run.run_confirmatory import (
    ARTIFACT_UNDER_TEST,
    PINNED,
    load_config,
    verify_pins,
)

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO_PACKAGES = ("experiments.", "aggregation.", "canon.", "provenance.")
WORLD_MODULES = (
    "experiments/aid2run/world.py",
    "experiments/aid2run/arms.py",
    "experiments/aid2run/scoring.py",
)


def test_pins_hold_at_freeze_time():
    verify_pins()


def test_the_policy_itself_is_pinned():
    """A runner that pins the world but not the policy can measure a policy
    that is not the one the record names."""
    assert ARTIFACT_UNDER_TEST == "aggregation/attested_independence.py"
    assert ARTIFACT_UNDER_TEST in PINNED


def test_the_pinned_policy_is_the_repaired_one():
    """AID-2 measures the policy as merged, not the one AID-1 rejected."""
    source = (ROOT / ARTIFACT_UNDER_TEST).read_text(encoding="utf-8")
    assert "def witness_bounds" in source
    assert "a.ancestry_complete and b.ancestry_complete" not in source


def test_protocol_and_config_are_pinned():
    assert "experiments/aid2run/PREREGISTRATION.md" in PINNED
    assert "experiments/aid2run/EXECUTION-CONFIG.json" in PINNED


def test_every_repository_module_the_world_imports_is_pinned():
    """Derived from the imports, not from memory: an unpinned dependency can
    change under a frozen protocol without anything noticing."""
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
    assert config["success_criterion"]["primary_arm"] == "attested_bounds"
    assert config["success_criterion"]["baseline_arm"] == "ladder"
    assert config["confirmatory_salt"] != config["development_salt"]


def test_the_refusal_mechanism_bites(tmp_path, monkeypatch):
    """A pin is worth exactly what its refusal is worth.

    Exercised against a synthetic pin map so the test needs neither git history
    nor bytes that may later be repaired.
    """
    target = tmp_path / "experiments" / "aid2run" / "world.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"original\n")
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    monkeypatch.setattr(run_confirmatory, "PINNED",
                        {"experiments/aid2run/world.py": digest})

    verify_pins(tmp_path)

    target.write_bytes(b"changed\n")
    with pytest.raises(ValueError, match="aid2run/world.py"):
        verify_pins(tmp_path)


def test_a_changed_policy_would_refuse_too(tmp_path, monkeypatch):
    """The case that matters most: editing the artifact under test."""
    target = tmp_path / ARTIFACT_UNDER_TEST
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"policy\n")
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    monkeypatch.setattr(run_confirmatory, "PINNED", {ARTIFACT_UNDER_TEST: digest})

    verify_pins(tmp_path)

    target.write_bytes(b"policy repaired again\n")
    with pytest.raises(ValueError, match="attested_independence.py"):
        verify_pins(tmp_path)


def test_the_config_names_every_required_family():
    config = json.loads(
        (ROOT / "experiments/aid2run/EXECUTION-CONFIG.json").read_text())
    for family in ("nobody_can_attest", "adversary_attests_freely",
                   "hidden_shared_source", "baseline_already_right",
                   "minority_suppression", "mixed_attestation"):
        assert family in config["families"], family


def test_the_confirmatory_salt_is_not_the_development_salt():
    config = json.loads(
        (ROOT / "experiments/aid2run/EXECUTION-CONFIG.json").read_text())
    assert config["confirmatory_salt"] != config["development_salt"]
    assert "confirmatory" in config["confirmatory_salt"]
