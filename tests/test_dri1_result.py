import hashlib
import json
from pathlib import Path

RESULT = Path(__file__).parents[1] / "results" / "dri1a-v1" / "result.json"


def test_dri1a_adverse_result_is_content_bound_and_not_relabelled_success():
    assert hashlib.sha256(RESULT.read_bytes()).hexdigest() == (
        "ec8b2428f459af9f80b8372935d5d0eb1ed1d22aefc30aa0864ec00b55da4c6c"
    )
    result = json.loads(RESULT.read_text())
    assert result["criterion"]["supported"] is False
    assert result["semanticResultSha256Runs"] == [
        "c63097e8ada155aba93e2ceb310dca771285114a2581998515a8fbdfa85487a2",
        "c63097e8ada155aba93e2ceb310dca771285114a2581998515a8fbdfa85487a2",
    ]
    assert result["semanticResult"]["worlds"] == 8192
    assert result["semanticResult"]["rulesOracleDispositionMismatches"] == 0


def test_dri1a_preserves_the_narrow_diagnostic_without_rescuing_the_criterion():
    result = json.loads(RESULT.read_text())["semanticResult"]
    overall = result["methodsByStratum"]["overall"]
    assert overall["oracle_policy"]["correctSettlementRate"] == 0.909912109
    assert overall["agent_headcount"]["correctSettlementRate"] == 0.607788086
    assert overall["oracle_policy"]["minorityReversalRecoveryRate"] == 1.0
    assert overall["agent_headcount"]["minorityReversalRecoveryRate"] == 0.0
    assert overall["fixed_upstream_component"]["abstentionRate"] == 0.40234375

