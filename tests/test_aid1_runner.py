"""The AID-1 runner's pins, which are what make the record mean anything.

Separate from `tests/test_aid1_protocol.py`, which belongs to the world's
author. This file tests the runner, which is the operator's part.

**The pins are verified against the freeze commit, not the working tree.** They
were written to refuse a changed input, and the policy has since been repaired,
so on the working tree they now correctly refuse. That is the machinery doing
its job, not a broken test: a closed canonical record names the exact bytes it
measured, and those bytes live in git at the commit the record binds. Asserting
the pins still match HEAD would quietly re-bind the record to whatever the policy
became, which is the one thing the pins exist to prevent.
"""

import hashlib
import pathlib
import re
import subprocess

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

#: The commit that froze the AID-1 protocol, bound by `research/records/AID-1-V1.json`.
FREEZE_COMMIT = "ee88928e4ae70f1aea5969a910336795fb960da5"


def _blob(path: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(ROOT), "show", f"{FREEZE_COMMIT}:{path}"],
        capture_output=True,
    )
    assert result.returncode == 0, f"{path} absent at {FREEZE_COMMIT[:7]}"
    return result.stdout


@pytest.fixture
def freeze_tree(tmp_path):
    """The pinned inputs exactly as they stood when the protocol was frozen."""
    for name in PINNED:
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(_blob(name))
    return tmp_path


def test_pins_hold_against_the_commit_the_record_binds(freeze_tree):
    verify_pins(freeze_tree)


def test_pins_no_longer_hold_on_a_repaired_working_tree():
    """The repair changed the artifact under test, so the runner must refuse.

    Recorded as an assertion rather than left implicit: this is how the record
    stays honest about what it measured after the policy moves on.
    """
    with pytest.raises(ValueError, match="attested_independence.py"):
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
        for line in _blob(relative).decode().splitlines():
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


def test_config_loads_only_in_its_preregistered_state(freeze_tree):
    config = load_config(freeze_tree)
    assert config["status"] == "preregistered-unexecuted"
    assert config["success_criterion"]["policy_arm"] == "attested"
    assert config["success_criterion"]["baseline_arm"] == "ladder"
    assert config["confirmatory_salt"] != config["development_salt"]


def test_a_changed_input_refuses_to_run(freeze_tree):
    """The pin is only worth what its refusal is worth."""
    target = freeze_tree / "experiments/aid1run/world.py"
    target.write_bytes(target.read_bytes() + b"\n# changed\n")
    with pytest.raises(ValueError, match="aid1run/world.py"):
        verify_pins(freeze_tree)


def test_a_changed_policy_also_refuses_to_run(freeze_tree):
    """The case that matters most: editing the artifact under test."""
    target = freeze_tree / ARTIFACT_UNDER_TEST
    target.write_bytes(target.read_bytes() + b"\n# changed\n")
    with pytest.raises(ValueError, match="attested_independence.py"):
        verify_pins(freeze_tree)


def test_pinned_digests_are_real_sha256_of_the_bytes_that_were_measured():
    for name, digest in PINNED.items():
        assert re.fullmatch(r"[0-9a-f]{64}", digest), name
        assert hashlib.sha256(_blob(name)).hexdigest() == digest, name


def test_config_at_the_freeze_commit_names_every_required_family():
    import json

    config = json.loads(_blob("experiments/aid1run/EXECUTION-CONFIG.json"))
    for family in ("nobody_can_attest", "adversary_attests_freely",
                   "hidden_shared_source", "baseline_already_right",
                   "minority_suppression", "mixed_attestation"):
        assert family in config["families"], family
