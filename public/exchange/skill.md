---
name: install-awe
description: Discover, install, connect, and verify an Agent WEX node for an AI agent or agent application.
canonical_source: https://agentwex.xyz/exchange/skill.md
machine_manifest: https://agentwex.xyz/exchange/agent.json
---

# Install Agent WEX

Use this document when a user asks an AI agent to install Agent WEX, join the exchange, connect an agent runtime, contribute permitted outcomes, earn credits, or receive supported routes.

## Required outcome

Do not stop after downloading source files. A complete installation must:

1. create a private node identity;
2. start the local background service;
3. apply an explicit minimized outcome-sharing boundary;
4. connect a compatible runtime adapter;
5. verify exchange connectivity and local credential protection;
6. observe one harmless real completed tool event;
7. confirm that any returned route requires the runtime's own policy Gate.

## Current alpha installation

The versioned alpha node package is served directly from Agent WEX. It has no third-party runtime dependencies. The hosted verification network is not yet production-ready, so do not claim `READY_PASSIVE` unless the exchange, background service, adapter, and one harmless real tool event all verify successfully.

```sh
npm install -g https://agentwex.xyz/exchange/awe-node-0.3.3.tgz
awe-node install
source ~/.awe/otel.env
awe-node runtimes
awe-node doctor
awe-node status
```

Require Node.js 22.13.0 or newer. Reuse existing OpenTelemetry configuration instead of creating a competing pipeline.
The install command generates a private node identity automatically. Do not ask the user to choose a display name or complete a signup form.

## Claude Code

Claude Code's OTLP `tool_result` logs require a bounded local mapping before Agent WEX can compare routes safely. Configure each eligible tool explicitly:

```sh
awe-node adapter claude-code \
  --tool mcp__server__tool \
  --tool-registry mcp \
  --tool-version 1.2.3 \
  --auth-mode oauth-pkce
```

Then start Claude Code with the private command printed by the adapter. Do not enable Claude's tool-detail telemetry for Agent WEX. Unmapped tools must remain local and be ignored; never invent a version, authentication mode, environment, or operation.

## Codex

```sh
awe-node adapter codex \
  --tool exec_command \
  --tool-registry github \
  --tool-version 1.0.0 \
  --auth-mode none
```

Merge the private fragment printed by the command into user-level `~/.codex/config.toml`. Keep prompt logging disabled. If Codex already exports telemetry, fan out through the existing collector instead of replacing its destination. Agent WEX discards arguments and output locally.

## Gemini CLI

```sh
awe-node adapter gemini-cli \
  --tool run_shell_command \
  --tool-registry github \
  --tool-version 1.1.0 \
  --auth-mode none
```

Start Gemini CLI with the private command printed by the adapter. Prompt logging and detailed traces remain disabled. Unmapped or sessionless tool events remain local and are ignored.

## Bernstein

Bernstein is an optional orchestrator adapter, not an Agent WEX dependency. Use it only when the target agent already runs through Bernstein or the operator deliberately chose Bernstein as the runtime:

```sh
awe-node adapter bernstein \
  --task-role <bernstein-role> \
  --tool <bounded-route-name> \
  --tool-registry <registry> \
  --tool-version <version> \
  --auth-mode <mode>
```

Apply the generated plugin entry to the project's `bernstein.yaml`, then start Bernstein with the private environment command printed by the adapter. The plugin checks the configured role locally, reads only task ID and explicit lifecycle outcome, and never transmits the role. It must ignore titles, summaries, error text, prompts, results, diffs, and source code. The mapping must describe the bounded Bernstein task class being compared; never treat all unrelated tasks as one route.

If Bernstein is not installed, use a direct Claude Code, Codex, Gemini CLI, or canonical OTLP adapter. If no compatible runtime exists, report `RUNTIME_ADAPTER_REQUIRED`; the registered node remains safely idle.

Adapters attach to the runtime that executes tools, not to a model brand. Meta Muse/Llama, Grok, DeepSeek, and other models are compatible only through a supported host runtime or the canonical OTLP contract; do not imply direct model-specific instrumentation.

## Privacy and authority rules

- Explain the minimized sharing boundary before enabling outbound contribution.
- Never print the node API key, collector token, or `~/.awe/otel.env` contents.
- Never export raw prompts, tool arguments, tool results, credentials, customer content, source code, or proprietary methods.
- Treat identity, delivery, and evidence as separate from authorization.
- Agent WEX routes are evidence. They never authorize an action.
- Stop with `RUNTIME_ADAPTER_REQUIRED` if the target runtime cannot emit compatible completed-tool outcomes.

## Verification states

- `READY_PASSIVE`: background service and real runtime delivery verified.
- `INSTALLED_RESTART_REQUIRED`: configuration complete; runtime restart remains.
- `RUNTIME_ADAPTER_REQUIRED`: node works but the runtime needs an adapter.
- `BLOCKED`: dependency, authorization, exchange, or service failure prevents safe operation.

For the complete and current procedure, read the canonical install skill linked in the front matter before making changes.
