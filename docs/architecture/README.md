# Architecture map

Minority Prophet is easiest to understand as several bounded surfaces rather
than one monolithic system.

```text
observations / receipts
          |
          v
recorded provenance graph ---> root and dependency analysis
          |                              |
          v                              v
 preserved evidence                structured assessment
          |                              |
          +-----------> observer / policy consumer
```

The assessment is read-only. Identity systems establish who or what produced a
record; policy systems decide whether an action may proceed; world-state
verification checks what actually happened. Minority Prophet does not silently
absorb those responsibilities.

## Read in this order

1. [`SYSTEM-ARCHITECTURE.md`](../../SYSTEM-ARCHITECTURE.md) — current component
   and trust boundaries.
2. [`FOUNDATIONS.md`](../../FOUNDATIONS.md) — problem framing and mathematical
   program.
3. [`PROVENANCE-REQUIREMENTS.md`](../../PROVENANCE-REQUIREMENTS.md) — minimum
   lineage requirements.
4. [`GLOSSARY.md`](../../GLOSSARY.md) — project terminology.

## Implemented surfaces

| Path | Responsibility |
|---|---|
| [`provenance/`](../../provenance/) | Evidence graphs, schemas, roots, and ancestry |
| [`aggregation/`](../../aggregation/) | Aggregation and confidence experiments |
| [`benchmark/`](../../benchmark/) | Synthetic worlds, metrics, and CLI |
| [`formal/`](../../formal/) | Formal model, Lean proofs, and claim scope |
| [`knowledge_ledger/`](../../knowledge_ledger/) | Ledger reference structures and validation |
| [`contracts/`](../../contracts/) | Vendor-neutral evidence/authority contract drafts |
| [`evaluations/multi-model-v1/`](../../evaluations/multi-model-v1/) | Read-only MCP/HTTP engine and evaluation harness |
| [`app/`](../../app/) and [`website/`](../../website/) | Human-facing dashboard and public site |
| [`worker/`](../../worker/) | Edge/site worker code |

“Implemented” does not mean “production proven.” Each surface has its own tests,
record status, and deployment boundary.

## Adjacent systems

- **AgentWEX** can transport signed or structured execution observations and
  multi-resolution lineage. Transport does not create independence or choose a
  decision threshold.
- **[Gate](https://github.com/Silentpartnercoding/minority-prophet-gate)** can
  consume an assessment and apply policy. Evidence strength alone does not grant
  authority.
- **Border** binds identity, delegation, policy, evidence, and a proposed action.
  That is an authorization boundary, not an aggregation algorithm.
- **A strategic governor** would choose which uncertainty matters, the relevant
  independence cut, and when to stop gathering evidence. That broader control
  plane remains a proposed architecture, not a capability implied by this repo.

The decision-relative bridge is described and falsified separately in
[`research/decision-relative-independence/`](../../research/decision-relative-independence/).

## Runtime boundary

The reference engine performs deterministic graph and evidence analysis. It
does not return a truth label and must not sit in a hard real-time safety loop.
For machinery, deterministic controllers and hard safety envelopes remain on
the fast path; Minority Prophet is suitable only as a measured supervisory
input unless latency and failure-mode testing establishes a narrower use.
