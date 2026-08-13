# Minority Prophet engine runtime

This package exposes the deterministic, provider-neutral evidence-structure
tool separately from the research website and benchmark runner.

```sh
npm install @minority-prophet/engine
MP_ENGINE_ALLOW_INSECURE_LOCAL=1 mp-engine doctor
MP_ENGINE_ALLOW_INSECURE_LOCAL=1 mp-engine serve
```

Agent runtimes can use `mp-engine mcp` over stdio. Services can call
`POST /v1/analyze` or Gate's neutral
`POST /internal/provenance/compile` adapter. Non-loopback deployments require
an `MP_ENGINE_TOKEN` of at least 24 characters. The runtime never returns a
truth label and never grants protected-action authority.

`/healthz`, `/readyz`, and `/metrics` provide local operational visibility.
Set `MP_ENGINE_TELEMETRY_PATH` for redacted JSONL events containing hashes and
timing, not raw evidence.

This is a reference runtime. Production TLS, workload identity, token custody,
revocation, durable audit storage, and network policy remain deployment
responsibilities.
