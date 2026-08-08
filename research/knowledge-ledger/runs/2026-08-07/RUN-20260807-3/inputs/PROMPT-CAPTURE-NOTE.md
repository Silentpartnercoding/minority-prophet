# Prompt capture provenance — RUN-20260807-3

`PROMPT.txt` (`sha256:78157a926dea5b6fad9a1055044c283d205f6fd882364fa523a9ea5149064eee`)
is an **agent transcription** from the run context, the same capture method as
RUN-20260807-2 and subject to the same caveat: it authenticates the
transcription, not the operator's bytes, and a silent normalisation of the
kind PROV-004 documented (4 bytes, curly quotes) would be undetectable from
inside this session. No operator-side prompt artifact was found.
`run-manifest.json` carries `promptCaptureMethod: "agent-transcription"`;
the digest is unverified provenance.

No scientific number in this run derives from the prompt text. The two
repairs it instructs (R5.1, R5.2) are grounded in the independent
implementation's findings G2 and G1, which this run verified computationally
before acting (see ORIENTATION.md §3).
