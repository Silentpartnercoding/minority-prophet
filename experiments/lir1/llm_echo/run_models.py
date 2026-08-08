"""Isolated, resumable CLI runner for the registered LIR-1E model calls.

Dry-run is the default. Actual calls require both a registered configuration
and the explicit ``--execute`` flag. Each child process starts in an empty
temporary directory and receives no repository path.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


ALLOWED_ADAPTERS = {"claude-cli", "codex-cli"}
ANSWER_KEYS = {"answer", "confidence", "explanation"}


def _canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _timestamp() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def load_config(path: Path, request_count: int, requests_sha256: str | None = None) -> dict[str, Any]:
    config = json.loads(path.read_text(encoding="utf-8"))
    if config.get("schema") != "minority-prophet.lir1e-execution-config.v1":
        raise ValueError("unexpected execution config schema")
    if config.get("status") != "registered":
        raise ValueError("execution config must have status 'registered'")
    frozen_requests = config.get("frozenRequestsSha256")
    if not isinstance(frozen_requests, str) or len(frozen_requests) != 64:
        raise ValueError("execution config must bind frozenRequestsSha256")
    if requests_sha256 is not None and frozen_requests != requests_sha256:
        raise ValueError("request inventory does not match frozenRequestsSha256")
    assignments = config.get("assignments", {})
    if set(assignments) != {"model-a", "model-b"}:
        raise ValueError("execution config must define exactly model-a and model-b")
    for slot, assignment in assignments.items():
        if assignment.get("adapter") not in ALLOWED_ADAPTERS:
            raise ValueError(f"{slot} has unsupported adapter")
        if not assignment.get("provider") or not assignment.get("model"):
            raise ValueError(f"{slot} must freeze provider and exact model")
    limits = config.get("limits", {})
    if not isinstance(limits.get("maximumCalls"), int) or limits["maximumCalls"] < request_count:
        raise ValueError("maximumCalls is below the request count")
    maximum_usd = limits.get("maximumUsd")
    if not isinstance(maximum_usd, (int, float)) or maximum_usd < 0:
        raise ValueError("maximumUsd must be a non-negative number")
    billing_modes = {assignment.get("billingMode") for assignment in assignments.values()}
    if maximum_usd == 0 and billing_modes != {"subscription"}:
        raise ValueError("zero maximumUsd requires subscription billing for every model")
    if config.get("parameters", {}).get("temperature") != 0:
        raise ValueError("temperature must remain frozen at zero")
    return config


def render_input(request: dict[str, Any]) -> str:
    return (
        f"{request['prompt']}\n\n"
        f"QUESTION\n{request['question']}\n\n"
        f"SOURCE PACKET\n{request['sourcePacket']}\n"
    )


def command_for(adapter: str, model: str, answer_schema: Path, prompt: str) -> tuple[list[str], str | None]:
    if adapter == "claude-cli":
        schema_value = json.loads(answer_schema.read_text())
        # Claude Code accepts the validation body but rejects draft metadata
        # such as `$schema` before any provider request is made.
        schema_value.pop("$schema", None)
        schema_value.pop("$id", None)
        schema = json.dumps(schema_value, separators=(",", ":"))
        return ([
            "claude", "--print", "--safe-mode", "--tools", "",
            "--no-session-persistence", "--model", model,
            "--output-format", "json", "--json-schema", schema, prompt,
        ], None)
    if adapter == "codex-cli":
        return ([
            "codex", "exec", "--ephemeral", "--ignore-user-config", "--ignore-rules",
            "--skip-git-repo-check", "--sandbox", "read-only", "--model", model,
            "--output-schema", str(answer_schema), "--json", "-",
        ], prompt)
    raise ValueError(f"unsupported adapter: {adapter}")


def _valid_answer(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and set(value) == ANSWER_KEYS
        and isinstance(value["answer"], str)
        and bool(value["answer"])
        and isinstance(value["confidence"], (int, float))
        and not isinstance(value["confidence"], bool)
        and 0 <= value["confidence"] <= 1
        and isinstance(value["explanation"], str)
    )


def parse_cli_output(adapter: str, stdout: str) -> tuple[dict[str, Any] | None, str | None, Any]:
    if adapter == "claude-cli":
        wrapper = json.loads(stdout)
        candidate = wrapper.get("structured_output")
        if candidate is None and isinstance(wrapper.get("result"), str):
            try:
                candidate = json.loads(wrapper["result"])
            except json.JSONDecodeError:
                candidate = None
        receipt = wrapper.get("session_id")
        usage = wrapper.get("usage") or wrapper.get("modelUsage")
        return (candidate if _valid_answer(candidate) else None, receipt, usage)

    events = [json.loads(line) for line in stdout.splitlines() if line.strip()]
    receipt = next((event.get("thread_id") for event in events if event.get("type") == "thread.started"), None)
    texts = [
        event.get("item", {}).get("text")
        for event in events
        if event.get("type") == "item.completed"
        and event.get("item", {}).get("type") == "agent_message"
    ]
    candidate = None
    if texts:
        try:
            candidate = json.loads(texts[-1])
        except (json.JSONDecodeError, TypeError):
            pass
    usage = next((event.get("usage") for event in reversed(events) if event.get("usage")), None)
    return (candidate if _valid_answer(candidate) else None, receipt, usage)


def run_one(request: dict[str, Any], config: dict[str, Any], answer_schema: Path, attempt: int) -> tuple[dict, bytes]:
    assignment = config["assignments"][request["modelSlot"]]
    prompt = render_input(request)
    requested_at = _timestamp()
    with tempfile.TemporaryDirectory(prefix="lir1e-isolated-") as directory:
        local_schema = Path(directory) / "answer.schema.json"
        local_schema.write_bytes(answer_schema.read_bytes())
        command, stdin = command_for(
            assignment["adapter"], assignment["model"], local_schema, prompt
        )
        completed = subprocess.run(
            command, input=stdin, text=True, cwd=directory, capture_output=True, check=False,
        )
    completed_at = _timestamp()
    answer = None
    provider_request_id = None
    usage = None
    status = "provider_error" if completed.returncode else "malformed"
    if completed.returncode == 0:
        try:
            answer, provider_request_id, usage = parse_cli_output(assignment["adapter"], completed.stdout)
        except (json.JSONDecodeError, TypeError, ValueError):
            answer = None
        status = "valid" if answer is not None else "malformed"

    receipt = {
        "schema": "minority-prophet.lir1e-cli-receipt.v1",
        "requestId": request["requestId"],
        "attempt": attempt,
        "adapter": assignment["adapter"],
        "command": command[:-1] + (["<PROMPT>" ] if assignment["adapter"] == "claude-cli" else []),
        "stdinSha256": hashlib.sha256(prompt.encode()).hexdigest(),
        "returnCode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }
    response = {
        "schema": "minority-prophet.lir1e-response.v1",
        "requestId": request["requestId"],
        "attempt": attempt,
        "provider": assignment["provider"],
        "model": assignment["model"],
        "requestedAt": requested_at,
        "completedAt": completed_at,
        "requestParameters": config["parameters"],
        "rawResponse": json.dumps(answer, sort_keys=True) if answer is not None else None,
        "providerRequestId": provider_request_id,
        "usage": usage,
        "status": status,
    }
    return response, _canonical(receipt)


def execute(requests: list[dict], config: dict, output: Path, answer_schema: Path) -> dict[str, int]:
    output.mkdir(parents=True, exist_ok=True)
    receipts = output / "receipts"
    receipts.mkdir(exist_ok=True)
    response_path = output / "responses.jsonl"
    existing = read_jsonl(response_path) if response_path.exists() else []
    attempts_used = len(existing)
    maximum_calls = config["limits"]["maximumCalls"]
    valid_ids = {row["requestId"] for row in existing if row["status"] == "valid"}
    counts = {"valid": 0, "malformed": 0, "provider_error": 0, "skipped": 0}

    with response_path.open("ab") as handle:
        for request in requests:
            if request["requestId"] in valid_ids:
                counts["skipped"] += 1
                continue
            for attempt in (1, 2):
                if attempts_used >= maximum_calls:
                    raise RuntimeError("registered maximumCalls reached before completion")
                response, receipt = run_one(request, config, answer_schema, attempt)
                attempts_used += 1
                handle.write(_canonical(response))
                handle.flush()
                receipt_path = receipts / f"{request['requestId']}-attempt-{attempt}.json"
                receipt_path.write_bytes(receipt)
                counts[response["status"]] += 1
                print(json.dumps({
                    "attemptsUsed": attempts_used,
                    "requestId": request["requestId"],
                    "status": response["status"],
                }, sort_keys=True), flush=True)
                if response["status"] == "provider_error":
                    raise RuntimeError(
                        f"provider error on {request['requestId']}; stopping without substitution"
                    )
                if response["status"] == "valid":
                    break
    return counts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--requests", required=True, type=Path)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    requests = read_jsonl(args.requests)
    requests_sha256 = hashlib.sha256(args.requests.read_bytes()).hexdigest()
    config = load_config(args.config, len(requests), requests_sha256)
    answer_schema = Path(__file__).with_name("schema") / "answer.schema.json"
    plan = {
        "requestCount": len(requests),
        "requestsSha256": requests_sha256,
        "configSha256": hashlib.sha256(args.config.read_bytes()).hexdigest(),
        "modelSlots": sorted({row["modelSlot"] for row in requests}),
        "execute": args.execute,
    }
    print(json.dumps(plan, sort_keys=True, indent=2))
    if not args.execute:
        return
    if shutil.which("claude") is None and any(
        assignment["adapter"] == "claude-cli" for assignment in config["assignments"].values()
    ):
        raise SystemExit("claude executable is unavailable")
    if shutil.which("codex") is None and any(
        assignment["adapter"] == "codex-cli" for assignment in config["assignments"].values()
    ):
        raise SystemExit("codex executable is unavailable")
    print(json.dumps(execute(requests, config, args.output, answer_schema), sort_keys=True))


if __name__ == "__main__":
    main()
