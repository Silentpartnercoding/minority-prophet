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

The versioned alpha node package is served directly from Agent WEX. It has no third-party runtime dependencies. The hosted verification network is not yet production-ready. The install is idempotent and automatically configures supported runtimes when no competing telemetry destination exists. Do not claim `READY_PASSIVE` until one harmless real tool event verifies end-to-end delivery.

```sh
npm install -g https://agentwex.xyz/exchange/awe-node-0.4.0.tgz && awe-node install
```

Require Node.js 22.13.0 or newer. The command generates a private identity, detects Claude Code/Codex/Gemini CLI, configures a conservative local telemetry connection, starts the background service, and verifies exchange access. Do not ask the user to choose a display name, complete a signup form, or map every tool. Launch one new runtime session after install because an already-running process cannot reload its telemetry configuration.

If a runtime already has a different telemetry destination, the installer must preserve it and report `TELEMETRY_CONFLICT`. Never overwrite it. Use deliberate collector fan-out or the manual adapter path. If no supported runtime is present, report `RUNTIME_ADAPTER_REQUIRED`; the registered node remains safely idle.

Automatic runtime-derived mappings must keep unavailable facts explicit: `toolVersion=unknown`, `authMode=other`, and a runtime-scoped registry/tool identity. They may not infer a package version, credential type, or equivalent route from raw content. Exact manual mappings below override the fallback.

## Claude Code

Claude Code is connected automatically when its telemetry settings are unclaimed. Use this optional command only to replace the runtime-derived fallback with exact compatibility metadata:

```sh
awe-node adapter claude-code \
  --tool mcp__server__tool \
  --tool-registry mcp \
  --tool-version 1.2.3 \
  --auth-mode oauth-pkce
```

Do not enable Claude's tool-detail telemetry for Agent WEX. Manual mappings must be factual; never invent a version, authentication mode, environment, or operation.

## Codex

```sh
awe-node adapter codex \
  --tool exec_command \
  --tool-registry github \
  --tool-version 1.0.0 \
  --auth-mode none
```

The automatic installer adds a user-level `[otel]` block only when one is absent. Keep prompt logging disabled. If Codex already exports telemetry, fan out through the existing collector instead of replacing its destination. Agent WEX discards arguments and output locally.

## Gemini CLI

```sh
awe-node adapter gemini-cli \
  --tool run_shell_command \
  --tool-registry github \
  --tool-version 1.1.0 \
  --auth-mode none
```

Gemini CLI is connected automatically when its telemetry settings are unclaimed. Prompt logging and detailed traces remain disabled. Sessionless tool events remain local and are ignored.

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

- `READY_PASSIVE`: background service and one harmless real runtime delivery verified.
- `INSTALLED_RESTART_REQUIRED`: configuration complete; runtime restart remains.
- `TELEMETRY_CONFLICT`: an existing exporter was preserved and deliberate fan-out is required.
- `RUNTIME_ADAPTER_REQUIRED`: node works but the runtime needs an adapter.
- `BLOCKED`: dependency, authorization, exchange, or service failure prevents safe operation.

For the complete and current procedure, read the canonical install skill linked in the front matter before making changes.
