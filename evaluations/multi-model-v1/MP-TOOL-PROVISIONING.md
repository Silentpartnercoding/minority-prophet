# Provisioning Minority Prophet to an AI

Minority Prophet is deterministic code joined to a model through a narrow, read-only contract.

## Production shape

1. The application supplies claims, sources, provenance edges, and context to `analyze_evidence_structure`.
2. Minority Prophet deterministically returns roots, clusters, correlation warnings, evidence-unit counts, freshness information, and uncertainty signals.
3. The application gives that receipt to the model alongside the original evidence.
4. The model remains the decision-maker. The tool does not return a correct answer and has no execution authority.

The same contract can be exposed as an in-process function, local service, MCP tool, or HTTP endpoint. Transport must not change its semantics.

## Benchmark shape

Condition C receives a precomputed receipt rather than letting the model decide whether to call a live tool. This guarantees every C trial receives the identical deterministic output and removes tool-choice, latency, retry, and provider tool-calling differences from the causal comparison.

The receipt input is built only from the exact bytes visible in Condition B. Hidden world labels are rejected. Conditions A and B receive no receipt. This isolates the measured difference as the value of Minority Prophet's analysis beyond raw provenance.

## Boundary

This candidate engine tests evidence structure. It does not prove source truth, validate externally supplied provenance, browse for missing evidence, recommend an answer, or authorize an action. Those capabilities require separate evaluation and controls.
