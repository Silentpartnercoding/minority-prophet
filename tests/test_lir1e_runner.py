import json
import tempfile
import unittest
from pathlib import Path

from experiments.lir1.llm_echo.run_models import (
    command_for,
    load_config,
    parse_cli_output,
    render_input,
)


class LIR1ERunnerTests(unittest.TestCase):
    def _config(self, status="registered", maximum_usd=5):
        return {
            "schema": "minority-prophet.lir1e-execution-config.v1",
            "status": status,
            "frozenRequestsSha256": "a" * 64,
            "assignments": {
                "model-a": {"adapter": "claude-cli", "provider": "a", "model": "a-1", "billingMode": "subscription"},
                "model-b": {"adapter": "codex-cli", "provider": "b", "model": "b-1", "billingMode": "subscription"},
            },
            "parameters": {"temperature": 0},
            "limits": {"maximumCalls": 5, "maximumUsd": maximum_usd},
        }

    def test_unregistered_or_unbudgeted_config_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(json.dumps(self._config(status="draft")))
            with self.assertRaisesRegex(ValueError, "status 'registered'"):
                load_config(path, 5)
            path.write_text(json.dumps(self._config(maximum_usd="replace-me")))
            with self.assertRaisesRegex(ValueError, "non-negative number"):
                load_config(path, 5)

    def test_config_binds_the_request_inventory(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(json.dumps(self._config()))
            self.assertEqual(load_config(path, 5, "a" * 64)["status"], "registered")
            with self.assertRaisesRegex(ValueError, "does not match"):
                load_config(path, 5, "b" * 64)

    def test_prompt_contains_only_fixed_request_material(self):
        request = {"prompt": "P", "question": "Q", "sourcePacket": "S"}
        self.assertEqual(render_input(request), "P\n\nQUESTION\nQ\n\nSOURCE PACKET\nS\n")

    def test_commands_apply_isolation_flags(self):
        schema = Path(__file__).resolve().parents[1] / "experiments/lir1/llm_echo/schema/answer.schema.json"
        claude, claude_stdin = command_for("claude-cli", "claude-x", schema, "prompt")
        codex, codex_stdin = command_for("codex-cli", "gpt-x", schema, "prompt")
        self.assertIn("--safe-mode", claude)
        self.assertIn("--no-session-persistence", claude)
        self.assertNotIn("$schema", claude[claude.index("--json-schema") + 1])
        self.assertIsNone(claude_stdin)
        self.assertIn("--ephemeral", codex)
        self.assertIn("read-only", codex)
        self.assertEqual(codex_stdin, "prompt")

    def test_parses_claude_structured_output(self):
        answer = {"answer": "sigil-a", "confidence": 1, "explanation": "source"}
        wrapper = json.dumps({"structured_output": answer, "session_id": "s", "usage": {"x": 1}})
        parsed, receipt, usage = parse_cli_output("claude-cli", wrapper)
        self.assertEqual((parsed, receipt, usage), (answer, "s", {"x": 1}))

    def test_parses_codex_final_message_and_rejects_extra_keys(self):
        answer = {"answer": "sigil-a", "confidence": 0.8, "explanation": "source"}
        events = "\n".join((
            json.dumps({"type": "thread.started", "thread_id": "t"}),
            json.dumps({"type": "item.completed", "item": {"type": "agent_message", "text": json.dumps(answer)}}),
        ))
        parsed, receipt, _ = parse_cli_output("codex-cli", events)
        self.assertEqual((parsed, receipt), (answer, "t"))
        answer["extra"] = True
        bad = json.dumps({"structured_output": answer})
        self.assertIsNone(parse_cli_output("claude-cli", bad)[0])


if __name__ == "__main__":
    unittest.main()
