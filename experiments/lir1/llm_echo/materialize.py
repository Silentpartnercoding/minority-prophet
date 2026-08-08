"""Materialize model responses and deterministic descendants as LIR-1 claims."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any

from experiments.lir1.model import ClaimInstance, write_jsonl


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def _answer(response: dict[str, Any]) -> dict[str, Any]:
    if response.get("status") != "valid" or not isinstance(response.get("rawResponse"), str):
        raise ValueError(f"response is not valid: {response.get('requestId')}")
    value = json.loads(response["rawResponse"])
    if set(value) != {"answer", "confidence", "explanation"}:
        raise ValueError("response answer does not match the frozen schema")
    return value


def _surface_mutations(answer: dict[str, Any], raw: str) -> list[tuple[str, str]]:
    explanation = answer["explanation"]
    synonyms = explanation.replace("source packet", "provided record").replace("Source packet", "Provided record")
    synonyms = synonyms.replace("states", "lists").replace("States", "Lists")
    truncated = " ".join(explanation.split()[:8])
    normalized = " ".join(explanation.replace(";", ".").replace(":", ".").split())
    reordered = json.dumps({
        "explanation": explanation,
        "confidence": answer["confidence"],
        "answer": answer["answer"],
    }, separators=(",", ":"))
    synonym_json = json.dumps({**answer, "explanation": synonyms}, sort_keys=True, separators=(",", ":"))
    truncated_json = json.dumps({**answer, "explanation": truncated}, sort_keys=True, separators=(",", ":"))
    normalized_json = json.dumps({**answer, "explanation": normalized}, sort_keys=True, separators=(",", ":"))
    return [
        ("clause-reorder", reordered),
        ("synonym-map", synonym_json),
        ("wrapper-addition", f"ANSWER RECORD START\n{raw}\nANSWER RECORD END"),
        ("explanation-truncation", truncated_json),
        ("punctuation-normalization", normalized_json),
        ("synonym-and-wrapper", f"REPHRASED RECORD\n{synonym_json}"),
    ]


def materialize(
    requests_path: Path,
    responses_path: Path,
    labels_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    requests = read_jsonl(requests_path)
    labels = read_jsonl(labels_path)
    all_responses = read_jsonl(responses_path)
    valid_responses = [row for row in all_responses if row.get("status") == "valid"]
    by_response = {row["requestId"]: row for row in valid_responses}
    if len(by_response) != len(valid_responses) or set(by_response) != {row["requestId"] for row in requests}:
        raise ValueError("responses must contain exactly one valid row per request")
    by_label = {row["recordId"]: row for row in labels}
    if len(by_label) != len(labels):
        raise ValueError("construction label IDs are not unique")

    claims: list[ClaimInstance] = []
    transformation_log: list[dict[str, Any]] = []
    request_map = {row["requestId"]: row for row in requests}
    for request in requests:
        response = by_response[request["requestId"]]
        answer = _answer(response)
        label = by_label[request["requestId"]]
        claims.append(ClaimInstance(
            dataset="lir1e_controlled_echo",
            case_id=request["caseId"],
            claim_id=request["requestId"],
            proposition_id=f"{request['caseId']}-proposition",
            text=response["rawResponse"],
            timestamp=response["completedAt"],
            author_id=response["model"],
            observed_parents=(),
            content_truth="true",
            independence_label="unknown",
            true_root_id=label["trueRootId"],
            label_basis="constructed_exact",
            label_scope="record_root",
            split=request["split"],
            channel_metadata={
                "asserted_value": answer["answer"] == label["constructedTruth"],
                "model": response["model"],
            },
        ))

    cases = sorted({row["caseId"] for row in requests})
    for case_id in cases:
        case_requests = [row for row in requests if row["caseId"] == case_id]
        origin_request = next(row for row in case_requests if row["roleId"] == "role-3")
        origin_response = by_response[origin_request["requestId"]]
        origin_answer = _answer(origin_response)
        origin_raw = origin_response["rawResponse"]
        case_times = [
            dt.datetime.fromisoformat(by_response[row["requestId"]]["completedAt"].replace("Z", "+00:00"))
            for row in case_requests
        ]
        base_time = max(case_times)
        copy_id = f"{case_id}-exact-copy"
        copy_label = by_label[copy_id]
        asserted_value = origin_answer["answer"] == copy_label["constructedTruth"]
        claims.append(ClaimInstance(
            dataset="lir1e_controlled_echo", case_id=case_id, claim_id=copy_id,
            proposition_id=f"{case_id}-proposition", text=origin_raw,
            timestamp=(base_time + dt.timedelta(seconds=1)).isoformat(),
            author_id="programmatic-copy", observed_parents=(origin_request["requestId"],),
            content_truth="true", independence_label="copy",
            true_root_id=copy_label["trueRootId"], label_basis="constructed_exact",
            label_scope="record_root", split=origin_request["split"],
            channel_metadata={"asserted_value": asserted_value, "transformation": "exact-copy"},
        ))
        transformation_log.append({
            "recordId": copy_id, "directParent": origin_request["requestId"],
            "transformationId": "exact-copy",
            "inputSha256": hashlib.sha256(origin_raw.encode()).hexdigest(),
            "outputSha256": hashlib.sha256(origin_raw.encode()).hexdigest(),
        })
        for index, (transformation, text) in enumerate(_surface_mutations(origin_answer, origin_raw)):
            record_id = f"{case_id}-mutation-{index}"
            label = by_label[record_id]
            if label["transformationId"] != transformation or label["directParent"] != copy_id:
                raise ValueError("mutation plan does not match frozen construction label")
            claims.append(ClaimInstance(
                dataset="lir1e_controlled_echo", case_id=case_id, claim_id=record_id,
                proposition_id=f"{case_id}-proposition", text=text,
                timestamp=(base_time + dt.timedelta(seconds=2 + index)).isoformat(),
                author_id="programmatic-mutation", observed_parents=(copy_id,),
                content_truth="true", independence_label="mutated_copy",
                true_root_id=label["trueRootId"], label_basis="constructed_exact",
                label_scope="record_root", split=origin_request["split"],
                channel_metadata={"asserted_value": asserted_value, "transformation": transformation},
            ))
            transformation_log.append({
                "recordId": record_id, "directParent": copy_id,
                "transformationId": transformation,
                "inputSha256": hashlib.sha256(origin_raw.encode()).hexdigest(),
                "outputSha256": hashlib.sha256(text.encode()).hexdigest(),
            })

    claims.sort(key=lambda row: (row.case_id, row.timestamp or "", row.claim_id))
    output_dir.mkdir(parents=True, exist_ok=True)
    claims_path = output_dir / "claims.jsonl"
    write_jsonl(claims_path, claims)
    log_path = output_dir / "transformation-log.jsonl"
    with log_path.open("wb") as handle:
        for row in sorted(transformation_log, key=lambda item: item["recordId"]):
            handle.write((json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n").encode())
    return {
        "caseCount": len(cases),
        "claimCount": len(claims),
        "modelResponseCount": len(requests),
        "derivedRecordCount": len(transformation_log),
        "claimsSha256": hashlib.sha256(claims_path.read_bytes()).hexdigest(),
        "transformationLogSha256": hashlib.sha256(log_path.read_bytes()).hexdigest(),
    }

