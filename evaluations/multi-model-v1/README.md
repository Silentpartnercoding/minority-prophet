# Minority Prophet engine

Provider-neutral, deterministic evidence-structure analysis for agents and
services. The engine reports ancestry, independent roots, correlation warnings,
and uncertainty. It does not return a truth label and does not grant authority
to execute protected actions.

```sh
npm install @minority-prophet/engine
MP_ENGINE_ALLOW_INSECURE_LOCAL=1 mp-engine doctor
MP_ENGINE_ALLOW_INSECURE_LOCAL=1 mp-engine serve
```

Use `mp-engine-mcp` for the read-only MCP stdio surface. For authenticated HTTP,
set a random `MP_ENGINE_TOKEN` of at least 24 characters and call
`POST /v1/analyze`. The insecure-local flag is restricted to loopback listeners.

This package contains no benchmark worlds, model responses, ground-truth labels,
leaderboard results, website, or provider credentials. See `RUNTIME-README.md`
for the deployment boundary.
