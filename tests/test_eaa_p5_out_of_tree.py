import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_DIR = ROOT / "results" / "eaa-p5-out-of-tree-v1"


def test_eaa_p5_manifest_binds_public_packet():
    manifest = json.loads((RESULT_DIR / "manifest.json").read_text())
    for relative_path, expected in manifest["files"].items():
        actual = hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()
        assert actual == expected, relative_path


def test_eaa_p5_rejected_gate_is_preserved():
    result = json.loads((RESULT_DIR / "result.json").read_text())
    assert result["verdict"] == "rejected"
    assert result["transition"] == "RESOLVE_SKIP_P6"
    assert result["syntheticConfirmation"]["candidateCollapsePoint"] == 1
    assert result["syntheticConfirmation"]["auditorV0CollapsePoint"] == 13
    assert result["softwareConfirmation"]["bestComparator"] == "hard_collapse"
    candidate_risk = result["softwareConfirmation"]["candidate"]["selectiveRisk"]
    hard_collapse_risk = result["softwareConfirmation"]["hardCollapse"]["selectiveRisk"]
    assert candidate_risk > hard_collapse_risk
    assert result["syntheticConfirmation"]["falseIndependentRate"] == 0.0
    assert not all(result["gate"]["conditions"].values())
