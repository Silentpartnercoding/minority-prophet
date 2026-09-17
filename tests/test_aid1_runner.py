"""The AID-1 runner's pins, which are what make the record mean anything.

Separate from `tests/test_aid1_protocol.py`, which belongs to the world's
author. This file tests the runner, which is the operator's part.

**Verified against the canonical manifest, not against git history.** An earlier
version of this file read blobs out of the freeze commit. That passed locally
and failed in CI, where the Python job checks out at the default depth and has
no tree for that commit. Reading a repository's own history inside a test is
fragile by construction, and the invariant did not need it: the manifest is a
committed file, present in every checkout, recording the same digests for the
same paths. What matters is that the runner and the closed record agree about
which bytes were measured, and that is checkable from the working tree alone.

The pins no longer match the working tree, because the policy was repaired after
AID-1 closed. That is the machinery working — a closed record names the bytes it
measured, and re-pinning it to whatever the policy became is the one thing pins
exist to prevent — and it is asserted below rather than left implicit.
"""

import hashlib
import json
import pathlib
import re

import pytest

from experiments.aid1run import run_confirmatory
from experiments.aid1run.run_confirmatory import (
    ARTIFACT_UNDER_TEST,
    PINNED,
    load_config,
    verify_pins,
)

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "results" / "aid1-v1" / "canonical-manifest.json"
MANIFEST = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
RECORDED = MANIFEST["files"]

REPO_PACKAGES = ("experiments.", "aggregation.", "canon.", "provenance.")
WORLD_MODULES = (
    "experiments/aid1run/world.py",
    "experiments/aid1run/arms.py",
    "experiments/aid1run/scoring.py",
)


def test_every_pinned_path_is_bound_by_the_record_at_the_same_digest():
    """The invariant: runner and record name the same bytes."""
    missing = sorted(set(PINNED) - set(RECORDED))
    assert not missing, missing
    disagreements = {
        name: (digest, RECORDED[name])
        for name, digest in PINNED.items()
        if RECORDED[name] != digest
    }
    assert not disagreements, disagreements


def test_the_policy_itself_is_pinned_and_bound():
    """A runner that pins the world but not the policy can measure a policy
    that is not the one the record names."""
    assert ARTIFACT_UNDER_TEST == "aggregation/attested_independence.py"
    assert ARTIFACT_UNDER_TEST in PINNED
    assert ARTIFACT_UNDER_TEST in RECORDED
    assert MANIFEST["artifactUnderTest"] == ARTIFACT_UNDER_TEST


def test_protocol_and_config_are_pinned():
    assert "experiments/aid1run/PREREGISTRATION.md" in PINNED
    assert "experiments/aid1run/EXECUTION-CONFIG.json" in PINNED


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


def test_pinned_digests_are_well_formed():
    for name, digest in PINNED.items():
        assert re.fullmatch(r"[0-9a-f]{64}", digest), name


def test_the_repaired_policy_makes_the_runner_refuse():
    """The record must not silently re-bind to a policy it never measured."""
    with pytest.raises(ValueError, match="attested_independence.py"):
        verify_pins()


def test_loading_the_config_refuses_while_a_pinned_input_differs():
    """`load_config` verifies pins first, so it fails closed for the same reason."""
    with pytest.raises(ValueError, match="attested_independence.py"):
        load_config()


def test_the_refusal_mechanism_bites(tmp_path, monkeypatch):
    """A pin is worth exactly what its refusal is worth.

    Exercised against a synthetic pin map so the test needs neither git history
    nor the original bytes of a file that has since been repaired.
    """
    target = tmp_path / "experiments" / "aid1run" / "world.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"original\n")
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    monkeypatch.setattr(run_confirmatory, "PINNED",
                        {"experiments/aid1run/world.py": digest})

    verify_pins(tmp_path)

    target.write_bytes(b"changed\n")
    with pytest.raises(ValueError, match="aid1run/world.py"):
        verify_pins(tmp_path)


def test_the_config_names_every_required_family():
    config = json.loads(
        (ROOT / "experiments/aid1run/EXECUTION-CONFIG.json").read_text())
    assert config["status"] == "preregistered-unexecuted"
    assert config["success_criterion"]["policy_arm"] == "attested"
    assert config["success_criterion"]["baseline_arm"] == "ladder"
    assert config["confirmatory_salt"] != config["development_salt"]
    for family in ("nobody_can_attest", "adversary_attests_freely",
                   "hidden_shared_source", "baseline_already_right",
                   "minority_suppression", "mixed_attestation"):
        assert family in config["families"], family


def test_the_record_and_the_runner_agree_on_the_verdict_they_describe():
    assert MANIFEST["verdict"] == "rejected"
    assert MANIFEST["reproducible"] is True
