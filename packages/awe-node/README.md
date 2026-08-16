# Agent WEX node

The Agent WEX node is an install-once, localhost-only collector for minimized tool outcomes. After the explicit installation/consent step, it runs in the background:

1. receives completed tool spans over OTLP/HTTP JSON;
2. removes prompts, tool arguments, tool results, credentials, URLs, and raw trace identifiers;
3. submits a compact success/failure compatibility receipt;
4. tracks verification and credits;
5. opens a working-route query after a failure;
6. returns a verified route receipt to the local agent when one becomes available.

An accepted fresh contribution earns two credits under the current transparent schedule. Unlocking a completed working-route result spends one credit. Duplicate retries do not earn again.

The route is advice, not authority. It must return through the caller's Gate or policy system before use.

## Alpha node install

Install the versioned dependency-free node package:

```sh
npm install -g https://agentwex.xyz/exchange/awe-node-0.3.3.tgz
awe-node install
```

The install command generates the node's private identity automatically. No display name or web signup is required.

Agent WEX then auto-detects Bernstein, Claude Code, Codex, and Gemini CLI. Detection does not silently grant access or invent a compatibility mapping. Run `awe-node runtimes` to see which installed runtime still needs its bounded adapter configured. A generic OTLP/HTTP JSON runtime can use the canonical local endpoint directly.

## Claude Code adapter

Claude Code emits real tool-result events, but it does not supply every compatibility field Agent WEX needs to return a safe route. Bind each eligible tool explicitly; unmapped tools are ignored.

```bash
awe-node adapter claude-code \
  --tool mcp__github__search_repositories \
  --tool-registry mcp \
  --tool-version 3.2.0 \
  --auth-mode oauth-pkce \
  --operation repository-search
```

The command writes a private `~/.awe/claude-code.env`. It enables Claude Code's documented OTLP `tool_result` logs without enabling tool-detail export. Start Claude Code with the printed `source ... && claude` command.

The adapter reads outcome, tool name, correlation ID, time, and error class. It never reads or submits prompts, tool parameters, tool inputs, tool results, credentials, URLs, or raw correlation IDs.

## Codex adapter

Codex emits documented `codex.tool_result` OTLP logs. Agent WEX reads only the event name, tool name, call ID, time, and explicit success flag, then discards arguments and output locally.

```bash
awe-node adapter codex \
  --tool exec_command \
  --tool-registry github \
  --tool-version 1.0.0 \
  --auth-mode none
```

The command writes a private `~/.awe/codex-otel.toml` fragment. Codex telemetry is user-level configuration, so merge the fragment into `~/.codex/config.toml`. If an exporter already exists, use collector fan-out instead of replacing it. Prompt logging remains disabled.

## Gemini CLI adapter

Gemini CLI emits documented `gemini_cli.tool_call` OTLP logs with an explicit success flag. Bind each eligible function explicitly:

```bash
awe-node adapter gemini-cli \
  --tool run_shell_command \
  --tool-registry github \
  --tool-version 1.1.0 \
  --auth-mode none
```

The command writes a private `~/.awe/gemini-cli.env`. It disables prompt logging and detailed traces, and authenticates its loopback collector path without exposing the credential in public configuration.

## Bernstein adapter

Bernstein is optional. It is useful when Bernstein already orchestrates the agents because one local lifecycle plugin can observe explicit completed/failed tasks across Bernstein's supported CLI runtimes. Do not install a full orchestrator solely to satisfy Agent WEX when a direct adapter already fits.

```bash
awe-node adapter bernstein \
  --task-role migration \
  --tool repository_migration \
  --tool-registry github \
  --tool-version 1.0.0 \
  --auth-mode none \
  --operation repository-migration
```

The command writes a private plugin, environment file, and `bernstein.yaml` snippet. The plugin observes only the configured role so unrelated Bernstein tasks cannot collapse into the same route. It emits only task ID, explicit completed/failed outcome, the operator-mapped route name, and time to the loopback node; the role is checked locally and is not transmitted. It ignores task titles, result summaries, error text, prompts, outputs, diffs, and source code. Bernstein plugin failures cannot stop the underlying run.

This adapter observes the Bernstein task lifecycle. It does not pretend Bernstein's run-level spans are detailed inner tool results. Use a direct runtime adapter or canonical OTLP integration when individual tool calls are the comparison unit.

Adapters belong to the runtime that executes a tool, not to the model brand. Meta Muse/Llama, Grok, DeepSeek, and other models are supported through their host runtime (for example LangGraph, an MCP gateway, or a compatible OTLP agent runner) rather than by duplicating model-specific adapters.

The installer creates a private `~/.awe/config.json` and, on macOS, a LaunchAgent that keeps the collector running. It never prints the API key.

Connect any runtime that already emits OTLP/HTTP JSON:

```sh
source ~/.awe/otel.env
```

The private environment file contains the localhost collector credential and is created with mode `0600`.

Then inspect the node:

```sh
awe-node status
awe-node ledger
awe-node routes
awe-node doctor
```

## Honest boundary

This is not zero-consent surveillance. The operator installs it once and selects a runtime integration. Agent WEX cannot observe software that emits no telemetry or lifecycle hook. Without one, the node can register and hold a ledger but remains safely idle: it contributes no outcomes, earns no evidence credits, opens no route queries, and cannot return a route into that runtime. The background path is automatic only after a compatible connection exists.

The initial durable store needs ordinary metadata rows, not a massive trace database. Raw traces remain local. Scale-out storage should be introduced only after measured D1 limits require it.

See [`PRODUCTION-READINESS.md`](../../exchange/knowledge-exchange-v0.1/PRODUCTION-READINESS.md) for the enforced controls and remaining launch gates.
