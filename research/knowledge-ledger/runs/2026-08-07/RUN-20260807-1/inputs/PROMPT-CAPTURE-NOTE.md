# Prompt capture provenance

`RESEARCH-METHOD.md` requires each run manifest to record the prompt digest.
This note records **how** the accompanying `PROMPT.txt` was obtained, because the
distinction matters to anyone auditing this run.

## What was captured

`PROMPT.txt` is the operator instruction that initiated `RUN-20260807-1`,
transcribed by the executing agent from its own run context, plus the
mid-run operator message recorded separately in `PROMPT-ADDENDUM.txt`.

## The honest limitation

The agent had no filesystem access to the original prompt bytes as they were
delivered to the model runtime. It transcribed them from context. Therefore:

- `PROMPT.txt` is an **agent transcription**, not a captured byte stream;
- its SHA-256 digest authenticates *that transcription file*, and nothing more;
- it does **not** prove the operator's original bytes were identical, because
  invisible differences (trailing whitespace, line-ending convention, Unicode
  normalisation) would not survive transcription and would change the digest
  without being visible to the transcriber.

This is exactly the distinction the program itself insists on: a digest
authenticates a specific artifact, it does not establish that the artifact
faithfully represents an upstream reality. Recording the digest of a
transcription as though it were the digest of the original would be the
provenance equivalent of counting a copy as an independent root.

## What would remove the limitation

The runtime harness writing the delivered prompt bytes to disk before the agent
starts, and the agent digesting that file rather than its own transcription.
Until then this field is `transcribed`, not `captured`, in
`run-manifest.json`.

## Consequence for this run

None of `RUN-20260807-1`'s scientific conclusions depend on the prompt digest.
The KL-000 result is reproducible from the committed evaluator, generator,
frozen seed, and declared bounds, none of which are derived from the prompt
text. The prompt digest documents provenance of the *instruction*, not of the
*evidence*.
