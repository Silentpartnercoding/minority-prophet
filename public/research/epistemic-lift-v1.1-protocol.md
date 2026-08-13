# Minority Prophet Epistemic Lift v1.1 — frozen protocol

Status: frozen before v1.1 model execution.

## Hypotheses

- H1: exposing provenance improves truth recovery under correlated false consensus.
- H2: Minority Prophet's deterministic evidence-structure analysis improves truth recovery beyond provenance alone.

Null and adverse results were valid outcomes.

## Experimental control

The model, world, question, system prompt, response schema, sampling configuration, and B/C provenance bytes were held fixed. Only the available epistemic information changed.

- A received claims without ancestry.
- B received claims plus complete declared provenance.
- C received the exact B payload plus the deterministic MP receipt.

Condition order covered all six A/B/C permutations. Provider tools, external retrieval, files, and network access were disabled inside model calls.

## Candidate set

- 32 generated development worlds
- eight scenario families
- 24 answerable false-consensus worlds
- eight appropriate-abstention worlds
- generator seed 1,730,000
- replication unit: world

## Models

- OpenAI Codex CLI: `gpt-5.6-sol`, medium reasoning
- Anthropic Claude CLI: `sonnet`, medium effort; resolved version recorded per trial

## Response transport

V1.1 disabled provider-managed response-schema enforcement. Each invocation captured one raw final response and the versioned local parser validated it afterward. No model repaired schemas and no formatting retry occurred after a response was captured. One retry was allowed only when the provider process failed to return a response.

## Decision rule

The primary endpoint was paired C-minus-B truth recovery within each model. The candidate supported H2 only if every preregistered model achieved:

- C − B at least 0.15; and
- exact paired two-sided p below 0.05.

## Boundary

The worlds and earlier v1.0 outcomes were known before this transport-controlled replication. V1.1 could validate the complete transport and measure the development-set result, but it could not serve as an independent confirmation. Official publication requires held-out worlds and external audit.

Frozen manifest: `sha256:7bf6d393e59ce6fbc78ca41bda4f71b5a0c29dc95d2b535bb19901c345bf3943`
