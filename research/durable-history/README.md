# Epistemic support and durable history

Status: **proposed research track; no experimental result is claimed.**

## Research question

Can a knowledge system preserve the exact historical form of a qualified result
without confusing persistence with truth?

This track separates four layers that are often collapsed:

1. **Ground source** — where a claim first touches observable reality.
2. **Evidence method** — how provenance, independence, search coverage,
   counterexamples, uncertainty, and bounded conclusions are evaluated.
3. **Independent reproduction** — whether a separately implemented method
   recovers the same protected meaning and result.
4. **Durable history** — how hashes, signatures, retained copies, transparency
   logs, or public timestamps preserve which exact record existed when.

The central hypothesis is that keeping these layers explicit prevents a durable
record from being mistaken for a true claim, while still making silent historical
revision detectable.

## Candidate contribution

> Reality is the source. Evidence is our contact with it. Reproduction tests
> that contact. The ledger preserves its lineage. A public anchor can preserve
> the moment, but it proves neither the evidence nor the truth.

This formulation is a research direction, not a novelty claim. Any claim of
novelty requires a recorded primary-source literature review and comparison with
prior work in provenance, reproducible research, transparency logs, trusted
timestamping, content-addressed storage, and blockchain anchoring.

## Relationship to the knowledge ledger

The knowledge-ledger experiments determine whether a conclusion is supported.
This track begins only after a result has acquired a stable evidence package. It
tests preservation and verification; it cannot promote, repair, or strengthen an
unsupported result.

Ordinary experiments do not require a blockchain. Many qualified records may be
batched into one Merkle root and anchored periodically. Canonical milestones may
justify an independently verifiable public timestamp when cost, authority, and
privacy permit.

See [`EXPERIMENTS.md`](EXPERIMENTS.md) for the falsification program and
[`RECEIPT-SCHEMA.json`](RECEIPT-SCHEMA.json) for the proposed portable receipt.

## Claim boundary

An anchor may support only this statement:

> A commitment to these exact bytes existed no later than the recorded point in
> the referenced public history.

It does not establish that the committed statement is true, complete,
independent, safe, novel, or authorized.
