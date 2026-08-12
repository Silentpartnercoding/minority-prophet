# Claude extension v1.1 — instrumentation amendment

Frozen before the v1.1 restart: 2026-08-11 (America/Los_Angeles).

The first v1.0 execution attempt stopped after two Opus A-lane trials. Both
were recorded as failures because the stream auditor counted Claude CLI's
synthetic `StructuredOutput` response-schema transport as a forbidden tool
request. A separate non-benchmark diagnostic confirmed that Claude emits this
block even when `--tools ""` disables every built-in tool.

That is a harness classification error, not contestant tool use. The two v1.0
records remain preserved in
`data/runtime/capability-tournament-v1-claude-extension.json` and are excluded
from v1.1 rather than rewritten.

For v1.1 only:

- `StructuredOutput` is excluded from the contestant tool-event count;
- schema validation still checks the resulting structured output;
- every actual built-in tool request remains counted, retained, and forbidden
  in A;
- the generator, packets, manifest, prompts, models, lanes, hidden reference,
  scoring rule, and every substantive preregistered condition remain unchanged;
- all Claude trials restart into a new immutable runtime file.

No benchmark score was accepted or inspected before this amendment. The only
observed v1.0 outcomes were the two instrumentation failures described above.
