# Prompt capture provenance — RUN-20260807-2

`PROMPT.txt` is an **agent transcription** from the run context. No
operator-side prompt artifact was found for this run: the search covered
`/Users/james/Development/` (depth 2) for any `*prompt*` file outside `.git`,
and the two operator-notes files named by the prompt. Nothing matched.

Per constraint `PROV-004` (RUN-20260807-1), an agent transcription
authenticates itself and nothing upstream of it. The digest below is therefore
**unverified provenance**: it fixes what this run *acted on*, not what the
operator *sent*. RUN-20260807-1's transcription differed from the operator's
authoritative bytes by 4 bytes (curly quotes normalised to straight), and the
same failure mode is possible here and undetectable from inside this session.

`run-manifest.json` carries `promptCaptureMethod: "agent-transcription"`
accordingly. If the operator holds an independently captured byte stream for
this prompt, comparing it against `PROMPT.txt` and recording the delta would
upgrade or correct this record; until then this digest must not be relied on as
evidence of what was instructed.

The v3 prompt named by RUN-20260807-1
(`sha256:4bf92221f371cf55b67112f885d4c0b2496843a0ba19acc4d403d25fd117173f`)
was stated to govern "the next run". The prompt this run actually received is a
new instruction (RUN-20260807-2, specification repair), not v3; no file with
that digest was located in the working environment, and it remains unread.

No conclusion of this run derives from the prompt text: every number is
reproducible from the committed evaluator, generator, frozen seed, and declared
bounds.
