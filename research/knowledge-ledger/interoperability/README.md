# Interoperability conformance

## Reference conformance receipt

The checked-in fixture is a local reference demonstration:

- five locations are declared;
- four are searched and one is unavailable;
- four reports descend from two evidence roots;
- no counterexample is found in the searched locations;
- the only permitted result is `not_established`.

Run:

```bash
python3 scripts/run_knowledge_transaction.py \
  research/knowledge-ledger/interoperability/reference-input.json \
  research/knowledge-ledger/interoperability/reference-receipt.json \
  research/knowledge-ledger/interoperability/REFERENCE-RENDERING.md
```

`reference-receipt.json` is an executable conformance artifact, not an
experimental finding.

[`REFERENCE-RENDERING.md`](REFERENCE-RENDERING.md) is its generated,
human-readable companion. Every sentence in it is derived from the receipt's own
values, so the two cannot drift apart. The JSON receipt remains authoritative.

It is not a milestone and must not be described as one. Two lines above, this
file states that the receipt is a conformance artifact rather than an
experimental finding; calling its rendering a milestone contradicted that in the
same document. The title **First Transmission** is reserved for a passed KL-011
cross-system transaction carrying a durable-history receipt, and **Candidate
First Transmission** for one that passed the scientific gates without that
receipt. Rendering a fixture in human language does not promote it.

## Cross-system acceptance gate

A cross-system interoperability result may be reported only when:

1. two implementations are written independently from the public schema;
2. they use different languages or runtimes and do not share evaluator code;
3. five stages exchange the transaction: discovery, collection, provenance,
   decision, and presentation;
4. paraphrases, retries, reordering, partial failure, a malicious duplicate,
   and an unavailable location are injected;
5. both implementations preserve the same roots, coverage, conclusion,
   uncertainty, and authorization boundary;
6. a clean third environment reproduces the receipts and hashes;
7. the full run manifest, prompts, code, logs, failures, and artifacts are
   committed before the result is promoted.

The visible receipt must show both cases:

- incomplete coverage -> `not_established`;
- complete coverage with no counterexample -> `absent_within_declared_scope`.

No broader absence or truth claim is permitted.
