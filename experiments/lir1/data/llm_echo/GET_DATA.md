# Multi-agent LLM echo — generation

Generation follows `experiments/lir1/llm_echo/PREREGISTRATION.md` and requires
a committed generator, sealed case inventories, and frozen model-access
configuration.
Every record must capture provider, exact model identifier, request timestamp,
system and user prompts, sampling parameters, allowed inter-agent context,
retrieval document identifiers and hashes, response, and provider receipt or
request identifier when available. Secrets stay in environment variables.

The construction cells are:

1. same model and identical retrieved context;
2. same model and disjoint retrieved sources;
3. different model families and disjoint retrieved sources; and
4. explicit answer-copy and mutated-copy controls.

No cell runs until its sources, models, question count, and budget are frozen in
a registered execution amendment.

Local private material is written only below `artifacts/lir1/llm_echo/`. The
repository receives hash-bound inventories and, after closure, a sanitized
result package. Credentials and provider receipts are never committed.
