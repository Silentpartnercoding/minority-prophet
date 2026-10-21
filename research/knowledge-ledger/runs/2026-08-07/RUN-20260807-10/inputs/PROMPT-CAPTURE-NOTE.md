# Prompt capture provenance — RUN-20260807-10

The run's prompt capture was unverified, the tenth consecutive instance in the
PROV-004..015 line.

Mid-run technical correction: the conformance profile must carry C11/C12 as
full test vectors—canonical input, expected canonical string, expected
contentDigest—because a profile without pinned vectors is self-referential in
the pre-v1.2.0 way. Applied by generating the vectors verbatim from the
registered fixtures.
The packet check itself caught this run's missing PROMPT.txt transcription
before close -- the enforcement working on its own author, again.
