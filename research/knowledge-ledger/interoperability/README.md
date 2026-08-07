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
  research/knowledge-ledger/interoperability/FIRST-TRANSMISSION.md
```

`reference-receipt.json` is an executable conformance artifact, not an
experimental finding.

[`FIRST-TRANSMISSION.md`](FIRST-TRANSMISSION.md) is its generated, human-readable
companion. It gives the milestone a memorable voice while preserving the same
limits and conclusion. The JSON receipt remains authoritative.

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
