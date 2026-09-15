"""DRI-2 v2 is the frozen v1 code with no speed criterion and fresh worlds."""

import json
from pathlib import Path

import pytest

from experiments.dri2.run_confirmatory import PINNED as V1_PINNED
from experiments.dri2v2.run_confirmatory import PINNED, ROOT, load_config, verify_pins


def test_v2_pins_hold_and_config_is_preregistered():
    verify_pins()
    config = load_config()
    assert config["success_criterion"]["faster_than"] == []
    assert config["wrong_time_escalation_cost_ms"] == 0


def test_v2_uses_the_v1_implementation_byte_for_byte():
    for name in ("world.py", "arms.py", "stats.py", "scoring.py", "PREREGISTRATION.md"):
        assert PINNED[f"experiments/dri2/{name}"] == V1_PINNED[name]


def test_v2_changes_only_the_registered_fields():
    v1 = json.loads((ROOT / "experiments/dri2/EXECUTION-CONFIG.json").read_text())
    v2 = json.loads((ROOT / "experiments/dri2v2/EXECUTION-CONFIG.json").read_text())
    changed = {k for k in v1 if v1[k] != v2[k]}
    assert changed == {"schema", "experiment", "confirmatory_salt", "development_salt",
                       "wrong_time_escalation_cost_ms", "success_criterion"}
    assert v2["confirmatory_salt"] != v1["confirmatory_salt"]
    v1_rule = dict(v1["success_criterion"]); v1_rule["faster_than"] = []
    assert v2["success_criterion"] == v1_rule


def test_v2_runner_refuses_changed_inputs(tmp_path):
    import shutil

    for name in PINNED:
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / name, tmp_path / name)
    target = tmp_path / "experiments/dri2v2/EXECUTION-CONFIG.json"
    target.write_text(target.read_text().replace('"familywise_alpha": 0.05', '"familywise_alpha": 0.1'))
    with pytest.raises(ValueError, match="EXECUTION-CONFIG"):
        verify_pins(tmp_path)
