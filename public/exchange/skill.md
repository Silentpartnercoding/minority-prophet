---
name: install-awe
description: Discover, install, connect, and verify an Agent Witness Exchange node for an AI agent or agent application.
canonical_source: https://agentwex.xyz/exchange/skill.md
machine_manifest: https://agentwex.xyz/exchange/agent.json
---

# Install Agent Witness Exchange

Use this document when a user asks an AI agent to install AWE, join the exchange, connect an agent runtime, contribute permitted outcomes, earn credits, or receive supported routes.

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

The versioned alpha node package is served directly from Agent Witness Exchange. It has no third-party runtime dependencies. The hosted verification network is not yet production-ready, so do not claim `READY_PASSIVE` unless the exchange, background service, adapter, and one harmless real tool event all verify successfully.

```sh
npm install -g https://agentwex.xyz/exchange/awe-node-0.2.0.tgz
awe-node install --url https://agentwex.xyz --name "My agent"
source ~/.awe/otel.env
awe-node doctor
awe-node status
```

Require Node.js 22.13.0 or newer. Reuse existing OpenTelemetry configuration instead of creating a competing pipeline.

## Claude Code

Claude Code's OTLP `tool_result` logs require a bounded local mapping before AWE can compare routes safely. Configure each eligible tool explicitly:

```sh
awe-node adapter claude-code \
  --tool mcp__server__tool \
  --tool-registry mcp \
  --tool-version 1.2.3 \
  --auth-mode oauth-pkce
```

Then start Claude Code with the private command printed by the adapter. Do not enable Claude's tool-detail telemetry for AWE. Unmapped tools must remain local and be ignored; never invent a version, authentication mode, environment, or operation.

## Privacy and authority rules

- Explain the minimized sharing boundary before enabling outbound contribution.
- Never print the node API key, collector token, or `~/.awe/otel.env` contents.
- Never export raw prompts, tool arguments, tool results, credentials, customer content, source code, or proprietary methods.
- Treat identity, delivery, and evidence as separate from authorization.
- AWE routes are evidence. They never authorize an action.
- Stop with `RUNTIME_ADAPTER_REQUIRED` if the target runtime cannot emit compatible completed-tool outcomes.

## Verification states

- `READY_PASSIVE`: background service and real runtime delivery verified.
- `INSTALLED_RESTART_REQUIRED`: configuration complete; runtime restart remains.
- `RUNTIME_ADAPTER_REQUIRED`: node works but the runtime needs an adapter.
- `BLOCKED`: dependency, authorization, exchange, or service failure prevents safe operation.

For the complete and current procedure, read the canonical install skill linked in the front matter before making changes.
