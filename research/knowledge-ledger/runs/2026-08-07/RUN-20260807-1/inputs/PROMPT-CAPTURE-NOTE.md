# Prompt capture provenance

`RESEARCH-METHOD.md` requires each run manifest to record the prompt digest.
This note records **which bytes** were digested and how they were obtained,
because this run produced two different answers to that question and the
difference is itself a finding.

## Final state

| File | SHA-256 | Bytes | Status |
|---|---|---|---|
| `PROMPT.txt` | `729bfb70f39916e320f6bcb248febb273e4a1d832f6de9356b0e34940b2f5ccb` | 30,015 | **authoritative** |
| `PROMPT-TRANSCRIBED-SUPERSEDED.txt` | `8478639c1e90dcecd0ca12cffbf3462503124e40967fbefc3cbaecc5a693024a` | 30,011 | superseded, retained |
| `PROMPT-TRANSCRIPTION-DELTA.diff` | — | — | the exact difference |

`PROMPT.txt` now holds the operator's authoritative bytes, copied from
`RUN-20260807-1-PROMPT.txt`. The operator computed
`sha256:729bfb70…5ccb` **before this session began**, from the file the pasted
prompt was generated out of. That is an independent capture, not a copy of the
agent's transcription, so it is admissible as a check on it.

The superseded transcription is retained rather than deleted, under governing
principle 9 (preserve corrected results). Deleting it would erase the evidence
that the correction was needed.

## What went wrong, exactly

The agent's first `PROMPT.txt` was a transcription from its own run context, not
a captured byte stream. It differed from the authoritative bytes on **exactly one
line** — line 457, inside the ELI5 block — and nowhere else:

```
457c457
< > missing, the package said “we do not know.” When every declared location was   (authoritative)
> > missing, the package said "we do not know." When every declared location was   (transcribed)
```

Verified at byte level rather than accepted on assertion:

| | left quote | right quote |
|---|---|---|
| authoritative | `e2 80 9c` (U+201C) | `e2 80 9d` (U+201D) |
| transcribed | `22` (U+0022) | `22` (U+0022) |

Two curly quotation pairs were normalised to straight quotes. Each lost 2 bytes,
for a total of 4: 30,015 − 30,011 = 4. One hunk, two changed characters, no
other difference anywhere in the file.

## Why this matters more than four bytes

The superseded note filed under this same name predicted this failure mode in
the abstract — it warned that "invisible differences (trailing whitespace,
line-ending convention, **Unicode normalisation**) would not survive
transcription and would change the digest without being visible to the
transcriber." That prediction was correct, and the agent still had no way to
detect the discrepancy from inside its own context. It took an **independent
capture with an earlier timestamp** to surface it.

That is the program's own thesis applied to its own provenance:

- A digest authenticates a specific artifact. It does not establish that the
  artifact faithfully represents an upstream reality.
- The agent's transcription was internally consistent, self-digesting, and
  wrong. Self-consistency is not fidelity.
- Recording the digest of a transcription as if it were the digest of the
  original is the provenance equivalent of **counting a copy as an independent
  root** — the exact error KL-000 exists to make impossible.
- The correction did not come from re-reading the copy more carefully. It came
  from a second, causally independent capture. Agreement between the agent and
  itself would never have found it.

## Consequence for this run's conclusions

None. No KL-000 conclusion depends on the prompt digest. The KL-000 result is
reproducible from the committed evaluator, generator, frozen seed, and declared
bounds, none of which derive from the prompt text. The prompt digest documents
provenance of the **instruction**, not of the **evidence**.

The finding is recorded as constraint `PROV-004`. The generalisation — that any
agent-transcribed provenance field in this program is unverifiable from inside
the agent's own context, and needs an independent capture — is recorded in
`RESEARCH-BACKLOG-v1.json`, because it applies to every future run, not only
this one.

## What would prevent a recurrence

The runtime harness writing the delivered prompt bytes to disk before the agent
starts, and the agent digesting that file rather than its own transcription.
`run-manifest.json` therefore carries `promptCaptureMethod: "operator-file"`
for this run, and that field should read `operator-file` or `harness-capture` —
never `agent-transcription` — in any run whose prompt digest is relied upon.
