"""The AID-1 runner's pins, which are what make the record mean anything.

Separate from `tests/test_aid1_protocol.py`, which belongs to the world's
author. This file tests the runner, which is the operator's part.
"""

import hashlib
import json
import pathlib
import re
import shutil

import pytest

from experiments.aid1run.run_confirmatory import (
    ARTIFACT_UNDER_TEST,
    PINNED,
    load_config,
    verify_pins,
)

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO_PACKAGES = ("experiments.", "aggregation.", "canon.", "provenance.")
WORLD_MODULES = (
    "experiments/aid1run/world.py",
    "experiments/aid1run/arms.py",
    "experiments/aid1run/scoring.py",
)


def test_pins_hold_on_this_tree():
    verify_pins()


def test_the_policy_itself_is_pinned():
    """A runner that pins the world but not the policy can measure a policy
    that is not the one the record names."""
    assert ARTIFACT_UNDER_TEST in PINNED
    assert ARTIFACT_UNDER_TEST == "aggregation/attested_independence.py"


def test_every_repository_module_the_world_imports_is_pinned():
    """Derived from the imports, not from memory: an unpinned dependency can
    change under a frozen protocol without anything noticing."""
    imported = set()
    for relative in WORLD_MODULES:
        for line in (ROOT / relative).read_text().splitlines():
            match = (re.match(r"\s*from ([\w.]+) import", line)
                     or re.match(r"\s*import ([\w.]+)", line))
            if match and match.group(1).startswith(REPO_PACKAGES):
                candidate = match.group(1).replace(".", "/") + ".py"
                if (ROOT / candidate).is_file():
                    imported.add(candidate)
    assert imported <= set(PINNED), sorted(imported - set(PINNED))


def test_protocol_and_config_are_pinned():
    assert "experiments/aid1run/PREREGISTRATION.md" in PINNED
    assert "experiments/aid1run/EXECUTION-CONFIG.json" in PINNED


def test_config_loads_only_in_its_preregistered_state():
    config = load_config()
    assert config["status"] == "preregistered-unexecuted"
    assert config["success_criterion"]["policy_arm"] == "attested"
    assert config["success_criterion"]["baseline_arm"] == "ladder"
    assert config["confirmatory_salt"] != config["development_salt"]


def test_a_changed_input_refuses_to_run(tmp_path):
    """The pin is only worth what its refusal is worth."""
    for name in PINNED:
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / name, tmp_path / name)
    target = tmp_path / "experiments/aid1run/world.py"
    target.write_text(target.read_text() + "\n# changed\n")
    with pytest.raises(ValueError, match="aid1run/world.py"):
        verify_pins(tmp_path)


def test_a_changed_policy_also_refuses_to_run(tmp_path):
    """The case that matters most: editing the artifact under test."""
    for name in PINNED:
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / name, tmp_path / name)
    target = tmp_path / ARTIFACT_UNDER_TEST
    target.write_text(target.read_text() + "\n# changed\n")
    with pytest.raises(ValueError, match="attested_independence.py"):
        verify_pins(tmp_path)


def test_pinned_digests_are_real_sha256_of_the_named_files():
    for name, digest in PINNED.items():
        assert re.fullmatch(r"[0-9a-f]{64}", digest), name
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name


def test_config_is_valid_json_and_names_every_required_family():
    config = json.loads(
        (ROOT / "experiments/aid1run/EXECUTION-CONFIG.json").read_text())
    for family in ("nobody_can_attest", "adversary_attests_freely",
                   "hidden_shared_source", "baseline_already_right",
                   "minority_suppression", "mixed_attestation"):
        assert family in config["families"], family
