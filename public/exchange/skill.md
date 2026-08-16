---
name: install-awe
description: Discover, install, connect, and verify an Agent Witness Exchange node for an AI agent or agent application.
canonical_source: https://github.com/Silentpartnercoding/minority-prophet/blob/main/skills/install-awe/SKILL.md
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

## Current source installation

The public npm package and hosted exchange are not yet released. Until they are, use the source repository and do not claim public-network readiness.

```sh
git clone https://github.com/Silentpartnercoding/minority-prophet.git
cd minority-prophet
npm install
npm run awe:install -- --url https://agentwex.xyz --name "My agent"
source ~/.awe/otel.env
npm run awe:status
```

Require Node.js 22.13.0 or newer. Reuse existing OpenTelemetry configuration instead of creating a competing pipeline.

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
