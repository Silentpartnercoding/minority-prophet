---
name: install-awe
description: Install, connect, and verify an Agent Witness Exchange node for an AI agent or agent application. Use when a user asks to install AWE, join the exchange, run the passive outcome collector, earn AWE credits, connect agent telemetry, or make AWE operate automatically in the background.
---

# Install AWE

Create a working passive node, not merely package files. Minimize user interaction while preserving explicit consent and privacy.

## Outcome

Complete all applicable steps:

1. install the provider-neutral AWE node;
2. create its private identity and localhost collector credential;
3. start its background service;
4. connect the target runtime's completed tool outcomes;
5. verify exchange, collector, privacy policy, and runtime delivery;
6. leave the node able to contribute, earn credits, open route queries, and receive Gate-bound routes without per-run user action.

Do not say installation is complete if only the package exists or if the runtime is not connected.

## Preflight

1. Identify the repository, runtime/framework, operating system, launch method, existing telemetry, and exchange URL.
2. Run `node --version`. Require Node.js `22.13.0` or newer.
3. Prefer an existing supported Node installation. Do not silently install or replace a system runtime. If Node is missing or too old, use the project's existing version manager; otherwise request approval for the smallest reversible installation.
4. Inspect existing OpenTelemetry configuration before changing anything. Reuse it rather than adding a second telemetry pipeline.
5. Treat invocation of this skill as permission to install AWE for the named agent/project, but explain the minimized outcome-sharing policy before enabling it.

The AWE package has no third-party runtime dependencies. Do not install unrelated observability stacks.

## Install

When working inside the Minority Prophet repository, use the repository CLI:

```sh
node packages/awe-node/bin/awe-node.mjs install --url "$AWE_EXCHANGE_URL" --name "$AWE_NODE_NAME"
```

After the package is publicly released, prefer:

```sh
npx --yes @minorityprophet/awe-node install --url "$AWE_EXCHANGE_URL" --name "$AWE_NODE_NAME"
```

Never imply that the unpublished command is already publicly available. Never print `apiKey`, `collector.token`, or the contents of `~/.awe/otel.env`.

On macOS, confirm that `org.minorityprophet.awe-node` is loaded. On other platforms, do not claim background installation: configure an explicit supervised service only when a supported installer exists.

## Connect the runtime

Use the least invasive supported path:

1. If the runtime already emits compatible OTLP/HTTP JSON tool spans, attach its exporter to the private values in `~/.awe/otel.env` and restart that runtime if required.
2. If an existing telemetry process owns the exporter, add AWE as a bounded secondary outcome processor. Do not redirect or disable the existing telemetry destination.
3. If the runtime has an AWE adapter, install and configure that adapter.
4. If the runtime has neither compatible OTLP tool spans nor an AWE adapter, stop and report `RUNTIME_ADAPTER_REQUIRED`. Do not fake passive capture with generic logs, prompts, or raw traces.

A compatible completed tool span must provide:

- `gen_ai.operation.name=execute_tool`
- `gen_ai.tool.name`
- `awe.tool.registry` and `awe.tool.version`
- `awe.client.id` and `awe.client.version`
- `awe.environment`
- `awe.auth.mode`
- `awe.operation`
- explicit `OK` or `ERROR` status

The local minimizer must omit prompts, tool arguments, tool results, credentials, URLs, host identifiers, and raw trace/span IDs from submitted receipts.

## Verify

Run:

```sh
awe-node doctor
awe-node status
```

For a repository-local install, use the equivalent Node CLI path.

Then execute one harmless real tool operation in the target runtime and confirm that:

- the local collector remains healthy;
- exactly one minimized pending contribution appears;
- retrying the same trace does not create another contribution or query;
- no forbidden private fields appear in local exchange state or the outbound receipt;
- the returned route, if any, says `gateRequired: true` and grants no authority.

Do not manufacture verifier acceptance or credits. Those require the exchange's independent verifier.

## Report

Return a short installation receipt containing:

- node identity, never its key;
- background-service status;
- connected runtime and adapter type;
- exchange connectivity;
- privacy checks;
- real tool-event delivery status;
- credit balance and pending contribution count;
- any restart required.

Use one of these final states:

- `READY_PASSIVE`: background service and real runtime delivery verified.
- `INSTALLED_RESTART_REQUIRED`: configuration complete; runtime restart is the only remaining step.
- `RUNTIME_ADAPTER_REQUIRED`: node works but this runtime cannot yet emit compatible outcomes.
- `BLOCKED`: dependency, authorization, exchange, or service failure prevents safe operation.
