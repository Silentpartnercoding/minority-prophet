# Agent Witness Exchange node

The AWE node is an install-once, localhost-only collector for minimized tool outcomes. After the explicit installation/consent step, it runs in the background:

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
npm install -g https://agentwex.xyz/exchange/awe-node-0.2.0.tgz
awe-node install --url https://agentwex.xyz --name "First AWE node"
```

## Claude Code adapter

Claude Code emits real tool-result events, but it does not supply every compatibility field AWE needs to return a safe route. Bind each eligible tool explicitly; unmapped tools are ignored.

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

This is not zero-consent surveillance. The operator installs it once and selects a runtime integration. AWE cannot observe software that emits no telemetry. The background path is automatic only after that connection exists.

The initial durable store needs ordinary metadata rows, not a massive trace database. Raw traces remain local. Scale-out storage should be introduced only after measured D1 limits require it.

See [`PRODUCTION-READINESS.md`](../../exchange/knowledge-exchange-v0.1/PRODUCTION-READINESS.md) for the enforced controls and remaining launch gates.
