# Prompt capture provenance — RUN-20260807-7

Agent transcriptions, unverified, seventh consecutive run (PROV-004..012
line). Two inputs: PROMPT.txt (the original brief) and PROMPT-CORRECTION.txt
(the owner's mid-run correction of the brief's own causal claim -- the
brief speculated "no natural trigger"; the evidenced cause is instruction
decay, and the correction itself notes the brief carried the M24 defect).

Blemish on the record: the run-open commit (a7a3f81) contained PROMPT.txt as
an EMPTY placeholder -- the transcription was written afterwards, in the
corrections commit. The new packet-completeness test now rejects empty
required artifacts at close precisely because an empty placeholder is an
absent file wearing a filename; this run supplied the first specimen.
