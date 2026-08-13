# Neutral system architecture

Minority Prophet, Gate, and Border are separable components joined through
versioned contracts. None is required to adopt a particular model provider,
agent framework, runtime, or deployment vendor.

```text
Border or equivalent verifier ---- authentic evidence ----+
                                                         |
requesting agent ---- proposed action ---- Gate ----------+---- decision
                                           |
                                      request_evidence
                                           |
                                           v
                                  capability router
                                  /       |       \
                             same agent   human   program
                                           \
                                      epistemic service
                                           |
                                Minority Prophet or another
                                compatible analysis service
```

## Component boundaries

**Gate** interprets verified evidence under provider-owned policy. It may
proceed, block, request bounded evidence, or escalate. Gate needs a verifier in
a real deployment, but it does not require Minority Prophet or Border by name.

**Border** is one implementation of evidence and authority verification. A
deployment may provide another verifier implementing Gate's neutral verifier
interface. Authentication establishes who issued an artifact and what it is
bound to; it does not establish truth or evidence independence.

**Minority Prophet** analyzes evidence structure. Its receipts describe
lineage, roots, correlation, warnings, and uncertainty. They never grant action
authority and cannot become an additional assertion in Gate's evidence count.
Minority Prophet can run without Gate, and Gate can use another epistemic
service or no epistemic service.

**The evidence router** belongs to Gate because it enforces the collection
policy and dispatch boundary. It selects a configured capability—not a vendor.
Its HTTP transport uses the neutral `evidence-collector.request.v1` and
`evidence-collector.response.v1` envelopes and contains no Minority Prophet
receipt logic.

**Minority Prophet adapters** belong in this repository. The local provenance
service accepts the neutral collector envelope, validates the MP-specific
`mp-provenance-service-input.v1`, compiles an `mp-provenance-receipt.v1`, and
returns that receipt as a non-authorizing verification artifact. The same MP
semantics may also be exposed in-process or through MCP.

## Authority sequence

1. Gate's evidence request grants no authority.
2. A separately controlled authorizer permits only the exact collection
   dispatch and its least-privilege actions.
3. Returned artifacts pass their domain verifier and Gate's ordinary evidence
   assessment.
4. Only the final Gate decision may reach the protected runtime.

Transport success, a valid signature, an MP receipt, a human handoff, or a
collector registration cannot skip this sequence.

## Deployment boundary

The repository provides reference contracts and local adapters. Production
service identity, TLS, key custody, revocation, human identity, control-domain
registry protection, external-program sandboxing, and runtime authorization
remain deployment responsibilities. Passing internal tests is not independent
validation or a production claim.
