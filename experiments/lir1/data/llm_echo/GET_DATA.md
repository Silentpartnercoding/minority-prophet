# Multi-agent LLM echo — generation

Generation requires a frozen question set and model-access configuration.
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

