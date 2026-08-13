# Provisioning Minority Prophet to an AI

Minority Prophet is deterministic code joined to a model through a narrow, read-only contract.

## Production shape

1. The application supplies claims, sources, provenance edges, and context to `analyze_evidence_structure`.
2. Minority Prophet deterministically returns roots, clusters, correlation warnings, evidence-unit counts, freshness information, and uncertainty signals.
3. The application gives that receipt to the model alongside the original evidence.
4. The model remains the decision-maker. The tool does not return a correct answer and has no execution authority.

The same contract can be exposed as an in-process function, local service, MCP tool, or HTTP endpoint. Transport must not change its semantics.

The local evaluation server also exposes an opt-in loopback adapter at
`POST /internal/provenance/compile` when `MP_PROVENANCE_TOKEN` is configured.
It accepts Gate's neutral `evidence-collector.request.v1` envelope. The opaque
service input is MP-owned `mp-provenance-service-input.v1`, containing the
exact evidence packet and lineage proposal. The service returns Gate's neutral
`evidence-collector.response.v1` envelope with a deterministic
`mp-provenance-receipt.v1` verification artifact. Gate therefore contains no MP
schema logic. The endpoint rejects unbound fields and any request that claims
protected-action authority. It does not call a model, browse, choose a route,
or authorize the protected action. A caller may obtain the proposal from
deterministic code or a separately controlled secondary model; the receipt
compiler applies the same validation either way.

## Benchmark shape

Condition C receives a precomputed receipt rather than letting the model decide whether to call a live tool. This guarantees every C trial receives the identical deterministic output and removes tool-choice, latency, retry, and provider tool-calling differences from the causal comparison.

The receipt input is built only from the exact bytes visible in Condition B. Hidden world labels are rejected. Conditions A and B receive no receipt. This isolates the measured difference as the value of Minority Prophet's analysis beyond raw provenance.

## Boundary

This candidate engine tests evidence structure. It does not prove source truth, validate externally supplied provenance, browse for missing evidence, recommend an answer, or authorize an action. Those capabilities require separate evaluation and controls.

The HTTP adapter is loopback-only because the server binds to `127.0.0.1`.
Production transport security, service identity, credential custody, and
network policy remain deployment responsibilities and are not configured here.
