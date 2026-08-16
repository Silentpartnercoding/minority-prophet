---
name: install-awe
description: Install, connect, and verify an Agent WEX node for an AI agent or agent application. Use when a user asks to install Agent WEX, join the exchange, run the passive outcome collector, earn Agent WEX credits, connect agent telemetry, or make Agent WEX operate automatically in the background.
---

# Install Agent WEX

Create a working passive node, not merely package files. Minimize user interaction while preserving explicit consent and privacy.

## Outcome

Complete all applicable steps:

1. install the provider-neutral Agent WEX node;
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
5. Treat invocation of this skill as permission to install Agent WEX for the named agent/project, but explain the minimized outcome-sharing policy before enabling it.

The Agent WEX package has no third-party runtime dependencies. Do not install unrelated observability stacks.

## Install

When working inside the Minority Prophet repository, use the repository CLI:

```sh
node packages/awe-node/bin/awe-node.mjs install --url "${AWE_EXCHANGE_URL:-https://agentwex.xyz}"
```

For the public alpha, install the versioned package directly:

```sh
npm install -g https://agentwex.xyz/exchange/awe-node-0.4.1.tgz && awe-node install
awe-node runtimes
```

Do not substitute an unversioned package URL. Never print `apiKey`, `collector.token`, or the contents of `~/.awe/otel.env`.
The node generates its private identity automatically. Do not ask the user to supply a display name, register through a web form, or choose an identifier.

On macOS, confirm that `org.minorityprophet.awe-node` is loaded. On other platforms, do not claim background installation: configure an explicit supervised service only when a supported installer exists.

## Connect the runtime

Use the least invasive supported path:

1. Run the one-line installer. It automatically configures a detected Claude Code, Codex, or Gemini CLI runtime when there is no competing exporter.
2. If an existing telemetry process owns the exporter, add Agent WEX as a bounded secondary outcome processor. Do not redirect or disable the existing telemetry destination.
3. Use an explicit adapter mapping only when exact compatibility metadata is available or a pre-existing exporter requires deliberate fan-out.
4. If the runtime has neither compatible OTLP tool spans nor an Agent WEX adapter, stop and report `RUNTIME_ADAPTER_REQUIRED`. Do not fake passive capture with generic logs, prompts, or raw traces.

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

### Claude Code adapter

Claude Code's OTLP `tool_result` logs require a bounded local mapping before Agent WEX can compare routes safely. Configure each eligible tool explicitly:

```sh
awe-node adapter claude-code \
  --tool mcp__server__tool \
  --tool-registry mcp \
  --tool-version 1.2.3 \
  --auth-mode oauth-pkce
```

Start Claude Code using the private `source ... && claude` command printed by the adapter. Do not enable tool-detail telemetry. Unmapped tools must remain local and be ignored; never invent compatibility metadata.

### Codex adapter

Configure each eligible Codex tool explicitly:

```sh
awe-node adapter codex \
  --tool exec_command \
  --tool-registry github \
  --tool-version 1.0.0 \
  --auth-mode none
```

Merge the generated private `~/.awe/codex-otel.toml` fragment into the user-level `~/.codex/config.toml`. Do not replace an existing exporter; use collector fan-out. Keep `log_user_prompt = false`. Codex may include arguments and output in its local OTLP event; the Agent WEX adapter must discard both before receipt construction.

### Gemini CLI adapter

Configure each eligible Gemini CLI function explicitly:

```sh
awe-node adapter gemini-cli \
  --tool run_shell_command \
  --tool-registry github \
  --tool-version 1.1.0 \
  --auth-mode none
```

Start Gemini CLI using the private `source ... && gemini` command printed by the adapter. Prompt logging and detailed traces must remain disabled. The adapter must ignore unmapped or sessionless events.

### Bernstein adapter

Bernstein is optional. If it is already the orchestrator, configure a bounded task-lifecycle mapping:

```sh
awe-node adapter bernstein \
  --task-role <bernstein-role> \
  --tool <bounded-route-name> \
  --tool-registry <registry> \
  --tool-version <version> \
  --auth-mode <mode>
```

Apply the generated plugin entry to `bernstein.yaml` and launch Bernstein through the generated private environment command. The plugin must filter to the configured role locally and may send only task ID, explicit completed/failed outcome, mapped route name, and time to the loopback node. It must not transmit the role or read titles, summaries, error text, prompts, results, diffs, or source code. Do not install Bernstein merely to satisfy Agent WEX when a direct runtime adapter is available.

Model vendors are not runtime adapters. A Meta Muse/Llama, Grok, DeepSeek, or other model running inside a supported framework is covered by that framework's tool-outcome adapter. Do not claim direct support merely because its inference API is compatible.

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
